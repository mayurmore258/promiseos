"""Safe Dataset Loader with strict Access Control and Schema Validation."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

ML_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = ML_DIR / "datasets"

EXPECTED_COLUMNS = {
    "id", "text", "label", "domain", "difficulty",
    "has_deadline", "has_condition", "has_owner",
    "language_style", "source_type", "reason"
}

ALLOWED_LABELS = {"COMMITMENT", "NON_COMMITMENT"}


class DatasetAccessViolationError(Exception):
    """Raised when training workflow attempts unauthorized access to hidden datasets."""
    pass


class DatasetValidationError(Exception):
    """Raised when a dataset violates schema, integrity, or non-null constraints."""
    pass


def load_dataset(
    split: str,
    datasets_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """Loads a core dataset split (train, validation, or test) with integrity validation.
    
    Enforces that 'hidden' split cannot be loaded via standard training loader.
    """
    base_dir = datasets_dir or DATASETS_DIR
    split_lower = split.lower().strip()

    # STRICT ACCESS CONTROL: Deny hidden access in normal loader
    if "hidden" in split_lower:
        raise DatasetAccessViolationError(
            f"Access Denied: Standard dataset loader cannot access '{split}'. "
            "The hidden surprise dataset is strictly reserved for the final evaluation script."
        )

    split_map = {
        "train": base_dir / "train" / "train.csv",
        "validation": base_dir / "validation" / "validation.csv",
        "val": base_dir / "validation" / "validation.csv",
        "test": base_dir / "test" / "test.csv",
        "train_v2": base_dir / "train_v2" / "train_v2.csv",
        "hard_validation": base_dir / "hard_augmentation" / "hard_validation.csv",
        "hard_val": base_dir / "hard_augmentation" / "hard_validation.csv",
    }

    if split_lower not in split_map:
        raise ValueError(f"Unknown split '{split}'. Allowed splits: {list(split_map.keys())}")

    file_path = split_map[split_lower]
    if not file_path.exists():
        if split_lower == "train_v2":
            # Auto-construct V2 training dataset from core train + hard train
            build_v2_training_dataset(base_dir)
        else:
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

    df = pd.read_csv(file_path, encoding="utf-8")

    # Schema & Integrity Checks
    missing_cols = EXPECTED_COLUMNS - set(df.columns)
    if missing_cols:
        raise DatasetValidationError(f"Missing columns in {file_path}: {missing_cols}")

    if df.empty:
        raise DatasetValidationError(f"Dataset {file_path} is empty.")

    if df["text"].isnull().any():
        raise DatasetValidationError(f"Found null texts in {file_path}")

    if df["label"].isnull().any():
        raise DatasetValidationError(f"Found null labels in {file_path}")

    invalid_labels = set(df["label"].unique()) - ALLOWED_LABELS
    if invalid_labels:
        raise DatasetValidationError(f"Found invalid labels in {file_path}: {invalid_labels}")

    if df["id"].duplicated().any():
        raise DatasetValidationError(f"Found duplicate IDs in {file_path}")

    return df


def build_v2_training_dataset(datasets_dir: Optional[Path] = None) -> Path:
    """Builds and saves the V2 training dataset (Core Train + Hard Train).
    
    Strictly excludes hidden dataset and preserves original validation & test sets.
    """
    base_dir = datasets_dir or DATASETS_DIR
    core_train_file = base_dir / "train" / "train.csv"
    hard_train_file = base_dir / "hard_augmentation" / "hard_train.csv"

    if not core_train_file.exists():
        raise FileNotFoundError(f"Core train file not found: {core_train_file}")
    if not hard_train_file.exists():
        raise FileNotFoundError(f"Hard train file not found: {hard_train_file}")

    core_df = pd.read_csv(core_train_file, encoding="utf-8")
    hard_df = pd.read_csv(hard_train_file, encoding="utf-8")

    combined_df = pd.concat([core_df, hard_df], ignore_index=True)
    out_dir = base_dir / "train_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "train_v2.csv"
    combined_df.to_csv(out_file, index=False, encoding="utf-8")
    return out_file


def load_core_splits(datasets_dir: Optional[Path] = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads all three core splits: train, validation, test."""
    train_df = load_dataset("train", datasets_dir)
    val_df = load_dataset("validation", datasets_dir)
    test_df = load_dataset("test", datasets_dir)
    return train_df, val_df, test_df


def load_v2_splits(datasets_dir: Optional[Path] = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads V2 training split, original validation, hard validation, and original test split.
    
    Returns:
        (train_v2_df, original_val_df, hard_val_df, test_df)
    """
    base_dir = datasets_dir or DATASETS_DIR
    v2_file = base_dir / "train_v2" / "train_v2.csv"
    if not v2_file.exists():
        build_v2_training_dataset(base_dir)

    train_v2_df = load_dataset("train_v2", base_dir)
    orig_val_df = load_dataset("validation", base_dir)
    hard_val_df = load_dataset("hard_val", base_dir)
    test_df = load_dataset("test", base_dir)

    return train_v2_df, orig_val_df, hard_val_df, test_df

