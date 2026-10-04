# PromiseOS Commitment Classifier — Training Report

## Architecture & Configuration
- **Selected Algorithm:** `logistic_regression`
- **Feature Pipeline:** TF-IDF (1-2 ngrams, max_features=5000, sublinear_tf=True)
- **Random Seed:** `42`
- **Model Path:** `C:\Users\Admin\Desktop\promiseos\backend\ml\models\commitment_classifier.joblib`

## Dataset Split Counts
- **Train:** 700 examples
- **Validation:** 150 examples
- **Test:** 150 examples

## Validation Model Selection
| Algorithm | Accuracy | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** | 0.9800 | 0.9737 | 0.9867 | 0.9801 |
| **Linear SVM** | 0.9800 | 0.9737 | 0.9867 | 0.9801 |

## Unseen Test Evaluation (Champion: logistic_regression)
- **Accuracy:** `0.9800`
- **Precision:** `0.9737`
- **Recall:** `0.9867`
- **F1 Score:** `0.9801`

### Confusion Matrix (Test Split)
| | Pred: NON_COMMITMENT | Pred: COMMITMENT |
| :--- | :--- | :--- |
| **Actual: NON_COMMITMENT** | 73 | 2 |
| **Actual: COMMITMENT** | 1 | 74 |
