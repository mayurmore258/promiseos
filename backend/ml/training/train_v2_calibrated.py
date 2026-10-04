"""V2 Calibrated Commitment Classifier Training and Freezing.

Calibrates the V2 champion (LinearSVC) using CalibratedClassifierCV on Train V2
(1,020 samples) to provide calibrated probability estimates (`predict_proba`)
while preserving high generalization performance.

Saves artifact to:
backend/ml/models/commitment_classifier_v2_calibrated.joblib
"""

import json
from pathlib import Path
from typing import Any, Dict, Tuple
import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from ml.evaluation.metrics import compute_metrics
from ml.preprocessing.text_cleaner import clean_text
from ml.training.dataset_loader import load_v2_splits

ML_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ML_DIR / "models"
REPORTS_DIR = ML_DIR / "reports"
CALIBRATED_MODEL_PATH = MODELS_DIR / "commitment_classifier_v2_calibrated.joblib"

RANDOM_SEED = 42


def build_calibrated_pipeline(cv: int = 3, method: str = "sigmoid") -> Pipeline:
    """Builds a pipeline with TF-IDF and CalibratedClassifierCV(LinearSVC)."""
    vectorizer = TfidfVectorizer(
        preprocessor=clean_text,
        ngram_range=(1, 2),
        max_features=8000,
        sublinear_tf=True,
        min_df=2,
    )

    base_svc = LinearSVC(
        C=1.0,
        max_iter=2000,
        random_state=RANDOM_SEED,
        class_weight="balanced",
    )

    calibrated_clf = CalibratedClassifierCV(
        estimator=base_svc,
        method=method,
        cv=cv,
    )

    return Pipeline([
        ("tfidf", vectorizer),
        ("classifier", calibrated_clf),
    ])


def run_calibration_pipeline() -> Tuple[Pipeline, Dict[str, Any]]:
    print("=" * 65)
    print("PROMISEOS V2 CALIBRATION PIPELINE (CalibratedClassifierCV)")
    print("=" * 65)

    # 1. Load V2 Development Splits (Strictly NO hidden data)
    print("\n[Step 1/5] Loading V2 Development Splits...")
    train_df, orig_val_df, hard_val_df, test_df = load_v2_splits()
    print(f"  Train V2:            {len(train_df)} rows")
    print(f"  Original Validation: {len(orig_val_df)} rows")
    print(f"  Hard Validation:     {len(hard_val_df)} rows")
    print(f"  Original Test Set:   {len(test_df)} rows")

    X_train, y_train = train_df["text"], train_df["label"]

    # 2. Compare CV fold strategies on validation sets
    print("\n[Step 2/5] Evaluating Calibration Settings (3-fold vs 5-fold CV)...")
    cv_configs = [3, 5]
    best_pipe = None
    best_score = -1.0
    best_cv = 3
    comparison_results = {}

    for cv_val in cv_configs:
        pipe = build_calibrated_pipeline(cv=cv_val)
        pipe.fit(X_train, y_train)

        val_pred = pipe.predict(orig_val_df["text"])
        m_val = compute_metrics(orig_val_df["label"], val_pred)

        hard_val_pred = pipe.predict(hard_val_df["text"])
        m_hval = compute_metrics(hard_val_df["label"], hard_val_pred)

        comb_true = list(orig_val_df["label"]) + list(hard_val_df["label"])
        comb_pred = list(val_pred) + list(hard_val_pred)
        m_comb = compute_metrics(comb_true, comb_pred)

        test_pred = pipe.predict(test_df["text"])
        m_test = compute_metrics(test_df["label"], test_pred)

        comparison_results[f"cv_{cv_val}"] = {
            "cv": cv_val,
            "orig_val": m_val,
            "hard_val": m_hval,
            "comb_val": m_comb,
            "test": m_test,
        }

        print(f"  CV={cv_val} -> OrigVal F1: {m_val['f1']:.4f} | HardVal F1: {m_hval['f1']:.4f} | CombVal F1: {m_comb['f1']:.4f} | Test F1: {m_test['f1']:.4f}")

        if m_comb["f1"] > best_score:
            best_score = m_comb["f1"]
            best_pipe = pipe
            best_cv = cv_val

    print(f"\n[Step 3/5] Selected Calibration Strategy: CV={best_cv} (Combined Val F1: {best_score:.4f})")
    champion_pipe = best_pipe

    # 3. Verify interface properties
    print("\n[Step 4/5] Verifying Interface Capabilities on Calibrated Artifact...")
    has_predict = hasattr(champion_pipe, "predict")
    has_predict_proba = hasattr(champion_pipe, "predict_proba")
    has_decision_func = hasattr(champion_pipe, "decision_function")
    classes_list = list(getattr(champion_pipe, "classes_", []))

    print(f"  hasattr(model, 'predict'):           {has_predict}")
    print(f"  hasattr(model, 'predict_proba'):     {has_predict_proba}")
    print(f"  hasattr(model, 'decision_function'): {has_decision_func}")
    print(f"  model.classes_:                      {classes_list}")

    assert has_predict, "Calibrated model missing predict()!"
    assert has_predict_proba, "Calibrated model missing predict_proba()!"
    assert len(classes_list) == 2, f"Expected 2 classes, got {classes_list}"

    # Sample probability check
    sample_text = "I will email the client proposal before 5 PM tomorrow."
    sample_probas = champion_pipe.predict_proba([sample_text])[0]
    comm_idx = classes_list.index("COMMITMENT")
    comm_prob = float(sample_probas[comm_idx])
    print(f"  Sample Prediction on '{sample_text}':")
    print(f"    Label: {champion_pipe.predict([sample_text])[0]}, Commitment Probability: {comm_prob:.4f}")

    # 4. Freeze Calibrated Artifact & Save Reports
    print("\n[Step 5/5] Freezing Calibrated Model Artifact and Saving Reports...")
    CALIBRATED_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(champion_pipe, CALIBRATED_MODEL_PATH)
    print(f"  Saved to: {CALIBRATED_MODEL_PATH}")

    # Compile report
    sel_data = comparison_results[f"cv_{best_cv}"]
    report = {
        "model_version": "v2_calibrated",
        "base_model": "LinearSVC (C=1.0, balanced)",
        "calibration_method": "CalibratedClassifierCV (method='sigmoid', cv=3)",
        "feature_representation": {
            "type": "TF-IDF (1-2 ngrams)",
            "max_features": 8000,
            "min_df": 2,
            "sublinear_tf": True,
            "preprocessor": "clean_text",
        },
        "training_data_used": {
            "train_v2_total": len(train_df),
            "core_train": 700,
            "hard_train": 320,
        },
        "interface_verification": {
            "has_predict": has_predict,
            "has_predict_proba": has_predict_proba,
            "has_decision_function": has_decision_func,
            "classes": classes_list,
        },
        "metrics": {
            "original_validation": sel_data["orig_val"],
            "hard_validation": sel_data["hard_val"],
            "combined_validation": sel_data["comb_val"],
            "original_test": sel_data["test"],
        },
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / "training_report_v2_calibrated.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    md_path = REPORTS_DIR / "training_report_v2_calibrated.md"
    m_val = sel_data["orig_val"]
    m_hval = sel_data["hard_val"]
    m_test = sel_data["test"]
    cm_test = m_test["confusion_matrix"]

    md_content = f"""# PromiseOS Commitment Classifier — V2 Calibrated Model Report

## Configuration & Architecture
- **Model Type:** `CalibratedClassifierCV (method='sigmoid', cv={best_cv})`
- **Base Classifier:** `LinearSVC (C=1.0, class_weight='balanced', max_iter=2000, random_state=42)`
- **Feature Extraction:** `TF-IDF (1-2 ngrams, max_features=8000, sublinear_tf=True)`
- **Artifact Path:** `{CALIBRATED_MODEL_PATH}`
- **Training Samples:** 1,020 (Core Train: 700, Hard Train: 320)

## Interface Compatibility
- **`predict()`:** Supported
- **`predict_proba()`:** Supported
- **`decision_function()`:** {has_decision_func}
- **`classes_`:** `{classes_list}`

## Performance Metrics

### Original Validation Set (150 samples)
- **Accuracy:** `{m_val['accuracy']:.4f}`
- **Precision:** `{m_val['precision']:.4f}`
- **Recall:** `{m_val['recall']:.4f}`
- **F1 Score:** `{m_val['f1']:.4f}`

### Hard Validation Set (120 samples)
- **Accuracy:** `{m_hval['accuracy']:.4f}`
- **Precision:** `{m_hval['precision']:.4f}`
- **Recall:** `{m_hval['recall']:.4f}`
- **F1 Score:** `{m_hval['f1']:.4f}`

### Benchmark Test Set (150 samples)
- **Accuracy:** `{m_test['accuracy']:.4f}`
- **Precision:** `{m_test['precision']:.4f}`
- **Recall:** `{m_test['recall']:.4f}`
- **F1 Score:** `{m_test['f1']:.4f}`

### Test Confusion Matrix
| | Pred: NON_COMMITMENT | Pred: COMMITMENT |
| :--- | :--- | :--- |
| **Actual: NON_COMMITMENT** | {cm_test['tn']} | {cm_test['fp']} |
| **Actual: COMMITMENT** | {cm_test['fn']} | {cm_test['tp']} |
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("\n" + "=" * 65)
    print("V2 CALIBRATION COMPLETE (Artifact frozen, ready for hidden eval)")
    print("=" * 65 + "\n")
    return champion_pipe, report


if __name__ == "__main__":
    run_calibration_pipeline()
