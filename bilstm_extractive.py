"""
bilstm_extractive.py
Extractive summarization bằng BiLSTM + Attention
Train từ đầu, không dùng pretrained weights
"""
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.feature_extraction.text import TfidfVectorizer

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ══════════════════════════════════════════════════════════
# 1. Tạo nhãn cho từng câu (oracle labels)
# ══════════════════════════════════════════════════════════

def sentence_rouge1_overlap(sentence: str, summary: str) -> float:
    """Tỉ lệ từ của câu xuất hiện trong summary → dùng làm nhãn."""
    s_words = set(sentence.lower().split())
    r_words = set(summary.lower().split())
    if not s_words:
        return 0.0
    return len(s_words & r_words) / len(s_words)


def make_labels(sentences: list[str], summary: str,
                top_k: int = 3) -> list[int]:
    """
    Gán nhãn 1 cho top_k câu có overlap cao nhất với summary.
    """
    scores = [sentence_rouge1_overlap(s, summary) for s in sentences]
    threshold_idx = sorted(range(len(scores)),
                           key=lambda i: scores[i], reverse=True)[:top_k]
    return [1 if i in threshold_idx else 0 for i in range(len(sentences))]


# ══════════════════════════════════════════════════════════
# 2. Dataset
# ══════════════════════════════════════════════════════════

class SentenceDataset(Dataset):
    def __init__(self, data: list[dict], vectorizer: TfidfVectorizer,
                 max_sents: int = 30):
        self.samples = []
        self.max_sents = max_sents

        for item in data:
            sents = item["article_sentences"][:max_sents]
            summary = item["summary_raw"]
            labels = make_labels(sents, summary, top_k=3)

            # Vectorize mỗi câu
            try:
                vecs = vectorizer.transform(sents).toarray().astype(np.float32)
            except Exception:
                continue

            # Pad / truncate
            feat_dim = vecs.shape[1]
            if len(sents) < max_sents:
                pad = np.zeros((max_sents - len(sents), feat_dim), dtype=np.float32)
                vecs = np.vstack([vecs, pad])
                labels += [0] * (max_sents - len(sents))

            mask = [1] * min(len(sents), max_sents) + \
                   [0] * max(0, max_sents - len(sents))

            self.samples.append({
                "features": torch.tensor(vecs),           # (max_sents, feat_dim)
                "labels":   torch.tensor(labels[:max_sents], dtype=torch.float),
                "mask":     torch.tensor(mask[:max_sents], dtype=torch.bool),
                "sentences": sents,
                "summary":   summary,
            })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


# ══════════════════════════════════════════════════════════
# 3. Model BiLSTM + Attention
# ══════════════════════════════════════════════════════════

class BiLSTMSummarizer(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 128,
                 num_layers: int = 2, dropout: float = 0.3):
        super().__init__()
        self.bilstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        # Attention
        self.attn = nn.Linear(hidden_dim * 2, 1)
        # Classifier
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x, mask=None):
        # x: (B, T, D)
        out, _ = self.bilstm(x)               # (B, T, 2H)
        attn_w = self.attn(out).squeeze(-1)   # (B, T)
        if mask is not None:
            attn_w = attn_w.masked_fill(~mask, -1e9)
        attn_w = torch.softmax(attn_w, dim=-1).unsqueeze(-1)  # (B, T, 1)
        context = (attn_w * out).sum(dim=1, keepdim=True)     # (B, 1, 2H)
        enhanced = out + context                               # (B, T, 2H)
        scores = self.classifier(enhanced).squeeze(-1)        # (B, T)
        return scores


# ══════════════════════════════════════════════════════════
# 4. Train
# ══════════════════════════════════════════════════════════

def collate_fn(batch):
    return {
        "features": torch.stack([b["features"] for b in batch]),
        "labels":   torch.stack([b["labels"]   for b in batch]),
        "mask":     torch.stack([b["mask"]     for b in batch]),
    }


def train(data_path: str, model_path: str = "models/bilstm.pt",
          epochs: int = 10, batch_size: int = 16, lr: float = 1e-3):

    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    # Fit TF-IDF trên toàn bộ corpus
    all_sents = [s for item in data for s in item["article_sentences"]]
    vectorizer = TfidfVectorizer(max_features=500)
    vectorizer.fit(all_sents)
    input_dim = len(vectorizer.get_feature_names_out())

    # Split train/val
    split = int(len(data) * 0.8)
    train_ds = SentenceDataset(data[:split], vectorizer)
    val_ds   = SentenceDataset(data[split:], vectorizer)

    train_dl = DataLoader(train_ds, batch_size=batch_size,
                          shuffle=True, collate_fn=collate_fn)
    val_dl   = DataLoader(val_ds, batch_size=batch_size,
                          collate_fn=collate_fn)

    model = BiLSTMSummarizer(input_dim=input_dim).to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()

    print(f"[INFO] Device: {DEVICE}")
    print(f"[INFO] Train: {len(train_ds)} | Val: {len(val_ds)} | Features: {input_dim}")
    print(f"[INFO] Params: {sum(p.numel() for p in model.parameters()):,}\n")

    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        # ── Train ──
        model.train()
        train_loss = 0.0
        for batch in train_dl:
            feats  = batch["features"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)
            mask   = batch["mask"].to(DEVICE)

            optimizer.zero_grad()
            preds = model(feats, mask)

            # Chỉ tính loss trên câu thật (không phải padding)
            loss = criterion(preds[mask], labels[mask])
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item()

        # ── Validation ──
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_dl:
                feats  = batch["features"].to(DEVICE)
                labels = batch["labels"].to(DEVICE)
                mask   = batch["mask"].to(DEVICE)
                preds  = model(feats, mask)
                val_loss += criterion(preds[mask], labels[mask]).item()

        tl = train_loss / len(train_dl)
        vl = val_loss / len(val_dl)
        print(f"Epoch {epoch:2d}/{epochs}  train_loss={tl:.4f}  val_loss={vl:.4f}")

        if vl < best_val_loss:
            best_val_loss = vl
            torch.save({"model_state": model.state_dict(),
                        "input_dim": input_dim,
                        "vectorizer": vectorizer}, model_path)
            print(f"           → saved (val_loss={vl:.4f})")

    print(f"\n[OK] Model lưu tại {model_path}")
    return model, vectorizer


# ══════════════════════════════════════════════════════════
# 5. Inference
# ══════════════════════════════════════════════════════════

def load_model(model_path: str):
    ckpt = torch.load(model_path, map_location=DEVICE, weights_only=False)
    model = BiLSTMSummarizer(input_dim=ckpt["input_dim"]).to(DEVICE)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model, ckpt["vectorizer"]


def predict(sentences: list[str], model: BiLSTMSummarizer,
            vectorizer: TfidfVectorizer, num_sentences: int = 3) -> str:
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    vecs = vectorizer.transform(sentences).toarray().astype(np.float32)
    x = torch.tensor(vecs).unsqueeze(0).to(DEVICE)   # (1, T, D)
    mask = torch.ones(1, len(sentences), dtype=torch.bool).to(DEVICE)

    with torch.no_grad():
        scores = model(x, mask).squeeze(0).cpu().numpy()

    top_idx = sorted(np.argsort(scores)[-num_sentences:].tolist())
    return " ".join(sentences[i] for i in top_idx)


# ── CLI ───────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "train"

    if mode == "train":
        lang = sys.argv[2] if len(sys.argv) > 2 else "vi"
        train(f"data/processed_{lang}.json",
              model_path=f"models/bilstm_{lang}.pt",
              epochs=10)
    elif mode == "predict":
        lang = sys.argv[2] if len(sys.argv) > 2 else "vi"
        model, vec = load_model(f"models/bilstm_{lang}.pt")
        with open(f"data/processed_{lang}.json", encoding="utf-8") as f:
            data = json.load(f)
        sample = data[0]
        result = predict(sample["article_sentences"], model, vec)
        print("=== BiLSTM Summary ===")
        print(result)
        print("\n=== Reference ===")
        print(sample["summary_raw"])
