# PromiseOS Commitment Classifier V2 — Training & Model Comparison Report

## Overview
- **Model Version:** `V2 (Generalization Improvement)`
- **Selected Champion:** `linearsvc_word12_c1`
- **Champion Configuration:** `Linear SVM (C=1.0, word 1-2 ngrams, max_features=8000)`
- **Random Seed:** `42`
- **V2 Model Artifact:** `C:\Users\Admin\Desktop\promiseos\backend\ml\models\commitment_classifier_v2.joblib`
- **Production Status:** Candidate model (NOT promoted to production yet).

## Dataset Composition
- **V2 Training Set:** 1020 examples (Core Train: 700, Hard Augmentation: 320)
- **Original Validation Set:** 150 examples (Untouched)
- **Hard Validation Set:** 120 examples
- **Combined Validation Set:** 270 examples
- **Original Test Set:** 150 examples (Untouched benchmark)

## Candidate Model Comparison (Fair Validation Selection)
| Candidate | Algorithm | Orig Val F1 | Hard Val F1 | Combined Val F1 | Combined Val Acc |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **logreg_word12_c1** | Logistic Regression (C=1.0, word 1-2 ngrams, max_features=8000) | 0.9933 | 0.9062 | 0.9531 | 0.9519 |
| **logreg_word12_c2** | Logistic Regression (C=2.0, word 1-2 ngrams, max_features=8000) | 0.9933 | 0.9206 | 0.9600 | 0.9593 |
| **logreg_word13_c1** | Logistic Regression (C=1.0, word 1-3 ngrams, max_features=12000) | 0.9867 | 0.8992 | 0.9462 | 0.9444 |
| **linearsvc_word12_c1** | Linear SVM (C=1.0, word 1-2 ngrams, max_features=8000) | 0.9867 | 0.9355 | 0.9635 | 0.9630 |
| **calibrated_linearsvc_word12** | Calibrated Linear SVM (C=1.0, word 1-2 ngrams, max_features=8000) | 0.9933 | 0.9280 | 0.9635 | 0.9630 |
| **logreg_word13_c2** | Logistic Regression (C=2.0, word 1-3 ngrams, max_features=12000) | 0.9867 | 0.9062 | 0.9496 | 0.9481 |

## Champion Model Validation Performance
### Original Validation Split (150 samples)
- **Accuracy:** `0.9867`
- **Precision:** `0.9867`
- **Recall:** `0.9867`
- **F1 Score:** `0.9867`

### Hard Validation Split (120 samples)
- **Accuracy:** `0.9333`
- **Precision:** `0.9062`
- **Recall:** `0.9667`
- **F1 Score:** `0.9355`

### Combined Validation (270 samples)
- **Accuracy:** `0.9630`
- **Precision:** `0.9496`
- **Recall:** `0.9778`
- **F1 Score:** `0.9635`

## Benchmark Evaluation on Untouched Original Test Set (150 samples)
- **Accuracy:** `0.9933`
- **Precision:** `0.9868`
- **Recall:** `1.0000`
- **F1 Score:** `0.9934`

### Confusion Matrix (Original Test Set)
| | Pred: NON_COMMITMENT | Pred: COMMITMENT |
| :--- | :--- | :--- |
| **Actual: NON_COMMITMENT** | 74 | 1 |
| **Actual: COMMITMENT** | 0 | 75 |
