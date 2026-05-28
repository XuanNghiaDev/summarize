"""
preprocessing.py
Tiền xử lý văn bản cho cả tiếng Việt và tiếng Anh
"""
import re
import json

# ── Stopwords ──────────────────────────────────────────────
STOPWORDS_VI = {
    "và","của","các","là","được","trong","có","với","để","cho",
    "này","những","đã","không","một","về","từ","theo","tại","khi",
    "như","bị","rằng","sẽ","mà","hay","hoặc","cũng","đây","đó",
    "thì","lại","rất","cần","nên","phải","có thể","hơn","nhưng",
    "vì","do","sau","trước","đến","qua","lên","xuống","ra","vào"
}

STOPWORDS_EN = {
    "the","a","an","is","are","was","were","be","been","being",
    "have","has","had","do","does","did","will","would","could",
    "should","may","might","shall","can","need","dare","ought",
    "used","to","of","in","on","at","by","for","with","about",
    "against","between","into","through","during","before","after",
    "above","below","from","up","down","out","off","over","under",
    "again","further","then","once","that","this","these","those",
    "it","its","itself","they","them","their","he","she","we","i",
    "me","my","you","your","his","her","our","which","who","whom"
}

# ── Làm sạch ──────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

# ── Tách câu ──────────────────────────────────────────────
def split_sentences_vi(text: str):
    text = clean_text(text)
    sents = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sents if len(s.strip()) > 15]

def split_sentences_en(text: str):
    text = clean_text(text)
    # Tránh tách sai tại viết tắt đơn giản
    text = re.sub(r'\b(Mr|Mrs|Dr|Prof|Sr|Jr|vs|etc)\.\s', r'\1<POINT> ', text)
    sents = re.split(r'(?<=[.!?])\s+', text)
    return [s.replace('<POINT>', '.').strip() for s in sents if len(s.strip()) > 15]

# ── Tokenize ──────────────────────────────────────────────
def tokenize_vi(sentence: str):
    tokens = sentence.lower().split()
    return [t for t in tokens if t not in STOPWORDS_VI and len(t) > 1]

def tokenize_en(sentence: str):
    tokens = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
    return [t for t in tokens if t not in STOPWORDS_EN and len(t) > 2]

# ── Pipeline chính ────────────────────────────────────────
def preprocess_item(item: dict) -> dict:
    lang = item.get("lang", "vi")
    article = item["article"]
    summary = item["summary"]

    if lang == "vi":
        sents = split_sentences_vi(article)
        tokens = [tokenize_vi(s) for s in sents]
        sum_sents = split_sentences_vi(summary)
    else:
        sents = split_sentences_en(article)
        tokens = [tokenize_en(s) for s in sents]
        sum_sents = split_sentences_en(summary)

    return {
        "id": item.get("id", ""),
        "lang": lang,
        "article_raw": article,
        "summary_raw": summary,
        "article_sentences": sents,
        "article_tokens": tokens,
        "summary_sentences": sum_sents,
        "num_sentences": len(sents),
    }

def preprocess_file(input_path: str, output_path: str):
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    processed, skipped = [], 0
    for item in data:
        p = preprocess_item(item)
        if p["num_sentences"] >= 3:
            processed.append(p)
        else:
            skipped += 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    msg = f"[OK] {output_path}: {len(processed)} bai (bo {skipped} bai qua ngan)"
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))
    return processed

if __name__ == "__main__":
    preprocess_file("data/sample_vi.json", "data/processed_vi.json")
    preprocess_file("data/sample_en.json", "data/processed_en.json")
