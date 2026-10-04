"""Detailed Evaluation of V2 Model on Validation & Benchmark Sets."""

import json
from pathlib import Path
import joblib
import pandas as pd
from ml.evaluation.metrics import compute_metrics
from ml.training.dataset_loader import load_v2_splits

ML_DIR = Path(__file__).resolve().parent.parent
V2_MODEL_PATH = ML_DIR / "models" / "commitment_classifier_v2.joblib"


def run_v2_evaluation():
    print("=" * 65)
    print("PROMISEOS V2 MODEL DETAILED VALIDATION EVALUATION")
    print("=" * 65)

    if not V2_MODEL_PATH.exists():
        raise FileNotFoundError(f"V2 model not found at {V2_MODEL_PATH}")

    model = joblib.load(V2_MODEL_PATH)
    _, orig_val_df, hard_val_df, test_df = load_v2_splits()

    # A. Original Validation Set
    print("\n--- A. ORIGINAL VALIDATION SET (150 samples) ---")
    val_pred = model.predict(orig_val_df["text"])
    m_val = compute_metrics(orig_val_df["label"], val_pred)
    print(f"  Accuracy:  {m_val['accuracy']:.4f}")
    print(f"  Precision: {m_val['precision']:.4f}")
    print(f"  Recall:    {m_val['recall']:.4f}")
    print(f"  F1 Score:  {m_val['f1']:.4f}")
    print(f"  Confusion Matrix: {m_val['confusion_matrix']['matrix']}")

    # B. Original Test Set
    print("\n--- B. ORIGINAL TEST SET (150 samples) ---")
    test_pred = model.predict(test_df["text"])
    m_test = compute_metrics(test_df["label"], test_pred)
    print(f"  Accuracy:  {m_test['accuracy']:.4f}")
    print(f"  Precision: {m_test['precision']:.4f}")
    print(f"  Recall:    {m_test['recall']:.4f}")
    print(f"  F1 Score:  {m_test['f1']:.4f}")
    print(f"  Confusion Matrix: {m_test['confusion_matrix']['matrix']}")

    # C. Hard Validation Set
    print("\n--- C. NEW HARD VALIDATION SET (120 samples) ---")
    hard_val_pred = model.predict(hard_val_df["text"])
    m_hval = compute_metrics(hard_val_df["label"], hard_val_pred)
    print(f"  Accuracy:  {m_hval['accuracy']:.4f}")
    print(f"  Precision: {m_hval['precision']:.4f}")
    print(f"  Recall:    {m_hval['recall']:.4f}")
    print(f"  F1 Score:  {m_hval['f1']:.4f}")
    print(f"  Confusion Matrix: {m_hval['confusion_matrix']['matrix']}")

    # Breakdown by Domain on Hard Validation
    print("\n--- HARD VALIDATION: BREAKDOWN BY DOMAIN ---")
    domain_results = {}
    for dom in sorted(hard_val_df["domain"].unique()):
        sub = hard_val_df[hard_val_df["domain"] == dom]
        sub_pred = model.predict(sub["text"])
        m_dom = compute_metrics(sub["label"], sub_pred)
        domain_results[dom] = m_dom
        print(f"  {dom:<20}: Total={len(sub):<3} | Acc={m_dom['accuracy']:.4f} | Prec={m_dom['precision']:.4f} | Rec={m_dom['recall']:.4f} | F1={m_dom['f1']:.4f}")

    # Breakdown by Difficulty on Hard Validation
    print("\n--- HARD VALIDATION: BREAKDOWN BY DIFFICULTY ---")
    diff_results = {}
    for diff in sorted(hard_val_df["difficulty"].unique()):
        sub = hard_val_df[hard_val_df["difficulty"] == diff]
        sub_pred = model.predict(sub["text"])
        m_diff = compute_metrics(sub["label"], sub_pred)
        diff_results[diff] = m_diff
        print(f"  {diff:<20}: Total={len(sub):<3} | Acc={m_diff['accuracy']:.4f} | Prec={m_diff['precision']:.4f} | Rec={m_diff['recall']:.4f} | F1={m_diff['f1']:.4f}")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    run_v2_evaluation()
