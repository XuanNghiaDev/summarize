"""
train_bilstm.py — Tiền xử lý + train BiLSTM (bắt buộc trước khi dùng model BiLSTM trên web)

Usage:
  python train_bilstm.py          # train vi + en
  python train_bilstm.py vi       # chỉ tiếng Việt
  python train_bilstm.py en       # chỉ tiếng Anh
"""
import os
import sys

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

LANGS = ["vi", "en"] if len(sys.argv) < 2 else [sys.argv[1]]
if LANGS[0] not in ("vi", "en"):
    print("Usage: python train_bilstm.py [vi|en]")
    sys.exit(1)

from preprocessing import preprocess_file
from bilstm_extractive import train as train_bilstm

INPUT = {"vi": "data/sample_vi.json", "en": "data/sample_en.json"}

for lang in LANGS:
    src = INPUT[lang]
    if not os.path.exists(src):
        print(f"[SKIP] Missing {src}")
        continue

    processed = f"data/processed_{lang}.json"
    print(f"\n=== Preprocess {lang.upper()} ===")
    preprocess_file(src, processed)

    print(f"\n=== Train BiLSTM {lang.upper()} ===")
    train_bilstm(
        processed,
        model_path=f"models/bilstm_{lang}.pt",
        epochs=10,
        batch_size=16,
    )

print("\n[OK] Done. Restart Flask (python ai_core/server.py) and chọn BiLSTM trên UI.")
