"""
demo.py  —  Chạy file này để xem đầu vào / đầu ra
Usage: python demo.py
"""
import sys, os, json
os.makedirs("models", exist_ok=True)
os.makedirs("data",   exist_ok=True)

# ─── Văn bản bạn muốn tóm tắt (thay nội dung này bằng bài của bạn) ───────────
VAN_BAN = """
Transformer architectures have gained a lot of attention in the field of Natural Language Processing. Ever since the original Transformer architecture was released in 2017, they have achieved state-of-the-art results on a variety of language tasks.

Another task was added to which Transformers can be applied last year. In this tutorial, we will take a look at Speech Recognition. We will take a look at the Wav2vec2 model which is specifically tailored to Speech Recognition tasks. We will show you how it can be used to pretrain and then finetune a model to the task of Speech-to-text recognition. This also includes an example implementation of a pipeline created with HuggingFace Transformers. Using the pipeline, you'll be able to apply Speech Recognition to your Machine Learning driven project very easily.

After reading this tutorial, you will be able to...

Understand how Transformer-based architectures can be applied to Speech Recognition.
Explain how the Wav2vec2 architecture works at a high level, and refer to a summary of the paper.
Build a Wav2vec2-powered Machine Learning pipeline with HuggingFace Transformers and Python.
"""

SO_CAU_TOM_TAT = 2   # ← thay số này nếu muốn tóm tắt dài/ngắn hơn
# ─────────────────────────────────────────────────────────────────────────────


def sep(title=""):
    w = 60
    if title:
        print(f"\n{'─'*3} {title} {'─'*(w-5-len(title))}")
    else:
        print("─" * w)


# ══ Tách câu đơn giản (không cần thư viện ngoài) ═════════════════════════════
import re

def tach_cau(text):
    text = re.sub(r'\s+', ' ', text).strip()
    caus = re.split(r'(?<=[.!?])\s+', text)
    return [c.strip() for c in caus if len(c.strip()) > 10]


# ══ TextRank ══════════════════════════════════════════════════════════════════
def tom_tat_textrank(cac_cau, n=2):
    from textrank import summarize
    ket_qua, scores = summarize(cac_cau, num_sentences=n)
    return ket_qua, scores


# ══ BiLSTM (nếu đã train) ════════════════════════════════════════════════════
def tom_tat_bilstm(cac_cau, n=2):
    path = "models/bilstm_vi.pt"
    if not os.path.exists(path):
        return None
    from bilstm_extractive import load_model, predict
    model, vec = load_model(path)
    return predict(cac_cau, model, vec, num_sentences=n)


# ══ Seq2Seq (nếu đã train) ═══════════════════════════════════════════════════
def tom_tat_seq2seq(van_ban):
    path = "models/seq2seq_vi.pt"
    if not os.path.exists(path):
        return None
    from seq2seq_abstractive import load_model, predict
    model, vocab = load_model(path)
    return predict(van_ban, model, vocab)


# ══ MAIN ══════════════════════════════════════════════════════════════════════
def main():
    cac_cau = tach_cau(VAN_BAN)

    sep("ĐẦU VÀO (văn bản gốc)")
    print(VAN_BAN.strip())
    print(f"\n→ Tổng số câu: {len(cac_cau)}")
    print(f"→ Tổng số từ : {len(VAN_BAN.split())}")

    sep("ĐẦU RA — TextRank  (không cần train)")
    tr, scores = tom_tat_textrank(cac_cau, SO_CAU_TOM_TAT)
    print(tr)
    print(f"\nScore từng câu:")
    for i, (c, s) in enumerate(zip(cac_cau, scores)):
        mark = " ◄ được chọn" if s in sorted(scores)[-SO_CAU_TOM_TAT:] else ""
        print(f"  [{s:.3f}] {c[:70]}{'...' if len(c)>70 else ''}{mark}")

    sep("ĐẦU RA — BiLSTM Extractive  (cần chạy run_pipeline.py trước)")
    bi = tom_tat_bilstm(cac_cau, SO_CAU_TOM_TAT)
    if bi:
        print(bi)
    else:
        print("(chưa có model — chạy: python run_pipeline.py vi)")

    sep("ĐẦU RA — Seq2Seq Abstractive  (cần chạy run_pipeline.py trước)")
    s2s = tom_tat_seq2seq(VAN_BAN)
    if s2s:
        print(s2s)
    else:
        print("(chưa có model — chạy: python run_pipeline.py vi)")

    sep()
    print("Để tóm tắt bài khác: mở demo.py, thay nội dung biến VAN_BAN")


if __name__ == "__main__":
    main()
