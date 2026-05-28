"""
evaluate.py
Đánh giá TextRank và BiLSTM bằng ROUGE
"""
import json
import os
import sys
import numpy as np
from rouge_score import rouge_scorer as rs

SCORER = rs.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)


def rouge(pred: str, ref: str) -> dict:
    s = SCORER.score(ref, pred)
    return {k: round(v.fmeasure, 4) for k, v in s.items()}


def avg(scores: list[dict]) -> dict:
    keys = scores[0].keys()
    return {k: round(np.mean([s[k] for s in scores]), 4) for k in keys}


def evaluate_textrank(data: list[dict], num_sentences: int = 3) -> dict:
    from textrank import summarize
    results = []
    for item in data:
        sents = item["article_sentences"]
        ref = item["summary_raw"]
        pred, _ = summarize(sents, num_sentences)
        results.append(rouge(pred, ref))
    return avg(results)


def evaluate_bilstm(data: list[dict], model_path: str, num_sentences: int = 3) -> dict:
    from bilstm_extractive import load_model, predict
    model, vec = load_model(model_path)
    results = []
    for item in data:
        sents = item["article_sentences"]
        ref = item["summary_raw"]
        pred = predict(sents, model, vec, num_sentences)
        results.append(rouge(pred, ref))
    return avg(results)


def print_table(results: dict):
    print("\n" + "=" * 62)
    print(f"{'Model':<25} {'ROUGE-1':>8} {'ROUGE-2':>8} {'ROUGE-L':>8}")
    print("-" * 62)
    for name, scores in results.items():
        print(
            f"{name:<25} {scores['rouge1']:>8.4f} "
            f"{scores['rouge2']:>8.4f} {scores['rougeL']:>8.4f}"
        )
    print("=" * 62)


def run_all(lang: str = "vi"):
    with open(f"data/processed_{lang}.json", encoding="utf-8") as f:
        data = json.load(f)

    split = int(len(data) * 0.8)
    test_data = data[split:]
    print(f"\n[INFO] Đánh giá trên {len(test_data)} bài test ({lang.upper()})")

    results = {}

    print("[1/2] Đánh giá TextRank...")
    results["TextRank (baseline)"] = evaluate_textrank(test_data)

    bilstm_path = f"models/bilstm_{lang}.pt"
    if os.path.exists(bilstm_path):
        print("[2/2] Đánh giá BiLSTM...")
        results["BiLSTM Extractive"] = evaluate_bilstm(test_data, bilstm_path)
    else:
        print("[2/2] BiLSTM chưa train, bỏ qua")

    print_table(results)

    out_path = f"outputs/evaluation_{lang}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Kết quả lưu tại {out_path}")
    return results


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "vi"
    run_all(lang)
