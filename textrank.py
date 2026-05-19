"""
textrank.py
Extractive summarization bằng TextRank (không cần train)
"""
import re
import numpy as np

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    _USE_SKLEARN = True
except Exception:
    _USE_SKLEARN = False


def _tokenize_sentence(sentence: str) -> list[str]:
    return re.findall(r"\b[\w']+\b", sentence.lower())


def _build_tfidf_matrix(sentences: list[str]) -> np.ndarray:
    if _USE_SKLEARN:
        vectorizer = TfidfVectorizer()
        try:
            tfidf = vectorizer.fit_transform(sentences)
            return tfidf.toarray()
        except ValueError:
            return np.zeros((len(sentences), 0), dtype=float)

    docs = [_tokenize_sentence(s) for s in sentences]
    vocab = {}
    for doc in docs:
        for token in doc:
            if token not in vocab:
                vocab[token] = len(vocab)

    if len(vocab) == 0:
        return np.zeros((len(sentences), 0), dtype=float)

    tf = np.zeros((len(docs), len(vocab)), dtype=float)
    df = np.zeros(len(vocab), dtype=float)
    for i, doc in enumerate(docs):
        for token in doc:
            tf[i, vocab[token]] += 1
        for token in set(doc):
            df[vocab[token]] += 1

    tf = tf / np.maximum(tf.sum(axis=1, keepdims=True), 1)
    idf = np.log((1 + len(docs)) / (1 + df)) + 1
    return tf * idf


def _cosine_similarity(matrix: np.ndarray) -> np.ndarray:
    if _USE_SKLEARN:
        return cosine_similarity(matrix)
    norm = np.linalg.norm(matrix, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    sim = matrix @ matrix.T
    sim = sim / (norm @ norm.T)
    return sim


def build_similarity_matrix(sentences: list[str]) -> np.ndarray:
    """Tính ma trận cosine similarity NxN giữa các câu."""
    if not sentences:
        return np.zeros((0, 0), dtype=float)

    tfidf = _build_tfidf_matrix(sentences)
    if tfidf.size == 0:
        return np.zeros((len(sentences), len(sentences)), dtype=float)

    sim = _cosine_similarity(tfidf)
    np.fill_diagonal(sim, 0)
    return sim


def pagerank(sim_matrix: np.ndarray, d: float = 0.85,
             max_iter: int = 100, tol: float = 1e-6) -> np.ndarray:
    """PageRank trên đồ thị câu."""
    N = len(sim_matrix)
    scores = np.ones(N) / N

    row_sums = sim_matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    norm = sim_matrix / row_sums

    for _ in range(max_iter):
        new_scores = (1 - d) + d * norm.T @ scores
        if np.abs(new_scores - scores).sum() < tol:
            break
        scores = new_scores

    return scores


def summarize(sentences: list[str], num_sentences: int = 3) -> tuple[str, np.ndarray]:
    """
    Input:  danh sách câu gốc
    Output: (tóm tắt, mảng score mỗi câu)
    """
    if len(sentences) <= num_sentences:
        return " ".join(sentences), np.ones(len(sentences))

    sim_matrix = build_similarity_matrix(sentences)
    scores = pagerank(sim_matrix)

    # Giữ thứ tự câu gốc (không sort theo score)
    top_idx = sorted(np.argsort(scores)[-num_sentences:].tolist())
    summary = " ".join(sentences[i] for i in top_idx)
    return summary, scores


# ── CLI nhanh ──────────────────────────────────────────────
if __name__ == "__main__":
    import json, sys

    path = sys.argv[1] if len(sys.argv) > 1 else "data/processed_vi.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    sample = data[0]
    print("=== VĂN BẢN GỐC ===")
    print(sample["article_raw"][:400], "...\n")

    summary, scores = summarize(sample["article_sentences"], num_sentences=3)
    print("=== TÓM TẮT (TextRank) ===")
    print(summary)
    print("\n=== TÓM TẮT THAM CHIẾU ===")
    print(sample["summary_raw"])
    print("\n=== SCORES TỪNG CÂU ===")
    for i, (s, sc) in enumerate(zip(sample["article_sentences"], scores)):
        print(f"  [{sc:.3f}] {s[:60]}...")
