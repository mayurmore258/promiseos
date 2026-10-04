"""V2 Commitment Classifier Training, Comparison, Selection, and Freezing.

Round 2 ML Generalization Improvement:
- Trains on V2 dataset (Core Train 700 + Hard Augmentation Train 320 = 1020 examples).
- Compares Logistic Regression and LinearSVC across representation variants.
- Selects champion model strictly using validation performance (Original Val + Hard Val).
- Zero hidden dataset access during training or model selection.
- Evaluates champion on Original Test Set (150 examples) for unbiased baseline comparison.
- Freezes artifact to backend/ml/models/commitment_classifier_v2.joblib (V1 untouched).
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from ml.evaluation.metrics import compute_metrics
from ml.preprocessing.text_cleaner import clean_text
from ml.training.dataset_loader import load_v2_splits

ML_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ML_DIR / "models"
REPORTS_DIR = ML_DIR / "reports"
V2_MODEL_PATH = MODELS_DIR / "commitment_classifier_v2.joblib"

RANDOM_SEED = 42


def get_candidate_configurations() -> List[Dict[str, Any]]:
    """Defines candidate configurations for local CPU baseline comparison."""
    return [
        {
            "name": "logreg_word12_c1",
            "algorithm": "logistic_regression",
            "model": LogisticRegression(
                C=1.0,
                max_iter=1000,
                random_state=RANDOM_SEED,
                class_weight="balanced",
                solver="lbfgs"
            ),
            "vectorizer": TfidfVectorizer(
                preprocessor=clean_text,
                ngram_range=(1, 2),
                max_features=8000,
                sublinear_tf=True,
                min_df=2
            ),
            "description": "Logistic Regression (C=1.0, word 1-2 ngrams, max_features=8000)"
        },
        {
            "name": "logreg_word12_c2",
            "algorithm": "logistic_regression",
            "model": LogisticRegression(
                C=2.0,
                max_iter=1000,
                random_state=RANDOM_SEED,
                class_weight="balanced",
                solver="lbfgs"
            ),
            "vectorizer": TfidfVectorizer(
                preprocessor=clean_text,
                ngram_range=(1, 2),
                max_features=8000,
                sublinear_tf=True,
                min_df=2
            ),
            "description": "Logistic Regression (C=2.0, word 1-2 ngrams, max_features=8000)"
        },
        {
            "name": "logreg_word13_c1",
            "algorithm": "logistic_regression",
            "model": LogisticRegression(
                C=1.0,
                max_iter=1000,
                random_state=RANDOM_SEED,
                class_weight="balanced",
                solver="lbfgs"
            ),
            "vectorizer": TfidfVectorizer(
                preprocessor=clean_text,
                ngram_range=(1, 3),
                max_features=12000,
                sublinear_tf=True,
                min_df=2
            ),
            "description": "Logistic Regression (C=1.0, word 1-3 ngrams, max_features=12000)"
        },
        {
            "name": "linearsvc_word12_c1",
            "algorithm": "linear_svm",
            "model": LinearSVC(
                C=1.0,
                max_iter=2000,
                random_state=RANDOM_SEED,
                class_weight="balanced"
            ),
            "vectorizer": TfidfVectorizer(
                preprocessor=clean_text,
                ngram_range=(1, 2),
                max_features=8000,
                sublinear_tf=True,
                min_df=2
            ),
            "description": "Linear SVM (C=1.0, word 1-2 ngrams, max_features=8000)"
        },
        {
            "name": "calibrated_linearsvc_word12",
            "algorithm": "calibrated_linear_svm",
            "model": CalibratedClassifierCV(
                estimator=LinearSVC(
                    C=1.0,
                    max_iter=2000,
                    random_state=RANDOM_SEED,
                    class_weight="balanced"
                ),
                cv=3
            ),
            "vectorizer": TfidfVectorizer(
                preprocessor=clean_text,
                ngram_range=(1, 2),
                max_features=8000,
                sublinear_tf=True,
                min_df=2
            ),
            "description": "Calibrated Linear SVM (C=1.0, word 1-2 ngrams, max_features=8000)"
        },
        {
            "name": "logreg_word13_c2",
            "algorithm": "logistic_regression",
            "model": LogisticRegression(
                C=2.0,
                max_iter=1000,
                random_state=RANDOM_SEED,
                class_weight="balanced",
                solver="lbfgs"
            ),
            "vectorizer": TfidfVectorizer(
                preprocessor=clean_text,
                ngram_range=(1, 3),
                max_features=12000,
                sublinear_tf=True,
                min_df=2
            ),
            "description": "Logistic Regression (C=2.0, word 1-3 ngrams, max_features=12000)"
        },
    ]


def run_v2_training() -> Tuple[Pipeline, Dict[str, Any]]:
    """Runs the V2 training pipeline and returns champion pipeline and report."""
    print("=" * 65)
    print("PROMISEOS V2 LOCAL ML TRAINING & MODEL SELECTION")
    print("=" * 65)

    # 1. Load V2 Splits (Core Train + Hard Train; strictly NO hidden dataset)
    print("\n[Step 1/5] Loading V2 Training Splits & Validation Benchmarks...")
    train_df, orig_val_df, hard_val_df, test_df = load_v2_splits()
    print(f"  Train V2:            {len(train_df)} rows ({sum(train_df['label'] == 'COMMITMENT')} C, {sum(train_df['label'] == 'NON_COMMITMENT')} NC)")
    print(f"  Original Validation: {len(orig_val_df)} rows")
    print(f"  Hard Validation:     {len(hard_val_df)} rows")
    print(f"  Original Test Set:   {len(test_df)} rows (Preserved for fair comparison)")

    X_train, y_train = train_df["text"], train_df["label"]

    # 2. Train and evaluate all candidates
    print("\n[Step 2/5] Training and Evaluating Candidate Configurations...")
    candidates = get_candidate_configurations()
    candidate_results = {}
    fitted_pipelines = {}

    for cand in candidates:
        name = cand["name"]
        pipe = Pipeline([
            ("tfidf", cand["vectorizer"]),
            ("classifier", cand["model"])
        ])
        pipe.fit(X_train, y_train)
        fitted_pipelines[name] = pipe

        orig_val_pred = pipe.predict(orig_val_df["text"])
        orig_val_metrics = compute_metrics(orig_val_df["label"], orig_val_pred)

        hard_val_pred = pipe.predict(hard_val_df["text"])
        hard_val_metrics = compute_metrics(hard_val_df["label"], hard_val_pred)

        # Combined validation metric
        comb_true = list(orig_val_df["label"]) + list(hard_val_df["label"])
        comb_pred = list(orig_val_pred) + list(hard_val_pred)
        comb_val_metrics = compute_metrics(comb_true, comb_pred)

        candidate_results[name] = {
            "config": cand["description"],
            "algorithm": cand["algorithm"],
            "orig_val_metrics": orig_val_metrics,
            "hard_val_metrics": hard_val_metrics,
            "comb_val_metrics": comb_val_metrics,
        }

        print(f"  - {cand['description']:<65}")
        print(f"    Orig Val F1: {orig_val_metrics['f1']:.4f} | Hard Val F1: {hard_val_metrics['f1']:.4f} | Combined Val F1: {comb_val_metrics['f1']:.4f}")

    # 3. Fair Champion Selection (Based strictly on validation performance)
    print("\n[Step 3/5] Selecting V2 Champion Model...")
    # Selection criteria: Highest combined validation F1 score, then hard validation F1 score
    champion_name = max(
        candidates,
        key=lambda c: (
            candidate_results[c["name"]]["comb_val_metrics"]["f1"],
            candidate_results[c["name"]]["hard_val_metrics"]["f1"],
            candidate_results[c["name"]]["orig_val_metrics"]["f1"],
        )
    )["name"]

    champion_pipe = fitted_pipelines[champion_name]
    champ_res = candidate_results[champion_name]
    print(f"  Selected Champion: {champion_name} ({champ_res['config']})")
    print(f"  Champion Validation Performance:")
    print(f"    Original Val: Acc={champ_res['orig_val_metrics']['accuracy']:.4f}, Prec={champ_res['orig_val_metrics']['precision']:.4f}, Rec={champ_res['orig_val_metrics']['recall']:.4f}, F1={champ_res['orig_val_metrics']['f1']:.4f}")
    print(f"    Hard Val:     Acc={champ_res['hard_val_metrics']['accuracy']:.4f}, Prec={champ_res['hard_val_metrics']['precision']:.4f}, Rec={champ_res['hard_val_metrics']['recall']:.4f}, F1={champ_res['hard_val_metrics']['f1']:.4f}")
    print(f"    Combined Val: Acc={champ_res['comb_val_metrics']['accuracy']:.4f}, Prec={champ_res['comb_val_metrics']['precision']:.4f}, Rec={champ_res['comb_val_metrics']['recall']:.4f}, F1={champ_res['comb_val_metrics']['f1']:.4f}")

    # 4. Evaluate Champion on Original Test Set (Unbiased test benchmark)
    print("\n[Step 4/5] Evaluating Champion on Untouched Original Test Set...")
    test_pred = champion_pipe.predict(test_df["text"])
    test_metrics = compute_metrics(test_df["label"], test_pred)
    print(f"  Original Test Set Performance:")
    print(f"    Accuracy:  {test_metrics['accuracy']:.4f}")
    print(f"    Precision: {test_metrics['precision']:.4f}")
    print(f"    Recall:    {test_metrics['recall']:.4f}")
    print(f"    F1 Score:  {test_metrics['f1']:.4f}")
    print(f"    Confusion Matrix: {test_metrics['confusion_matrix']['matrix']}")

    # 5. Freezing Model V2 & Compiling Report
    print("\n[Step 5/5] Freezing V2 Artifact and Saving Reports...")
    V2_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(champion_pipe, V2_MODEL_PATH)
    print(f"  V2 Model saved to: {V2_MODEL_PATH}")

    # Build report
    comparison_table = {
        name: {
            "description": candidate_results[name]["config"],
            "original_val_f1": candidate_results[name]["orig_val_metrics"]["f1"],
            "hard_val_f1": candidate_results[name]["hard_val_metrics"]["f1"],
            "combined_val_f1": candidate_results[name]["comb_val_metrics"]["f1"],
            "combined_val_acc": candidate_results[name]["comb_val_metrics"]["accuracy"],
        }
        for name in candidate_results
    }

    report = {
        "model_version": "v2",
        "selected_champion": champion_name,
        "champion_description": champ_res["config"],
        "random_seed": RANDOM_SEED,
        "v2_model_path": str(V2_MODEL_PATH),
        "dataset_split_counts": {
            "train_v2_total": len(train_df),
            "train_core": 700,
            "train_hard_aug": 320,
            "original_validation": len(orig_val_df),
            "hard_validation": len(hard_val_df),
            "combined_validation": len(orig_val_df) + len(hard_val_df),
            "original_test": len(test_df),
        },
        "candidate_comparison": comparison_table,
        "champion_metrics": {
            "original_validation": champ_res["orig_val_metrics"],
            "hard_validation": champ_res["hard_val_metrics"],
            "combined_validation": champ_res["comb_val_metrics"],
            "original_test": test_metrics,
        },
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / "training_report_v2.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"  JSON report: {json_path}")

    md_path = REPORTS_DIR / "training_report_v2.md"
    orig_val_m = champ_res["orig_val_metrics"]
    hard_val_m = champ_res["hard_val_metrics"]
    comb_val_m = champ_res["comb_val_metrics"]
    cm_test = test_metrics["confusion_matrix"]

    md_content = f"""# PromiseOS Commitment Classifier V2 — Training & Model Comparison Report

## Overview
- **Model Version:** `V2 (Generalization Improvement)`
- **Selected Champion:** `{champion_name}`
- **Champion Configuration:** `{champ_res['config']}`
- **Random Seed:** `{RANDOM_SEED}`
- **V2 Model Artifact:** `{V2_MODEL_PATH}`
- **Production Status:** Candidate model (NOT promoted to production yet).

## Dataset Composition
- **V2 Training Set:** {len(train_df)} examples (Core Train: 700, Hard Augmentation: 320)
- **Original Validation Set:** {len(orig_val_df)} examples (Untouched)
- **Hard Validation Set:** {len(hard_val_df)} examples
- **Combined Validation Set:** {len(orig_val_df) + len(hard_val_df)} examples
- **Original Test Set:** {len(test_df)} examples (Untouched benchmark)

## Candidate Model Comparison (Fair Validation Selection)
| Candidate | Algorithm | Orig Val F1 | Hard Val F1 | Combined Val F1 | Combined Val Acc |
| :--- | :--- | :---: | :---: | :---: | :---: |
"""
    for name, cdata in comparison_table.items():
        md_content += f"| **{name}** | {cdata['description']} | {cdata['original_val_f1']:.4f} | {cdata['hard_val_f1']:.4f} | {cdata['combined_val_f1']:.4f} | {cdata['combined_val_acc']:.4f} |\n"

    md_content += f"""
## Champion Model Validation Performance
### Original Validation Split (150 samples)
- **Accuracy:** `{orig_val_m['accuracy']:.4f}`
- **Precision:** `{orig_val_m['precision']:.4f}`
- **Recall:** `{orig_val_m['recall']:.4f}`
- **F1 Score:** `{orig_val_m['f1']:.4f}`

### Hard Validation Split (120 samples)
- **Accuracy:** `{hard_val_m['accuracy']:.4f}`
- **Precision:** `{hard_val_m['precision']:.4f}`
- **Recall:** `{hard_val_m['recall']:.4f}`
- **F1 Score:** `{hard_val_m['f1']:.4f}`

### Combined Validation (270 samples)
- **Accuracy:** `{comb_val_m['accuracy']:.4f}`
- **Precision:** `{comb_val_m['precision']:.4f}`
- **Recall:** `{comb_val_m['recall']:.4f}`
- **F1 Score:** `{comb_val_m['f1']:.4f}`

## Benchmark Evaluation on Untouched Original Test Set (150 samples)
- **Accuracy:** `{test_metrics['accuracy']:.4f}`
- **Precision:** `{test_metrics['precision']:.4f}`
- **Recall:** `{test_metrics['recall']:.4f}`
- **F1 Score:** `{test_metrics['f1']:.4f}`

### Confusion Matrix (Original Test Set)
| | Pred: NON_COMMITMENT | Pred: COMMITMENT |
| :--- | :--- | :--- |
| **Actual: NON_COMMITMENT** | {cm_test['tn']} | {cm_test['fp']} |
| **Actual: COMMITMENT** | {cm_test['fn']} | {cm_test['tp']} |
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  Markdown report: {md_path}")

    print("\n" + "=" * 65)
    print("V2 TRAINING & FREEZING COMPLETE (Ready for final hidden eval)")
    print("=" * 65 + "\n")
    return champion_pipe, report


if __name__ == "__main__":
    run_v2_training()
