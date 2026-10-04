"""CLI Entry Point: Train and Evaluate Commitment Classifier.

Usage:
    python -m ml.training.train_commitment_classifier
"""

import json
from pathlib import Path
from ml.training.dataset_loader import load_core_splits
from ml.training.model_trainer import train_and_compare, save_model

ML_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ML_DIR / "reports"


def run_training_pipeline():
    print("=" * 60)
    print("PROMISEOS LOCAL ML TRAINING PIPELINE")
    print("=" * 60)

    # 1. Load Core Splits ONLY (Strictly no hidden dataset)
    print("\n[Step 1/5] Loading Core Datasets (Train, Validation, Test)...")
    train_df, val_df, test_df = load_core_splits()
    print(f"  Train:      {len(train_df)} rows")
    print(f"  Validation: {len(val_df)} rows")
    print(f"  Test:       {len(test_df)} rows")

    # 2. Train and Compare Models
    print("\n[Step 2/5] Training candidate models (Logistic Regression vs Linear SVM)...")
    champion_pipe, report = train_and_compare(train_df, val_df, test_df)

    print("\n[Step 3/5] Validation Comparison:")
    for algo, m in report["algorithm_comparison_on_validation"].items():
        print(f"  - {algo:<20}: Acc={m['accuracy']:.4f}, Prec={m['precision']:.4f}, Rec={m['recall']:.4f}, F1={m['f1']:.4f}")

    print(f"\n[Step 4/5] Selected Champion Algorithm: {report['selected_algorithm']}")
    test_m = report["test_metrics"]
    print(f"  Test Set Performance:")
    print(f"    Accuracy:  {test_m['accuracy']:.4f}")
    print(f"    Precision: {test_m['precision']:.4f}")
    print(f"    Recall:    {test_m['recall']:.4f}")
    print(f"    F1 Score:  {test_m['f1']:.4f}")
    print(f"    Confusion Matrix: {test_m['confusion_matrix']['matrix']}")

    # 5. Save Artifact and Reports
    print("\n[Step 5/5] Freezing Model and Saving Reports...")
    model_path = save_model(champion_pipe)
    print(f"  Model saved to: {model_path}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_report_path = REPORTS_DIR / "training_report.json"
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"  JSON report: {json_report_path}")

    md_report_path = REPORTS_DIR / "training_report.md"
    md_content = f"""# PromiseOS Commitment Classifier — Training Report

## Architecture & Configuration
- **Selected Algorithm:** `{report['selected_algorithm']}`
- **Feature Pipeline:** TF-IDF (1-2 ngrams, max_features=5000, sublinear_tf=True)
- **Random Seed:** `{report['random_seed']}`
- **Model Path:** `{model_path}`

## Dataset Split Counts
- **Train:** {report['dataset_splits']['train_size']} examples
- **Validation:** {report['dataset_splits']['validation_size']} examples
- **Test:** {report['dataset_splits']['test_size']} examples

## Validation Model Selection
| Algorithm | Accuracy | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** | {report['algorithm_comparison_on_validation']['logistic_regression']['accuracy']:.4f} | {report['algorithm_comparison_on_validation']['logistic_regression']['precision']:.4f} | {report['algorithm_comparison_on_validation']['logistic_regression']['recall']:.4f} | {report['algorithm_comparison_on_validation']['logistic_regression']['f1']:.4f} |
| **Linear SVM** | {report['algorithm_comparison_on_validation']['linear_svm']['accuracy']:.4f} | {report['algorithm_comparison_on_validation']['linear_svm']['precision']:.4f} | {report['algorithm_comparison_on_validation']['linear_svm']['recall']:.4f} | {report['algorithm_comparison_on_validation']['linear_svm']['f1']:.4f} |

## Unseen Test Evaluation (Champion: {report['selected_algorithm']})
- **Accuracy:** `{test_m['accuracy']:.4f}`
- **Precision:** `{test_m['precision']:.4f}`
- **Recall:** `{test_m['recall']:.4f}`
- **F1 Score:** `{test_m['f1']:.4f}`

### Confusion Matrix (Test Split)
| | Pred: NON_COMMITMENT | Pred: COMMITMENT |
| :--- | :--- | :--- |
| **Actual: NON_COMMITMENT** | {test_m['confusion_matrix']['tn']} | {test_m['confusion_matrix']['fp']} |
| **Actual: COMMITMENT** | {test_m['confusion_matrix']['fn']} | {test_m['confusion_matrix']['tp']} |
"""
    with open(md_report_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  Markdown report: {md_report_path}")

    print("\n" + "=" * 60)
    print("TRAINING PIPELINE COMPLETE (Model frozen, ready for hidden eval)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_training_pipeline()
