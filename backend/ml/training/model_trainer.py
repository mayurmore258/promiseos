"""Model Training, Hyperparameter Comparison, Selection, and Freezing."""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from ml.evaluation.metrics import compute_metrics
from ml.preprocessing.text_cleaner import clean_text

ML_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ML_DIR / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "commitment_classifier.joblib"

RANDOM_SEED = 42


def build_pipeline(algorithm: str = "logistic_regression") -> Pipeline:
    """Builds an scikit-learn Pipeline with custom TF-IDF and specified classifier."""
    vectorizer = TfidfVectorizer(
        preprocessor=clean_text,
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
        min_df=2,
    )

    if algorithm == "logistic_regression":
        classifier = LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=RANDOM_SEED,
            class_weight="balanced",
            solver="lbfgs",
        )
    elif algorithm == "linear_svm":
        classifier = LinearSVC(
            C=1.0,
            max_iter=2000,
            random_state=RANDOM_SEED,
            class_weight="balanced",
        )
    else:
        raise ValueError(f"Unsupported algorithm '{algorithm}'. Choose 'logistic_regression' or 'linear_svm'.")

    return Pipeline([
        ("tfidf", vectorizer),
        ("classifier", classifier),
    ])


def train_and_compare(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> Tuple[Pipeline, Dict[str, Any]]:
    """Trains candidate models, compares on validation split, selects best, evaluates test split."""
    X_train, y_train = train_df["text"], train_df["label"]
    X_val, y_val = val_df["text"], val_df["label"]
    X_test, y_test = test_df["text"], test_df["label"]

    algorithms = ["logistic_regression", "linear_svm"]
    candidate_results = {}
    fitted_pipelines = {}

    for algo in algorithms:
        pipe = build_pipeline(algo)
        pipe.fit(X_train, y_train)
        fitted_pipelines[algo] = pipe

        val_preds = pipe.predict(X_val)
        val_metrics = compute_metrics(y_val, val_preds)
        candidate_results[algo] = {
            "validation_metrics": val_metrics,
            "pipeline": pipe,
        }

    # Selection criterion: Highest validation F1 score (then accuracy)
    best_algo = max(
        algorithms,
        key=lambda a: (
            candidate_results[a]["validation_metrics"]["f1"],
            candidate_results[a]["validation_metrics"]["accuracy"],
        )
    )

    champion_pipeline = fitted_pipelines[best_algo]
    champion_val_metrics = candidate_results[best_algo]["validation_metrics"]

    # Evaluate champion on unseen TEST set
    test_preds = champion_pipeline.predict(X_test)
    test_metrics = compute_metrics(y_test, test_preds)

    # Compile report summary
    comparison_summary = {
        algo: {
            "accuracy": candidate_results[algo]["validation_metrics"]["accuracy"],
            "precision": candidate_results[algo]["validation_metrics"]["precision"],
            "recall": candidate_results[algo]["validation_metrics"]["recall"],
            "f1": candidate_results[algo]["validation_metrics"]["f1"],
        }
        for algo in algorithms
    }

    report = {
        "selected_algorithm": best_algo,
        "random_seed": RANDOM_SEED,
        "feature_representation": {
            "type": "TF-IDF (1-2 grams)",
            "max_features": 5000,
            "min_df": 2,
            "sublinear_tf": True,
            "preprocessor": "clean_text",
        },
        "model_hyperparameters": {
            "algorithm": best_algo,
            "C": 1.0,
            "class_weight": "balanced",
            "random_state": RANDOM_SEED,
        },
        "dataset_splits": {
            "train_size": len(train_df),
            "validation_size": len(val_df),
            "test_size": len(test_df),
        },
        "algorithm_comparison_on_validation": comparison_summary,
        "validation_metrics": champion_val_metrics,
        "test_metrics": test_metrics,
    }

    return champion_pipeline, report


def save_model(pipeline: Pipeline, path: Optional[Path] = None) -> Path:
    """Saves the fitted pipeline to local disk."""
    out_path = path or DEFAULT_MODEL_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, out_path)
    return out_path


def load_frozen_model(path: Optional[Path] = None) -> Pipeline:
    """Loads the serialized model artifact from disk."""
    model_path = path or DEFAULT_MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(f"Model artifact not found at {model_path}. Run training first.")
    return joblib.load(model_path)
