# PromiseOS Commitment Classifier — V2 Calibrated Model Report

## Configuration & Architecture
- **Model Type:** `CalibratedClassifierCV (method='sigmoid', cv=5)`
- **Base Classifier:** `LinearSVC (C=1.0, class_weight='balanced', max_iter=2000, random_state=42)`
- **Feature Extraction:** `TF-IDF (1-2 ngrams, max_features=8000, sublinear_tf=True)`
- **Artifact Path:** `C:\Users\Admin\Desktop\promiseos\backend\ml\models\commitment_classifier_v2_calibrated.joblib`
- **Training Samples:** 1,020 (Core Train: 700, Hard Train: 320)

## Interface Compatibility
- **`predict()`:** Supported
- **`predict_proba()`:** Supported
- **`decision_function()`:** False
- **`classes_`:** `['COMMITMENT', 'NON_COMMITMENT']`

## Performance Metrics

### Original Validation Set (150 samples)
- **Accuracy:** `0.9933`
- **Precision:** `1.0000`
- **Recall:** `0.9867`
- **F1 Score:** `0.9933`

### Hard Validation Set (120 samples)
- **Accuracy:** `0.9333`
- **Precision:** `0.9062`
- **Recall:** `0.9667`
- **F1 Score:** `0.9355`

### Benchmark Test Set (150 samples)
- **Accuracy:** `0.9867`
- **Precision:** `0.9867`
- **Recall:** `0.9867`
- **F1 Score:** `0.9867`

### Test Confusion Matrix
| | Pred: NON_COMMITMENT | Pred: COMMITMENT |
| :--- | :--- | :--- |
| **Actual: NON_COMMITMENT** | 74 | 1 |
| **Actual: COMMITMENT** | 1 | 74 |
