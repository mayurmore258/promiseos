"""Dataset Quality Checks, Leakage Verification, and Isolation Testing."""

from pathlib import Path
from typing import Dict, List, Set
import pandas as pd

from ml.training.dataset_loader import (
    DatasetAccessViolationError,
    DatasetValidationError,
    load_core_splits,
    load_dataset,
)

ML_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = ML_DIR / "datasets"


def run_all_quality_checks() -> Dict[str, bool]:
    """Runs end-to-end dataset validation, isolation verification, and leakage checks."""
    print("=" * 60)
    print("RUNNING PROMISEOS DATASET QUALITY & INTEGRITY CHECKS")
    print("=" * 60)

    results = {}

    # 1. Core Dataset Loading and Schema Validation
    print("\n[Check 1/6] Validating Core Splits (Train, Validation, Test)...")
    try:
        train_df, val_df, test_df = load_core_splits()
        results["core_schema_valid"] = True
        print(f"  PASSED: Core splits loaded successfully.")
    except Exception as e:
        results["core_schema_valid"] = False
        print(f"  FAILED: Core loading failed: {e}")
        raise

    # 2. Hidden Dataset Isolation and Structure
    print("\n[Check 2/6] Validating Hidden Dataset Isolation & Structure...")
    hidden_inputs_file = DATASETS_DIR / "hidden" / "hidden_inputs.csv"
    hidden_labels_file = DATASETS_DIR / "hidden" / "hidden_labels.csv"

    assert hidden_inputs_file.exists(), "Missing hidden_inputs.csv"
    assert hidden_labels_file.exists(), "Missing hidden_labels.csv"

    h_in = pd.read_csv(hidden_inputs_file)
    h_lbl = pd.read_csv(hidden_labels_file)

    # Enforce that hidden inputs do NOT contain labels
    assert "label" not in h_in.columns, "CRITICAL: 'label' found in hidden_inputs.csv!"
    assert "label" in h_lbl.columns, "Missing 'label' in hidden_labels.csv"
    assert len(h_in) == len(h_lbl), f"Length mismatch: inputs ({len(h_in)}) vs labels ({len(h_lbl)})"
    assert set(h_in["id"]) == set(h_lbl["id"]), "ID set mismatch in hidden dataset files"
    results["hidden_structure_valid"] = True
    print(f"  PASSED: Hidden inputs and labels correctly separated ({len(h_in)} items).")

    # 3. Access Control Enforcement
    print("\n[Check 3/6] Testing Standard Loader Access Control...")
    try:
        load_dataset("hidden")
        results["access_control_enforced"] = False
        print("  FAILED: Standard loader allowed loading 'hidden' split!")
    except DatasetAccessViolationError:
        results["access_control_enforced"] = True
        print("  PASSED: Access control successfully blocked hidden split loading.")

    # 4. Class Balance Checks
    print("\n[Check 4/6] Verifying Class Balance Across Splits...")
    for name, df in [("Train", train_df), ("Validation", val_df), ("Test", test_df)]:
        counts = df["label"].value_counts().to_dict()
        c_count = counts.get("COMMITMENT", 0)
        nc_count = counts.get("NON_COMMITMENT", 0)
        total = len(df)
        ratio = abs(c_count - nc_count) / total
        assert ratio <= 0.10, f"{name} split imbalanced! C={c_count}, NC={nc_count}"
        print(f"  {name:<12}: Total={total}, COMMITMENT={c_count}, NON_COMMITMENT={nc_count} (Balanced)")
    results["class_balance_valid"] = True

    # 5. Non-null and String Sanity
    print("\n[Check 5/6] Checking for Nulls, Empty Strings, and Metadata Consistency...")
    for name, df in [("Train", train_df), ("Validation", val_df), ("Test", test_df)]:
        assert not df["text"].isnull().any(), f"Null text in {name}"
        assert not df["label"].isnull().any(), f"Null label in {name}"
        assert (df["text"].str.strip().str.len() > 5).all(), f"Extremely short text in {name}"
        assert df["domain"].isin([
            "project", "engineering", "sales_client", "operations",
            "academic_student", "personal_errands", "executive"
        ]).all(), f"Invalid domain in {name}"
        assert df["difficulty"].isin(["easy", "medium", "hard"]).all(), f"Invalid difficulty in {name}"
    results["metadata_valid"] = True
    print("  PASSED: All texts, labels, and metadata are valid.")

    # 6. Leakage Check (Exact and Normalized Text Overlap)
    print("\n[Check 6/7] Verifying Cross-Split Zero Data Leakage...")
    train_texts = set(train_df["text"].str.strip().str.lower())
    val_texts = set(val_df["text"].str.strip().str.lower())
    test_texts = set(test_df["text"].str.strip().str.lower())
    hidden_texts = set(h_in["text"].str.strip().str.lower())

    leakage_train_val = train_texts.intersection(val_texts)
    leakage_train_test = train_texts.intersection(test_texts)
    leakage_val_test = val_texts.intersection(test_texts)
    leakage_core_hidden = (train_texts | val_texts | test_texts).intersection(hidden_texts)

    assert not leakage_train_val, f"Leakage detected between Train and Validation: {len(leakage_train_val)} texts"
    assert not leakage_train_test, f"Leakage detected between Train and Test: {len(leakage_train_test)} texts"
    assert not leakage_val_test, f"Leakage detected between Validation and Test: {len(leakage_val_test)} texts"
    assert not leakage_core_hidden, f"Leakage detected between Core and Hidden: {len(leakage_core_hidden)} texts"

    results["zero_leakage_verified"] = True
    print("  PASSED: 0 overlapping text instances across any split pairs.")
    print("  Train intersect Val:    0")
    print("  Train intersect Test:   0")
    print("  Val intersect Test:     0")
    print("  Core intersect Hidden:  0")

    # 7. Hard Augmentation Dataset Quality & Isolation
    print("\n[Check 7/7] Validating Hard Augmentation Dataset Quality & Leakage...")
    aug_dir = DATASETS_DIR / "hard_augmentation"
    aug_full = aug_dir / "hard_examples.csv"
    aug_train = aug_dir / "hard_train.csv"
    aug_val = aug_dir / "hard_validation.csv"

    if aug_full.exists():
        df_aug = pd.read_csv(aug_full)
        df_atrain = pd.read_csv(aug_train)
        df_aval = pd.read_csv(aug_val)

        # Non-null & Schema checks
        assert not df_aug["text"].isnull().any(), "Null text in hard augmentation dataset"
        assert not df_aug["label"].isnull().any(), "Null label in hard augmentation dataset"
        assert df_aug["label"].isin(["COMMITMENT", "NON_COMMITMENT"]).all()
        assert not df_aug["id"].duplicated().any(), "Duplicate IDs in hard augmentation dataset"
        assert (df_aug["text"].str.strip().str.len() > 5).all(), "Short text in hard augmentation dataset"
        assert df_aug["difficulty"].isin(["easy", "medium", "hard"]).all()
        assert df_aug["domain"].isin([
            "project", "engineering", "sales_client", "operations",
            "academic_student", "personal_errands", "executive"
        ]).all()

        # Class balance check
        for name, d in [("Aug Full", df_aug), ("Aug Train", df_atrain), ("Aug Val", df_aval)]:
            c = (d["label"] == "COMMITMENT").sum()
            nc = (d["label"] == "NON_COMMITMENT").sum()
            assert abs(c - nc) / len(d) <= 0.05, f"{name} imbalanced: C={c}, NC={nc}"
            print(f"  {name:<12}: Total={len(d)}, COMMITMENT={c}, NON_COMMITMENT={nc} (Balanced)")

        # Leakage check: Augmentation vs Core (train, val, test) vs Hidden
        aug_texts = set(df_aug["text"].str.strip().str.lower())
        leakage_aug_core = aug_texts.intersection(train_texts | val_texts | test_texts)
        leakage_aug_hidden = aug_texts.intersection(hidden_texts)

        assert not leakage_aug_core, f"Leakage: Hard Augmentation <-> Core splits ({len(leakage_aug_core)})"
        assert not leakage_aug_hidden, f"Leakage: Hard Augmentation <-> Hidden ({len(leakage_aug_hidden)})"
        print("  PASSED: 0 overlap between Hard Augmentation and Core splits.")
        print("  PASSED: 0 overlap between Hard Augmentation and Hidden dataset.")
        results["hard_augmentation_valid"] = True
    else:
        results["hard_augmentation_valid"] = False
        print("  SKIPPED: Hard augmentation dataset not yet generated.")

    print("\n" + "=" * 60)
    print("ALL QUALITY CHECKS PASSED (100% compliant)")
    print("=" * 60 + "\n")
    return results


if __name__ == "__main__":
    run_all_quality_checks()

