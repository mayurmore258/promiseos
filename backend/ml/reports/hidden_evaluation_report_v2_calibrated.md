# PromiseOS Commitment Classifier — Hidden Surprise Evaluation Report (V2)

## Evaluation Policy & Integrity
- **Model Status:** Frozen model artifact evaluated as-is without modification.
- **Model Path:** `C:\Users\Admin\Desktop\promiseos\backend\ml\models\commitment_classifier_v2_calibrated.joblib`
- **Zero Contamination:** Hidden labels were withheld from training, feature engineering, and model selection.
- **Total Hidden Samples:** 200

## Overall Performance Metrics
- **Accuracy:** `0.8250`
- **Precision:** `0.8218`
- **Recall:** `0.8300`
- **F1 Score:** `0.8259`

### Confusion Matrix (Hidden Surprise Set)
| | Pred: NON_COMMITMENT | Pred: COMMITMENT |
| :--- | :--- | :--- |
| **Actual: NON_COMMITMENT** | 82 | 18 |
| **Actual: COMMITMENT** | 17 | 83 |

## Performance by Difficulty
| Difficulty | Samples | Accuracy | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Easy** | 25 | 0.6400 | 0.2500 | 1.0000 | 0.4000 |
| **Medium** | 41 | 0.8293 | 1.0000 | 0.8250 | 0.9041 |
| **Hard** | 134 | 0.8582 | 0.8393 | 0.8246 | 0.8319 |
