# PromiseOS Commitment Classifier — Hidden Surprise Evaluation Report

## Evaluation Policy & Integrity
- **Model Status:** Frozen model artifact evaluated as-is without modification.
- **Zero Contamination:** Hidden labels were withheld from training, feature engineering, and model selection.
- **Total Hidden Samples:** 200

## Overall Performance Metrics
- **Accuracy:** `0.5950`
- **Precision:** `0.5760`
- **Recall:** `0.7200`
- **F1 Score:** `0.6400`

### Confusion Matrix (Hidden Surprise Set)
| | Pred: NON_COMMITMENT | Pred: COMMITMENT |
| :--- | :--- | :--- |
| **Actual: NON_COMMITMENT** | 47 | 53 |
| **Actual: COMMITMENT** | 28 | 72 |

## Performance by Difficulty
| Difficulty | Samples | Accuracy | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Easy** | 25 | 0.3600 | 0.1579 | 1.0000 | 0.2727 |
| **Medium** | 41 | 0.7561 | 1.0000 | 0.7500 | 0.8571 |
| **Hard** | 134 | 0.5896 | 0.5132 | 0.6842 | 0.5865 |
