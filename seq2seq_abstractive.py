"""
seq2seq_abstractive.py
Abstractive summarization: Seq2Seq LSTM + Attention + Pointer-Generator
Xây dựng từ đầu với PyTorch
"""
import json, re
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from collections import Counter

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
PAD, UNK, SOS, EOS = "<PAD>", "<UNK>", "<SOS>", "<EOS>"


# ══════════════════════════════════════════════════════════
# 1. Vocabulary
# ══════════════════════════════════════════════════════════

class Vocabulary:
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.word2idx = {PAD: 0, UNK: 1, SOS: 2, EOS: 3}
        self.idx2word = {0: PAD, 1: UNK, 2: SOS, 3: EOS}

    def build(self, texts: list[str]):
        counter = Counter()
        for t in texts:
            counter.update(t.lower().split())
        for word, _ in counter.most_common(self.max_size - 4):
            idx = len(self.word2idx)
            self.word2idx[word] = idx
            self.idx2word[idx] = word

    def encode(self, text: str, max_len: int = 200) -> list[int]:
        tokens = text.lower().split()[:max_len]
        return [self.word2idx.get(t, 1) for t in tokens]

    def decode(self, indices: list[int]) -> str:
        words = []
        for i in indices:
            w = self.idx2word.get(i, UNK)
            if w == EOS:
                break
            if w not in (PAD, SOS):
                words.append(w)
        return " ".join(words)

    def __len__(self):
        return len(self.word2idx)


# ══════════════════════════════════════════════════════════
# 2. Dataset
# ══════════════════════════════════════════════════════════

class Seq2SeqDataset(Dataset):
    def __init__(self, data: list[dict], vocab: Vocabulary,
                 src_max: int = 200, tgt_max: int = 60):
        self.samples = []
        for item in data:
            src = vocab.encode(item["article_raw"], src_max)
            tgt = [vocab.word2idx[SOS]] + \
                  vocab.encode(item["summary_raw"], tgt_max - 2) + \
                  [vocab.word2idx[EOS]]
            self.samples.append((src, tgt))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def collate_seq2seq(batch, pad_idx=0):
    srcs, tgts = zip(*batch)
    src_len = max(len(s) for s in srcs)
    tgt_len = max(len(t) for t in tgts)
    src_pad = torch.tensor([s + [pad_idx]*(src_len-len(s)) for s in srcs])
    tgt_pad = torch.tensor([t + [pad_idx]*(tgt_len-len(t)) for t in tgts])
    return src_pad, tgt_pad


# ══════════════════════════════════════════════════════════
# 3. Encoder
# ══════════════════════════════════════════════════════════

class Encoder(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers, dropout):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers,
                            batch_first=True, bidirectional=True,
                            dropout=dropout if num_layers > 1 else 0.0)
        self.proj_h = nn.Linear(hidden_dim * 2, hidden_dim)
        self.proj_c = nn.Linear(hidden_dim * 2, hidden_dim)
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim

    def forward(self, src):
        embedded = self.embed(src)
        outputs, (h, c) = self.lstm(embedded)
        # outputs: (B, T, 2H), h/c: (2*layers, B, H)
        # Ghép forward + backward để init decoder
        h = torch.tanh(self.proj_h(
            torch.cat([h[-2], h[-1]], dim=1)
        )).unsqueeze(0).repeat(self.num_layers, 1, 1)
        c = torch.tanh(self.proj_c(
            torch.cat([c[-2], c[-1]], dim=1)
        )).unsqueeze(0).repeat(self.num_layers, 1, 1)
        return outputs, (h, c)


# ══════════════════════════════════════════════════════════
# 4. Attention
# ══════════════════════════════════════════════════════════

class BahdanauAttention(nn.Module):
    def __init__(self, enc_dim, dec_dim):
        super().__init__()
        self.W_enc = nn.Linear(enc_dim, dec_dim, bias=False)
        self.W_dec = nn.Linear(dec_dim, dec_dim, bias=False)
        self.v = nn.Linear(dec_dim, 1, bias=False)

    def forward(self, enc_out, dec_hidden):
        # enc_out: (B, T, 2H_enc), dec_hidden: (B, H_dec)
        energy = torch.tanh(
            self.W_enc(enc_out) + self.W_dec(dec_hidden).unsqueeze(1)
        )                                    # (B, T, H_dec)
        attn = F.softmax(self.v(energy).squeeze(-1), dim=1)  # (B, T)
        context = (attn.unsqueeze(-1) * enc_out).sum(dim=1)  # (B, 2H_enc)
        return context, attn


# ══════════════════════════════════════════════════════════
# 5. Decoder với Pointer-Generator
# ══════════════════════════════════════════════════════════

class PointerGeneratorDecoder(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, enc_dim, num_layers, dropout):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.attention = BahdanauAttention(enc_dim, hidden_dim)
        self.lstm = nn.LSTM(embed_dim + enc_dim, hidden_dim, num_layers,
                            batch_first=True,
                            dropout=dropout if num_layers > 1 else 0.0)
        self.out_proj = nn.Linear(hidden_dim + enc_dim + embed_dim, vocab_size)
        # Pointer gate: p_gen ∈ [0,1]
        self.p_gen_linear = nn.Linear(enc_dim + hidden_dim + embed_dim, 1)
        self.dropout = nn.Dropout(dropout)

    def forward_step(self, token, hidden, enc_out):
        emb = self.embed(token.unsqueeze(1))          # (B, 1, E)
        dec_h = hidden[0][-1]                         # (B, H)
        context, attn = self.attention(enc_out, dec_h)# (B, 2H), (B, T)

        lstm_in = torch.cat([emb, context.unsqueeze(1)], dim=-1)  # (B,1,E+2H)
        out, hidden = self.lstm(lstm_in, hidden)      # (B,1,H)

        out_cat = torch.cat([out.squeeze(1), context, emb.squeeze(1)], dim=-1)
        vocab_dist = F.softmax(self.out_proj(self.dropout(out_cat)), dim=-1)

        # Pointer gate
        p_gen = torch.sigmoid(self.p_gen_linear(out_cat))  # (B, 1)

        return vocab_dist, attn, p_gen, hidden

    def forward(self, tgt, enc_out, hidden, src_ids=None, teacher_forcing=0.5):
        B, T = tgt.shape
        vocab_size = self.out_proj.out_features
        outputs = torch.zeros(B, T, vocab_size).to(tgt.device)

        token = tgt[:, 0]
        for t in range(1, T):
            vocab_dist, attn, p_gen, hidden = self.forward_step(
                token, hidden, enc_out)

            # Pointer-Generator: trộn vocab dist + copy dist
            if src_ids is not None:
                final_dist = p_gen * vocab_dist
                copy_dist = torch.zeros_like(vocab_dist)
                copy_dist.scatter_add_(1, src_ids,
                                       (1 - p_gen) * attn)
                final_dist = final_dist + copy_dist
            else:
                final_dist = vocab_dist

            outputs[:, t] = final_dist

            # Teacher forcing
            use_tf = (torch.rand(1).item() < teacher_forcing)
            token = tgt[:, t] if use_tf else final_dist.argmax(dim=-1)

        return outputs


# ══════════════════════════════════════════════════════════
# 6. Seq2Seq model tổng hợp
# ══════════════════════════════════════════════════════════

class Seq2SeqPG(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=256,
                 num_layers=2, dropout=0.3):
        super().__init__()
        self.encoder = Encoder(vocab_size, embed_dim, hidden_dim,
                               num_layers, dropout)
        self.decoder = PointerGeneratorDecoder(
            vocab_size, embed_dim,
            hidden_dim, hidden_dim * 2,   # enc_dim = 2H (bidirectional)
            num_layers, dropout)

    def forward(self, src, tgt, teacher_forcing=0.5):
        enc_out, hidden = self.encoder(src)
        output = self.decoder(tgt, enc_out, hidden,
                              src_ids=src,
                              teacher_forcing=teacher_forcing)
        return output


# ══════════════════════════════════════════════════════════
# 7. Train
# ══════════════════════════════════════════════════════════

def train(data_path: str, model_path: str = "models/seq2seq.pt",
          epochs: int = 10, batch_size: int = 16, lr: float = 5e-4):

    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    # Build vocab
    vocab = Vocabulary(max_size=8000)
    all_texts = [d["article_raw"] + " " + d["summary_raw"] for d in data]
    vocab.build(all_texts)
    print(f"[INFO] Vocab size: {len(vocab)}")

    split = int(len(data) * 0.8)
    train_ds = Seq2SeqDataset(data[:split], vocab)
    val_ds   = Seq2SeqDataset(data[split:], vocab)
    train_dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                          collate_fn=collate_seq2seq)
    val_dl   = DataLoader(val_ds, batch_size=batch_size,
                          collate_fn=collate_seq2seq)

    model = Seq2SeqPG(vocab_size=len(vocab)).to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss(ignore_index=0)

    print(f"[INFO] Device: {DEVICE}")
    print(f"[INFO] Params: {sum(p.numel() for p in model.parameters()):,}\n")

    best_val = float("inf")
    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        train_loss = 0.0
        for src, tgt in train_dl:
            src, tgt = src.to(DEVICE), tgt.to(DEVICE)
            optimizer.zero_grad()
            out = model(src, tgt, teacher_forcing=0.5)
            # out: (B, T, V), tgt: (B, T)
            out_flat = out[:, 1:].reshape(-1, len(vocab))
            tgt_flat = tgt[:, 1:].reshape(-1)
            loss = criterion(out_flat, tgt_flat)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item()

        # Val
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for src, tgt in val_dl:
                src, tgt = src.to(DEVICE), tgt.to(DEVICE)
                out = model(src, tgt, teacher_forcing=0.0)
                out_flat = out[:, 1:].reshape(-1, len(vocab))
                tgt_flat = tgt[:, 1:].reshape(-1)
                val_loss += criterion(out_flat, tgt_flat).item()

        tl = train_loss / len(train_dl)
        vl = val_loss / len(val_dl)
        print(f"Epoch {epoch:2d}/{epochs}  train={tl:.4f}  val={vl:.4f}")

        if vl < best_val:
            best_val = vl
            torch.save({"model_state": model.state_dict(),
                        "vocab": vocab}, model_path)
            print(f"           → saved")

    print(f"\n[OK] Model lưu tại {model_path}")
    return model, vocab


# ══════════════════════════════════════════════════════════
# 8. Inference (greedy decode)
# ══════════════════════════════════════════════════════════

def load_model(model_path: str):
    ckpt = torch.load(model_path, map_location=DEVICE, weights_only=False)
    vocab = ckpt["vocab"]
    model = Seq2SeqPG(vocab_size=len(vocab)).to(DEVICE)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model, vocab


def predict(text: str, model: Seq2SeqPG, vocab: Vocabulary,
            max_len: int = 80) -> str:
    src_ids = vocab.encode(text, max_len=200)
    src = torch.tensor([src_ids]).to(DEVICE)

    with torch.no_grad():
        enc_out, hidden = model.encoder(src)

    token = torch.tensor([vocab.word2idx[SOS]]).to(DEVICE)
    result = []

    for _ in range(max_len):
        with torch.no_grad():
            vocab_dist, _, _, hidden = model.decoder.forward_step(
                token, hidden, enc_out)
        token = vocab_dist.argmax(dim=-1)
        word = vocab.idx2word.get(token.item(), UNK)
        if word == EOS:
            break
        if word not in (PAD, SOS, UNK):
            result.append(word)

    return " ".join(result)


# ── CLI ───────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "train"

    if mode == "train":
        lang = sys.argv[2] if len(sys.argv) > 2 else "vi"
        train(f"data/processed_{lang}.json",
              model_path=f"models/seq2seq_{lang}.pt",
              epochs=10)
    elif mode == "predict":
        lang = sys.argv[2] if len(sys.argv) > 2 else "vi"
        model, vocab = load_model(f"models/seq2seq_{lang}.pt")
        with open(f"data/processed_{lang}.json", encoding="utf-8") as f:
            data = json.load(f)
        sample = data[0]
        result = predict(sample["article_raw"], model, vocab)
        print("=== Seq2Seq Summary ===")
        print(result)
        print("\n=== Reference ===")
        print(sample["summary_raw"])
