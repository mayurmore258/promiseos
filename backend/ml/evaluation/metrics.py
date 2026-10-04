"""Evaluation metrics calculation for Commitment Classification."""

from typing import Any, Dict, List, Union
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def compute_metrics(
    y_true: Union[List[str], np.ndarray],
    y_pred: Union[List[str], np.ndarray],
    pos_label: str = "COMMITMENT",
) -> Dict[str, Any]:
    """Computes comprehensive binary classification metrics.
    
    Returns:
        Dict containing accuracy, precision, recall, f1, support, and confusion_matrix.
    """
    y_true = list(y_true)
    y_pred = list(y_pred)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, pos_label=pos_label, zero_division=0))
    rec = float(recall_score(y_true, y_pred, pos_label=pos_label, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, pos_label=pos_label, zero_division=0))

    # Confusion matrix with explicit labels order: [NON_COMMITMENT, COMMITMENT]
    labels_order = ["NON_COMMITMENT", "COMMITMENT"]
    cm = confusion_matrix(y_true, y_pred, labels=labels_order).tolist()

    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "support": {
            "total": len(y_true),
            "commitment": sum(1 for y in y_true if y == "COMMITMENT"),
            "non_commitment": sum(1 for y in y_true if y == "NON_COMMITMENT"),
        },
        "confusion_matrix": {
            "labels": labels_order,
            "matrix": cm,
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }
