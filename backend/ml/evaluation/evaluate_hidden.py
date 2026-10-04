"""Final Hidden Surprise Evaluation Script.

Evaluates the frozen Commitment Classifier model against the hidden surprise dataset.
Workflow:
1. Load frozen model.
2. Load hidden_inputs.csv (NO labels present).
3. Generate predictions.
4. Only then load hidden_labels.csv.
5. Compute metrics and generate reports.
6. Strictly DO NOT retrain or alter model.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
from ml.evaluation.metrics import compute_metrics
from ml.training.model_trainer import load_frozen_model

ML_DIR = Path(__file__).resolve().parent.parent
HIDDEN_DIR = ML_DIR / "datasets" / "hidden"
REPORTS_DIR = ML_DIR / "reports"
V2_MODEL_PATH = ML_DIR / "models" / "commitment_classifier_v2.joblib"


def run_hidden_evaluation(
    model_path: Optional[Path] = None,
    report_suffix: str = "",
) -> Dict[str, Any]:
    target_path = Path(model_path) if model_path else None
    version_label = "V2" if (target_path and "v2" in str(target_path).lower()) else "V1"

    print("=" * 60)
    print(f"PROMISEOS FINAL HIDDEN SURPRISE EVALUATION ({version_label})")
    print("=" * 60)

    # 1. Load Frozen Model
    print("\n[Step 1/5] Loading frozen model artifact...")
    model = load_frozen_model(target_path)
    print(f"  Frozen model loaded successfully: {target_path or 'Default V1'}")

    # 2. Load Hidden Inputs (Labels are NOT in this file)
    print("\n[Step 2/5] Loading hidden inputs (isolated from labels)...")
    inputs_file = HIDDEN_DIR / "hidden_inputs.csv"
    if not inputs_file.exists():
        raise FileNotFoundError(f"Missing hidden inputs file: {inputs_file}")

    inputs_df = pd.read_csv(inputs_file, encoding="utf-8")
    if "label" in inputs_df.columns:
        raise ValueError("Security violation: 'label' column must NOT exist in hidden_inputs.csv!")

    print(f"  Loaded {len(inputs_df)} hidden input examples.")

    # 3. Generate Predictions
    print("\n[Step 3/5] Generating blind predictions...")
    preds = model.predict(inputs_df["text"])
    pred_commitments = sum(1 for p in preds if p == "COMMITMENT")
    pred_non_commitments = sum(1 for p in preds if p == "NON_COMMITMENT")
    print(f"  Predictions generated: {pred_commitments} COMMITMENT, {pred_non_commitments} NON_COMMITMENT.")

    # 4. Access Hidden Labels (Strictly separated until this step)
    print("\n[Step 4/5] Accessing hidden labels for scoring...")
    labels_file = HIDDEN_DIR / "hidden_labels.csv"
    if not labels_file.exists():
        raise FileNotFoundError(f"Missing hidden labels file: {labels_file}")

    labels_df = pd.read_csv(labels_file, encoding="utf-8")

    # Match IDs to ensure aligned evaluation
    merged = pd.merge(inputs_df[["id", "text", "difficulty", "domain"]], labels_df[["id", "label"]], on="id")
    if len(merged) != len(inputs_df):
        raise ValueError("ID mismatch between hidden_inputs and hidden_labels!")

    y_true = merged["label"].tolist()
    y_pred = list(preds)

    # 5. Compute Metrics
    print(f"\n[Step 5/5] Computing generalization metrics on hidden surprise set ({version_label})...")
    metrics = compute_metrics(y_true, y_pred)

    print(f"\nHIDDEN SURPRISE EVALUATION RESULTS ({version_label}):")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1']:.4f}")
    print(f"  Confusion Matrix: {metrics['confusion_matrix']['matrix']}")

    # Breakdown by difficulty
    diff_breakdown = {}
    for diff in ["easy", "medium", "hard"]:
        mask = merged["difficulty"] == diff
        if mask.any():
            sub_true = [y_true[i] for i in range(len(y_true)) if mask.iloc[i]]
            sub_pred = [y_pred[i] for i in range(len(y_pred)) if mask.iloc[i]]
            diff_breakdown[diff] = compute_metrics(sub_true, sub_pred)

    # Breakdown by domain
    domain_breakdown = {}
    for dom in sorted(merged["domain"].unique()):
        mask = merged["domain"] == dom
        if mask.any():
            sub_true = [y_true[i] for i in range(len(y_true)) if mask.iloc[i]]
            sub_pred = [y_pred[i] for i in range(len(y_pred)) if mask.iloc[i]]
            domain_breakdown[dom] = compute_metrics(sub_true, sub_pred)

    report = {
        "model_version": version_label,
        "model_path": str(target_path or "backend/ml/models/commitment_classifier.joblib"),
        "dataset": "hidden_surprise",
        "total_samples": len(y_true),
        "overall_metrics": metrics,
        "difficulty_breakdown": diff_breakdown,
        "domain_breakdown": domain_breakdown,
    }

    # Save Reports
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"_{report_suffix}" if report_suffix else ""
    json_path = REPORTS_DIR / f"hidden_evaluation_report{suffix}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    md_path = REPORTS_DIR / f"hidden_evaluation_report{suffix}.md"
    cm = metrics["confusion_matrix"]
    md_content = f"""# PromiseOS Commitment Classifier — Hidden Surprise Evaluation Report ({version_label})

## Evaluation Policy & Integrity
- **Model Status:** Frozen model artifact evaluated as-is without modification.
- **Model Path:** `{target_path or 'backend/ml/models/commitment_classifier.joblib'}`
- **Zero Contamination:** Hidden labels were withheld from training, feature engineering, and model selection.
- **Total Hidden Samples:** {len(y_true)}

## Overall Performance Metrics
- **Accuracy:** `{metrics['accuracy']:.4f}`
- **Precision:** `{metrics['precision']:.4f}`
- **Recall:** `{metrics['recall']:.4f}`
- **F1 Score:** `{metrics['f1']:.4f}`

### Confusion Matrix (Hidden Surprise Set)
| | Pred: NON_COMMITMENT | Pred: COMMITMENT |
| :--- | :--- | :--- |
| **Actual: NON_COMMITMENT** | {cm['tn']} | {cm['fp']} |
| **Actual: COMMITMENT** | {cm['fn']} | {cm['tp']} |

## Performance by Difficulty
| Difficulty | Samples | Accuracy | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Easy** | {diff_breakdown.get('easy', {}).get('support', {}).get('total', 0)} | {diff_breakdown.get('easy', {}).get('accuracy', 0):.4f} | {diff_breakdown.get('easy', {}).get('precision', 0):.4f} | {diff_breakdown.get('easy', {}).get('recall', 0):.4f} | {diff_breakdown.get('easy', {}).get('f1', 0):.4f} |
| **Medium** | {diff_breakdown.get('medium', {}).get('support', {}).get('total', 0)} | {diff_breakdown.get('medium', {}).get('accuracy', 0):.4f} | {diff_breakdown.get('medium', {}).get('precision', 0):.4f} | {diff_breakdown.get('medium', {}).get('recall', 0):.4f} | {diff_breakdown.get('medium', {}).get('f1', 0):.4f} |
| **Hard** | {diff_breakdown.get('hard', {}).get('support', {}).get('total', 0)} | {diff_breakdown.get('hard', {}).get('accuracy', 0):.4f} | {diff_breakdown.get('hard', {}).get('precision', 0):.4f} | {diff_breakdown.get('hard', {}).get('recall', 0):.4f} | {diff_breakdown.get('hard', {}).get('f1', 0):.4f} |
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\nSaved Reports:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print("\n" + "=" * 60)
    print(f"HIDDEN EVALUATION COMPLETE ({version_label})")
    print("=" * 60 + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2", action="store_true", help="Evaluate V2 model")
    parser.add_argument("--v2-calibrated", action="store_true", help="Evaluate V2 Calibrated model")
    parser.add_argument("--model", type=str, default="", help="Path to specific model artifact")
    args = parser.parse_args()

    calibrated_path = ML_DIR / "models" / "commitment_classifier_v2_calibrated.joblib"

    if args.v2_calibrated or args.model == "v2_calibrated":
        run_hidden_evaluation(model_path=calibrated_path, report_suffix="v2_calibrated")
    elif args.v2 or args.model == "v2":
        run_hidden_evaluation(model_path=V2_MODEL_PATH, report_suffix="v2")
    elif args.model:
        run_hidden_evaluation(model_path=Path(args.model), report_suffix="custom")
    else:
        run_hidden_evaluation()

