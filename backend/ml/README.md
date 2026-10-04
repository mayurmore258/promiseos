# PromiseOS Local ML — Commitment Classification

## 1. Overview
The **Commitment Classification** ML module provides a lightweight, CPU-efficient, local machine learning component for PromiseOS to distinguish between messages containing binding commitments and general conversational noise or requests.

- **Task**: Binary Text Classification (`COMMITMENT` vs `NON_COMMITMENT`)
- **Philosophy**: This is **NOT** a lie detector, personality classifier, or fulfillment predictor. It strictly determines whether a given text snippet contains a trackable, actionable commitment.
- **Execution**: 100% local, CPU-based scikit-learn pipeline (zero external API calls, zero credit consumption, zero cloud database dependencies).

---

## 2. Directory Layout
```text
backend/ml/
├── README.md                      # Comprehensive documentation
├── datasets/                      # Local datasets
│   ├── train/train.csv            # 700 samples (350 Commitment / 350 Non-commitment)
│   ├── validation/validation.csv  # 150 samples (75 Commitment / 75 Non-commitment)
│   ├── test/test.csv              # 150 samples (75 Commitment / 75 Non-commitment)
│   └── hidden/                    # Isolated surprise evaluation set
│       ├── hidden_inputs.csv      # 200 samples (inputs only, no labels)
│       └── hidden_labels.csv      # 200 samples (ground truth labels + reasons)
├── models/
│   └── commitment_classifier.joblib # Frozen serialized model artifact
├── preprocessing/
│   ├── __init__.py
│   └── text_cleaner.py            # Contraction-preserving text normalizer
├── training/
│   ├── __init__.py
│   ├── dataset_loader.py          # Secure data loader with access control
│   ├── model_trainer.py           # Pipeline definitions & model selection
│   └── train_commitment_classifier.py # Main training CLI
├── evaluation/
│   ├── __init__.py
│   ├── metrics.py                 # Accuracy, Precision, Recall, F1, Confusion Matrix
│   └── evaluate_hidden.py         # Surprise evaluation CLI
├── scripts/
│   ├── __init__.py
│   ├── generate_datasets.py       # Domain-specific synthetic dataset generator
│   └── quality_checks.py          # Leakage & integrity verification
└── reports/
    ├── training_report.json
    ├── training_report.md
    ├── hidden_evaluation_report.json
    └── hidden_evaluation_report.md
```

---

## 3. Labeling Policy & Domain Categories

### Positive Class (`COMMITMENT`)
A statement indicating that the speaker or a designated party undertakes a concrete obligation or deliverable:
* **Explicit First-Person**: `"I will email the client proposal by 5 PM today."`
* **Delegated / Third-Person**: `"Arjun will deploy the patch tonight."`
* **Conditional Commitments**: `"If CI passes, I will push the release to staging."`
* **Multi-Message Dialogue**: Messy chat containing a firm undertaking amidst noise.
* **Informal / Student Language**: `"Bro don't worry, I'll finish the slides before midnight."`

### Negative Class (`NON_COMMITMENT`)
Statements that do not constitute an active commitment by the speaker:
* **Questions / Inquiries**: `"Can you send the report by Friday?"`
* **Requests Directed at Others**: `"Please upload the wireframes when possible."`
* **Suggestions / Opinions**: `"We should probably redesign the onboarding flow."`
* **Weak Intentions / Aspirational**: `"I'm thinking about working on the docs tomorrow."`
* **Factual Status Reports**: `"The server crashed at 3 AM."`
* **Conversational Noise / Gratitude**: `"Sounds good, thank you!"`
* **Explicit Negations**: `"I cannot promise that the feature will be ready."`
* **Historical / Completed Actions**: `"I already sent the invoice yesterday."`

---

## 4. Reproducibility & Commands

### Dataset Quality & Leakage Checks
```bash
python -m ml.scripts.quality_checks
```
Verifies:
- 0 null or empty values.
- Balanced classes (50/50).
- 0 text overlap across any split pairs (Train, Validation, Test, Hidden).
- Strict access control enforcement.

### Model Training & Validation
```bash
python -m ml.training.train_commitment_classifier
```
Trains Logistic Regression and Linear SVM on `train.csv`, evaluates both on `validation.csv`, selects champion (`logistic_regression`), scores on unseen `test.csv`, freezes `commitment_classifier.joblib`, and writes reports.

### Hidden Surprise Evaluation
```bash
python -m ml.evaluation.evaluate_hidden
```
Loads the frozen model artifact, reads `hidden_inputs.csv` blindly without labels, predicts classes, and scores against `hidden_labels.csv`.

---

## 5. Summary of Results

| Split | Size | Accuracy | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Validation** | 150 | 0.9800 | 0.9737 | 0.9867 | 0.9801 |
| **Test** | 150 | 0.9800 | 0.9737 | 0.9867 | 0.9801 |
| **Hidden Surprise** | 200 | 0.5950 | 0.5760 | 0.7200 | 0.6400 |

### Observations on Hidden Surprise Evaluation
The hidden evaluation dataset contained adversarial negations (`"I definitely cannot commit to..."`), speculative reflections (`"I really should send the quotation..."`), and hypothetical conditions without commitment. The frozen classical TF-IDF model captured 72% recall on tricky commitments, but showed false positive susceptibility on sentences dense with deadline/deliverable keywords. This highlights the exact value of an isolated surprise evaluation set for future model iterations.
