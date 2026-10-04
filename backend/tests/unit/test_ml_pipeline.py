"""Unit tests for PromiseOS Local Machine Learning Pipeline.

Tests:
1. Dataset loading and schema validation
2. Label integrity and balance
3. Text cleaner preprocessing
4. Metrics calculation correctness
5. Pipeline building, training, and inference
6. Model save and load round-trip
7. Zero data leakage across splits
8. Strict access control on hidden surprise dataset
"""

import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from ml.evaluation.metrics import compute_metrics
from ml.preprocessing.text_cleaner import clean_text
from ml.training.dataset_loader import (
    DatasetAccessViolationError,
    DatasetValidationError,
    load_core_splits,
    load_dataset,
)
from ml.training.model_trainer import (
    build_pipeline,
    load_frozen_model,
    save_model,
    train_and_compare,
)


def test_text_cleaner_preprocessing():
    """Verify that cleaner normalizes whitespace, preserves contractions, and removes punctuation."""
    raw = "Rahul: I'll SEND the revised proposal before 5 PM tomorrow!\n\n"
    cleaned = clean_text(raw)
    assert "i'll" in cleaned
    assert "send" in cleaned
    assert "!" not in cleaned
    assert "\n" not in cleaned

    empty = clean_text(None)
    assert empty == ""


def test_dataset_loader_and_schema():
    """Verify core splits load with expected schema and valid non-null rows."""
    train_df, val_df, test_df = load_core_splits()

    for name, df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        assert len(df) > 0
        assert "id" in df.columns
        assert "text" in df.columns
        assert "label" in df.columns
        assert df["label"].isin(["COMMITMENT", "NON_COMMITMENT"]).all()
        assert not df["text"].isnull().any()
        assert not df["label"].isnull().any()


def test_hidden_dataset_access_control():
    """Enforce that standard loader blocks access to hidden datasets."""
    with pytest.raises(DatasetAccessViolationError) as exc_info:
        load_dataset("hidden")
    assert "Access Denied" in str(exc_info.value)


def test_compute_metrics():
    """Verify accuracy, precision, recall, f1, and confusion matrix calculation."""
    y_true = ["COMMITMENT", "COMMITMENT", "NON_COMMITMENT", "NON_COMMITMENT"]
    y_pred = ["COMMITMENT", "NON_COMMITMENT", "NON_COMMITMENT", "NON_COMMITMENT"]

    m = compute_metrics(y_true, y_pred)
    assert m["accuracy"] == 0.75
    assert m["precision"] == 1.0  # 1 TP, 0 FP
    assert m["recall"] == 0.5     # 1 TP, 1 FN
    assert m["f1"] == round(2 * (1.0 * 0.5) / (1.0 + 0.5), 4)
    assert m["confusion_matrix"]["tp"] == 1
    assert m["confusion_matrix"]["fn"] == 1
    assert m["confusion_matrix"]["tn"] == 2
    assert m["confusion_matrix"]["fp"] == 0


def test_model_pipeline_train_and_predict():
    """Verify pipeline instantiation, fitting, and inference on fresh strings."""
    train_data = pd.DataFrame({
        "id": ["1", "2", "3", "4"],
        "text": [
            "I will send the quotation tomorrow morning.",
            "I promise to complete the slides tonight.",
            "Can you review this pull request?",
            "What time is our sync scheduled for?",
        ],
        "label": ["COMMITMENT", "COMMITMENT", "NON_COMMITMENT", "NON_COMMITMENT"],
    })

    pipe = build_pipeline("logistic_regression")
    pipe.fit(train_data["text"], train_data["label"])

    preds = pipe.predict(["I will deliver the report Friday.", "Did you eat lunch?"])
    assert len(preds) == 2
    assert preds[0] in ["COMMITMENT", "NON_COMMITMENT"]


def test_model_serialization_roundtrip():
    """Verify model can be saved and loaded back with identical predictions."""
    pipe = build_pipeline("logistic_regression")
    texts = ["I will deploy the fix.", "Where is the file?"]
    labels = ["COMMITMENT", "NON_COMMITMENT"]
    pipe.fit(texts, labels)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_model_path = Path(tmpdir) / "test_model.joblib"
        save_model(pipe, tmp_model_path)
        assert tmp_model_path.exists()

        loaded_pipe = load_frozen_model(tmp_model_path)
        pred_orig = pipe.predict(["I will deploy tonight."])
        pred_loaded = loaded_pipe.predict(["I will deploy tonight."])
        assert pred_orig[0] == pred_loaded[0]


def test_frozen_production_model_exists_and_infers():
    """Verify that the official frozen production model loads and runs inference."""
    model = load_frozen_model()
    sample = "I'll upload the design files before the demo at 2 PM."
    pred = model.predict([sample])[0]
    assert pred == "COMMITMENT"


def test_data_leakage_detector():
    """Verify that zero overlap exists between core splits and hidden set."""
    train_df, val_df, test_df = load_core_splits()
    
    hidden_inputs_file = Path("ml/datasets/hidden/hidden_inputs.csv")
    assert hidden_inputs_file.exists()
    hidden_df = pd.read_csv(hidden_inputs_file)

    train_set = set(train_df["text"].str.strip().str.lower())
    val_set = set(val_df["text"].str.strip().str.lower())
    test_set = set(test_df["text"].str.strip().str.lower())
    hidden_set = set(hidden_df["text"].str.strip().str.lower())

    assert len(train_set.intersection(val_set)) == 0, "Leakage: Train <-> Val"
    assert len(train_set.intersection(test_set)) == 0, "Leakage: Train <-> Test"
    assert len(val_set.intersection(test_set)) == 0, "Leakage: Val <-> Test"
    assert len((train_set | val_set | test_set).intersection(hidden_set)) == 0, "Leakage: Core <-> Hidden"


def test_v2_model_artifact_exists_and_infers():
    """Verify that V2 model artifact exists, loads, and correctly classifies clear cases."""
    v2_path = Path("ml/models/commitment_classifier_v2.joblib")
    assert v2_path.exists(), "V2 model artifact missing!"

    import joblib
    model_v2 = joblib.load(v2_path)

    # 1. Clear commitment
    pred_comm = model_v2.predict(["I will email the client proposal before 5 PM tomorrow."])[0]
    assert pred_comm == "COMMITMENT"

    # 2. Clear question with deadline (formerly common false positive)
    pred_q = model_v2.predict(["Will you be able to push the hotfix before tonight's deployment?"])[0]
    assert pred_q == "NON_COMMITMENT"

    # 3. Clear negation with deadline (formerly common false positive)
    pred_neg = model_v2.predict(["I won't send the financial forecast today because the ledger hasn't balanced."])[0]
    assert pred_neg == "NON_COMMITMENT"

    # 4. Clear speculative phrase
    pred_spec = model_v2.predict(["I might try to look over the financial forecast tomorrow if my schedule clears up."])[0]
    assert pred_spec == "NON_COMMITMENT"


def test_v2_dataset_loader_and_splits():
    """Verify load_v2_splits loads valid, balanced splits without leakage."""
    from ml.training.dataset_loader import load_v2_splits
    train_v2, orig_val, hard_val, test = load_v2_splits()

    assert len(train_v2) == 1020
    assert len(orig_val) == 150
    assert len(hard_val) == 120
    assert len(test) == 150

    # Class balance
    for name, df in [("Train V2", train_v2), ("Hard Val", hard_val)]:
        c = (df["label"] == "COMMITMENT").sum()
        nc = (df["label"] == "NON_COMMITMENT").sum()
        assert c == nc, f"Split {name} is not 50/50 balanced: {c} vs {nc}"


def test_hard_augmentation_zero_leakage():
    """Verify hard augmentation dataset has 0 overlap with core splits or hidden set."""
    from ml.training.dataset_loader import load_v2_splits, load_core_splits
    core_train, core_val, core_test = load_core_splits()
    hidden_inputs_file = Path("ml/datasets/hidden/hidden_inputs.csv")
    hidden_df = pd.read_csv(hidden_inputs_file)

    aug_file = Path("ml/datasets/hard_augmentation/hard_examples.csv")
    assert aug_file.exists()
    aug_df = pd.read_csv(aug_file)

    core_texts = set(core_train["text"].str.strip().str.lower()) | \
                 set(core_val["text"].str.strip().str.lower()) | \
                 set(core_test["text"].str.strip().str.lower())
    hidden_texts = set(hidden_df["text"].str.strip().str.lower())
    aug_texts = set(aug_df["text"].str.strip().str.lower())

    assert len(aug_texts.intersection(core_texts)) == 0, "Leakage: Hard Augmentation <-> Core"
    assert len(aug_texts.intersection(hidden_texts)) == 0, "Leakage: Hard Augmentation <-> Hidden"


def test_v2_calibrated_model_artifact_and_service_compatibility():
    """Verify calibrated V2 artifact exists, implements predict_proba, and integrates with MLCommitmentService."""
    cal_path = Path("ml/models/commitment_classifier_v2_calibrated.joblib")
    assert cal_path.exists(), "Calibrated V2 model artifact missing!"

    import joblib
    from app.services.ml_service import MLCommitmentService

    model = joblib.load(cal_path)
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")
    assert hasattr(model, "classes_")
    assert list(model.classes_) == ["COMMITMENT", "NON_COMMITMENT"]

    # Test MLCommitmentService integration without code modification
    service = MLCommitmentService(model_path=cal_path)

    # 1. Commitment check
    res_comm = service.predict("I will email the client proposal before 5 PM tomorrow.")
    assert res_comm.is_available is True
    assert res_comm.label == "COMMITMENT"
    assert res_comm.probability >= 0.80

    # 2. Non-commitment question check
    res_q = service.predict("Can you review this document when you get a chance?")
    assert res_q.is_available is True
    assert res_q.label == "NON_COMMITMENT"
    assert res_q.probability < 0.20

    # 3. Negation check
    res_neg = service.predict("I will not send the financial forecast today.")
    assert res_neg.is_available is True
    assert res_neg.label == "NON_COMMITMENT"
    assert res_neg.probability < 0.30


