"""Three-way benchmark comparison: V1 vs V2 LinearSVC vs V2 Calibrated."""

from pathlib import Path
import joblib
import pandas as pd
from ml.evaluation.metrics import compute_metrics
from ml.training.dataset_loader import load_v2_splits

ML_DIR = Path(__file__).resolve().parent.parent
V1_PATH = ML_DIR / "models" / "commitment_classifier.joblib"
V2_PATH = ML_DIR / "models" / "commitment_classifier_v2.joblib"
V2_CAL_PATH = ML_DIR / "models" / "commitment_classifier_v2_calibrated.joblib"


def run_benchmark():
    v1_model = joblib.load(V1_PATH)
    v2_model = joblib.load(V2_PATH)
    v2_cal_model = joblib.load(V2_CAL_PATH)

    _, orig_val, hard_val, test = load_v2_splits()

    splits = [
        ("Original Validation (150 samples)", orig_val),
        ("Hard Validation (120 samples)", hard_val),
        ("Original Test Set (150 samples)", test),
    ]

    models = [
        ("V1 (LogisticRegression)", v1_model),
        ("V2 (LinearSVC uncalibrated)", v2_model),
        ("V2 Calibrated (CalibratedClassifierCV)", v2_cal_model),
    ]

    for split_name, df in splits:
        print("=" * 70)
        print(f"BENCHMARK ON: {split_name}")
        print("=" * 70)
        print(f"{'Model':<40} | {'Acc':<7} | {'Prec':<7} | {'Rec':<7} | {'F1':<7}")
        print("-" * 70)

        for m_name, model in models:
            preds = model.predict(df["text"])
            m = compute_metrics(df["label"], preds)
            cm = m["confusion_matrix"]
            print(f"{m_name:<40} | {m['accuracy']:<7.4f} | {m['precision']:<7.4f} | {m['recall']:<7.4f} | {m['f1']:<7.4f} | CM: [[{cm['tn']}, {cm['fp']}], [{cm['fn']}, {cm['tp']}]]")
        print()


if __name__ == "__main__":
    run_benchmark()
