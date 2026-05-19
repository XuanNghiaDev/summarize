"""
run_pipeline.py
Chạy toàn bộ pipeline: data → train → evaluate → demo
Usage: python run_pipeline.py [vi|en|both] [--real|--sample] [--crawl]
  --real    : Dùng dữ liệu thực từ VnExpress cho tiếng Việt
  --sample  : Dùng dữ liệu mẫu
  --crawl   : Bắt buộc crawl dữ liệu mới
  Default: `vi` sẽ cố gắng dùng dataset thật nếu `data/vnexpress_dataset.json` tồn tại
"""
import sys
import os
import json
import time

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Parse arguments
LANG = sys.argv[1] if len(sys.argv) > 1 else "vi"
USE_SAMPLE = "--sample" in sys.argv
USE_REAL_DATA = "--real" in sys.argv or (LANG == "vi" and not USE_SAMPLE)
FORCE_CRAWL = "--crawl" in sys.argv
LANGS = ["vi", "en"] if LANG == "both" else [LANG]

def banner(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")

# ══════════════════════════════════════════════════════════
# BƯỚC 1: Tạo/tải data
# ══════════════════════════════════════════════════════════
INPUT_PATHS = {}
if USE_REAL_DATA:
    banner("BƯỚC 1 — Tải dữ liệu thực từ VnExpress")
    from generate_sample_data import generate
    generate(n_vi=300, n_en=300, use_real_data=True, force_crawl=FORCE_CRAWL)
    INPUT_PATHS["vi"] = "data/vnexpress_dataset.json" if os.path.exists("data/vnexpress_dataset.json") else "data/sample_vi.json"
else:
    banner("BƯỚC 1 — Tạo dữ liệu mẫu")
    from generate_sample_data import generate
    generate(n_vi=300, n_en=300, use_real_data=False)
    INPUT_PATHS["vi"] = "data/sample_vi.json"
INPUT_PATHS["en"] = "data/sample_en.json"

# ══════════════════════════════════════════════════════════════════
# BƯỚC 2: Tiền xử lý
# ══════════════════════════════════════════════════════════════════
banner("BƯỚC 2 — Tiền xử lý văn bản")
from preprocessing import preprocess_file
for lang in LANGS:
    preprocess_file(INPUT_PATHS.get(lang, f"data/sample_{lang}.json"), f"data/processed_{lang}.json")

# ══════════════════════════════════════════════════════════
# BƯỚC 3: TextRank (không cần train)
# ══════════════════════════════════════════════════════════
banner("BƯỚC 3 — TextRank demo")
from textrank import summarize
for lang in LANGS:
    with open(f"data/processed_{lang}.json", encoding="utf-8") as f:
        data = json.load(f)
    sample = data[0]
    summary, scores = summarize(sample["article_sentences"], num_sentences=3)
    print(f"\n[{lang.upper()}] Bài gốc:")
    print(" ", sample["article_raw"][:200], "...")
    print(f"\n[{lang.upper()}] TextRank tóm tắt:")
    print(" ", summary)
    print(f"\n[{lang.upper()}] Tham chiếu:")
    print(" ", sample["summary_raw"])

# ══════════════════════════════════════════════════════════
# BƯỚC 4: Train BiLSTM
# ══════════════════════════════════════════════════════════
banner("BƯỚC 4 — Train BiLSTM Extractive")
from bilstm_extractive import train as train_bilstm, load_model as load_bilstm, predict as pred_bilstm

for lang in LANGS:
    print(f"\n--- BiLSTM [{lang.upper()}] ---")
    t0 = time.time()
    train_bilstm(f"data/processed_{lang}.json",
                 model_path=f"models/bilstm_{lang}.pt",
                 epochs=10, batch_size=16)
    print(f"Train xong trong {time.time()-t0:.1f}s")

# ══════════════════════════════════════════════════════════
# BƯỚC 5: Train Seq2Seq
# ══════════════════════════════════════════════════════════
banner("BƯỚC 5 — Train Seq2Seq + Pointer-Generator")
from seq2seq_abstractive import train as train_seq2seq, load_model as load_seq2seq, predict as pred_seq2seq

for lang in LANGS:
    print(f"\n--- Seq2Seq [{lang.upper()}] ---")
    t0 = time.time()
    train_seq2seq(f"data/processed_{lang}.json",
                  model_path=f"models/seq2seq_{lang}.pt",
                  epochs=10, batch_size=16)
    print(f"Train xong trong {time.time()-t0:.1f}s")

# ══════════════════════════════════════════════════════════
# BƯỚC 6: Đánh giá so sánh
# ══════════════════════════════════════════════════════════
banner("BƯỚC 6 — Đánh giá ROUGE tất cả model")
from evaluate import run_all
all_results = {}
for lang in LANGS:
    all_results[lang] = run_all(lang)

# ══════════════════════════════════════════════════════════
# BƯỚC 7: Demo so sánh 2 model
# ══════════════════════════════════════════════════════════
banner("BƯỚC 7 — Demo so sánh trực tiếp")
for lang in LANGS:
    with open(f"data/processed_{lang}.json", encoding="utf-8") as f:
        data = json.load(f)
    sample = data[1]  # lấy bài thứ 2 cho đa dạng

    tr_sum, _ = summarize(sample["article_sentences"], num_sentences=3)

    bi_model, bi_vec = load_bilstm(f"models/bilstm_{lang}.pt")
    bi_sum = pred_bilstm(sample["article_sentences"], bi_model, bi_vec)

    s2s_model, s2s_vocab = load_seq2seq(f"models/seq2seq_{lang}.pt")
    s2s_sum = pred_seq2seq(sample["article_raw"], s2s_model, s2s_vocab)

    print(f"\n{'─'*60}")
    print(f"NGÔN NGỮ: {lang.upper()}")
    print(f"{'─'*60}")
    print(f"BÀI GỐC:\n  {sample['article_raw'][:300]}...")
    print(f"\nTHAM CHIẾU:\n  {sample['summary_raw']}")
    print(f"\nTEXTRANK:\n  {tr_sum}")
    print(f"\nBiLSTM EXTRACTIVE:\n  {bi_sum}")
    print(f"\nSEQ2SEQ ABSTRACTIVE:\n  {s2s_sum}")

banner("HOÀN THÀNH! Kiểm tra thư mục outputs/ để xem kết quả đánh giá.")
print("Các file đã tạo:")
for root, _, files in os.walk("."):
    if ".git" in root or "__pycache__" in root:
        continue
    for f in files:
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        print(f"  {path}  ({size:,} bytes)")
