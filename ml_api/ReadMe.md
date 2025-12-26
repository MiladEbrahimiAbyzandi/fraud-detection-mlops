---
editor_options: 
  markdown: 
    wrap: 72
---

# Fraud Detection ML API (End-to-End Pipeline)

A production-style **fraud detection** project that exposes the full ML
workflow through a **FastAPI** service: data ingestion → feature
engineering (multi-stage) → training → evaluation → inference.

> Live docs (Cloud Run):
> [**https://ml-api-25274068551.us-central1.run.app/docs**](https://ml-api-25274068551.us-central1.run.app/docs){.uri}

------------------------------------------------------------------------

## What this project does

This API guides you through an end-to-end workflow:

### Training flow (high level)

1.  **Merge raw datasets** (cards + users + transactions)
2.  **Transformation Stage 1**: base feature engineering (timestamps,
    demographics, ratios, risk flags)
3.  **Split**: stratified train/test split by `Is_Fraud`
4.  **Metadata artifact**: compute training-only “high risk” lists
    (states/cities/MCC/merchants) + thresholds
5.  **Transformation Stage 2**: metadata-driven risk/behavior features
6.  **Transformation Stage 3 (Training)**: drop columns, one-hot encode,
    scale numeric features, variance-based feature selection
7.  **Imbalance correction (SMOTE)**: oversample minority class **on
    training data only**
8.  **Train model**: choose **XGBoost** or **Random Forest**
9.  **Evaluate model**: accuracy, precision, recall, F1, ROC-AUC,
    confusion matrix

### Inference flow (high level)

1.  Run **Stage 1 + Stage 2** feature engineering on new data
2.  Run **Stage 3 (Inference)** using saved artifacts
    (encoder/scaler/selected columns)
3.  Load the saved model and generate:
    -   `predictions` (0/1)
    -   `predictions_proba` (fraud probability)

------------------------------------------------------------------------

------------------------------------------------------------------------

## Key design decisions (summary)

This project follows a **modular, production-style pipeline** where each
stage has one job and produces artifacts that are reused later.

-   **Multi-stage transformations (Stage 1 → Stage 2 → Stage 3):** Stage
    1 creates deterministic features from raw columns; Stage 2 adds
    metadata-driven risk signals; Stage 3 produces the final model
    matrix (encoding/scaling/feature selection).
-   **Training-only metadata artifacts (leakage prevention):**
    “High-risk” lists (states/cities/MCC/merchants) and thresholds are
    computed **only on training data** and reused during inference.
-   **Schema validation with Pydantic models:** After Stage 1/2, each
    row is validated to catch missing columns / wrong types early.
-   **Robust scaling for numeric features:** Transaction data has
    outliers; `RobustScaler` is less sensitive than `StandardScaler`.
-   **One-hot encoding with unseen-category safety:**
    `OneHotEncoder(handle_unknown="ignore")` prevents inference failures
    when new categories appear.
-   **Variance threshold feature selection:** After one-hot encoding,
    near-constant features are removed to reduce noise and speed
    training.
-   **Imbalance handling experiments:** Multiple imbalance strategies
    were tested (e.g., class weights, ADASYN/SMOTE). The best-performing
    setup used **SMOTE + XGBoost**.

See notebooks for full rationale and experiments: -
`ml_api/notebooks/data_cleaning.ipynb` -
`ml_api/notebooks/EDA & Feature engineering.ipynb` -
`ml_api/notebooks/Modelling.ipynb`

------------------------------------------------------------------------

## Results (best model)

Best-performing configuration (from experiments): **XGBoost + SMOTE**.

Metrics from the saved evaluation artifact
(`ml_api/src/fastapi_results/outputs/evaluation_metrics.json`):

-   **Precision:** 0.93
-   **Recall:** 0.89
-   **F1:** 0.91
-   **ROC-AUC:** 0.997

> Interpretation note: Fraud datasets are highly imbalanced. Accuracy
> (100%) and weighted avg (1.00) look perfect because normal
> transactions dominate (1.47M vs 1,846 fraud cases).
>
> The test set contained **1,846 fraud cases**, and the model detected
> **1,422** (77% recall). We report **macro avg** to fairly evaluate
> fraud performance.

## Tech Stack

-   **FastAPI** + **Uvicorn**
-   **pandas / numpy**
-   **scikit-learn**
-   **XGBoost**
-   **imbalanced-learn (SMOTE)**
-   **Pydantic** for schema validation
-   **PostgreSQL (Neon)** via **SQLAlchemy**
-   **Docker**
-   **Google Cloud Run** deployment
-   **GitHub Actions** CI/CD (build + push + deploy)
-   **GCP Secret Manager** for runtime environment variables

------------------------------------------------------------------------

## Repository structure (important folders)

```         
fraud-detection/
  ml_api/
    src/
      main.py                          # FastAPI app (all routers included)
      api/                             # pipeline endpoints and feature engineering
      db/                              # DB wrapper + ingestion helper
      fastapi_results/                 # generated outputs/artifacts (created at runtime)
    scripts/
      api/                             # run_dev_bash.sh, run_prod_bash.sh
      build_and_deploy.sh              # Cloud Run deploy wrapper
      _1_build_and_push_docker_image.sh# build, push, deploy to Cloud Run
      cloudrun.env                     # example env file 
    Dockerfile
    requirements.txt
    pyproject.toml
  .github/workflows/                   # CI/CD workflow(s)
  README.md
```

------------------------------------------------------------------------

## Data source

This project is built around the Kaggle dataset:

-   **Credit Card Transactions**:
    <https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions>

You can download it via Kaggle or using `kagglehub`.

------------------------------------------------------------------------

## Quickstart (local development)

### 1) Prerequisites

-   Python **3.13+** (matches `pyproject.toml` and Docker image)
-   A Postgres database (local Postgres or Neon)
-   Optional: Docker (for containerized runs)

### 2) Create & activate a virtual environment (recommended)

From `fraud-detection/ml_api`:

``` bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 3) Install dependencies

``` bash
pip install -r requirements.txt
# or, if you prefer packaging mode:
pip install -e .
```

### 4) Configure environment variables

Your scripts look for a file at:

-   `ml_api/scripts/api/.env.local`

Example (use your own DB connection string):

``` bash
# ml_api/scripts/api/.env.local
API_PORT=8000
DATABASE_URI=postgresql://USER:PASSWORD@HOST:5432/DBNAME
```

⚠️ **Security note:** avoid committing real credentials. Use secrets
(GitHub / GCP Secret Manager).

### 5) Download the raw data

Place the CSV files under (as used by the code):

```         
ml_api/raw_data/data/8/
  sd254_cards.csv
  sd254_users.csv
  User0_credit_card_transactions.csv
```

(These paths are defined in
`ml_api/src/api/_1_data_loader/constants.py`.)

### 6) Load raw CSVs into Postgres (one-time)

This project includes a helper script to load the raw datasets into
database tables:

``` bash
python -m src.db.export_data
```

It writes tables: - `"card"` - `"user"` - `"transaction"`

### 7) Run the API

From `fraud-detection/ml_api`:

``` bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Or run via the provided dev script:

``` bash
bash scripts/api/run_dev_bash.sh
```

Open: - Swagger UI: `http://localhost:8000/docs` - ReDoc:
`http://localhost:8000/redoc`

------------------------------------------------------------------------

## API endpoints (v1)

All endpoints are mounted under:

-   Base path: `/api/v1`

| Tag | Method | Path | Purpose |
|----|---:|----|----|
| Health | GET | `/health` | Health check |
| Training / Inference | POST | `/merge-csv` | Merge raw tables into a single dataset (stored in DB) |
| Training / Inference | POST | `/transformation-stage1` | Stage 1 feature engineering |
| Training | POST | `/data-split` | Stratified train/test split |
| Training | POST | `/artifacts` | Compute metadata artifact (high-risk lists + thresholds) |
| Training / Inference | POST | `/transformation-stage2` | Stage 2 metadata-driven features |
| Training | POST | `/transformation-stage3` | Stage 3 preprocessing for training (encode/scale/select + save artifacts) |
| Inference | POST | `/transformation-stage3-inference` | Stage 3 preprocessing for inference using saved artifacts |
| Training | POST | `/imbalance_correction` | SMOTE oversampling (training only) |
| Training | POST | `/train` | Train model (xgboost or randomforest) |
| Training | POST | `/evaluate` | Evaluate model on test set |
| Inference | POST | `/inference` | Load trained model and run predictions on inference table |

------------------------------------------------------------------------

## Recommended call order

### Training

1.  `POST /merge-csv`
2.  `POST /transformation-stage1`
3.  `POST /data-split`
4.  `POST /artifacts`
5.  `POST /transformation-stage2`
6.  `POST /transformation-stage3`
7.  `POST /imbalance_correction`
8.  `POST /train`
9.  `POST /evaluate`

### Inference

1.  `POST /merge-csv` *(optional; depends on your inference ingestion
    strategy)*
2.  `POST /transformation-stage1`
3.  `POST /transformation-stage2`
4.  `POST /transformation-stage3-inference`
5.  `POST /inference`

------------------------------------------------------------------------

## Outputs & artifacts

The API writes artifacts to:

-   `ml_api/src/fastapi_results/outputs/`

Key artifacts include: - `metadata.json` - `encoder.joblib` -
`scaler.joblib` - `selected_columns.joblib` - `model.joblib` -
`evaluation_metrics.json` - `inference_results.json`

These artifacts are what make training and inference consistent.

------------------------------------------------------------------------

## Database tables used

Common tables written/read by the pipeline include: - `"card"`,
`"user"`, `"transaction"` (raw ingestion) - `"merged_data"` -
`"transformed_data_stage1"` - `"X_train"`, `"X_test"`, `"y_train"`,
`"y_test"` - `"transformed_X_train_stage2"`,
`"transformed_X_test_stage2"` - `"transformed_X_train_stage3"`,
`"transformed_X_test_stage3"` - `"transformed_inference_data_stage3"`

------------------------------------------------------------------------

## CI/CD & Cloud Run deployment

This repo includes GitHub Actions workflows for Cloud Run deployment,
plus scripts under `ml_api/scripts/`.

### What the workflow does

-   Authenticates to GCP using a service account key stored in GitHub
    Secrets
-   Builds and pushes a Docker image to Artifact Registry
-   Deploys the service to **Cloud Run**
-   Loads runtime environment variables (e.g., DB connection string)
    from **GCP Secret Manager** into `cloudrun.env`

### Required GitHub configuration (typical)

-   **Repository Variables**:
    -   `GCP_PROJECT_ID`
-   **Repository Secrets**:
    -   `GCP_SA_KEY_SHARPLY` *(service account JSON key)*

> See: `.github/workflows/*cloudrun*.yml` for the exact names used.

------------------------------------------------------------------------

## Troubleshooting

### “Feature mismatch” during inference

Make sure: - you ran the training Stage 3 endpoint first (so
encoder/scaler/selected_columns exist) - your inference data contains
the same required columns before Stage 3

### DB connection errors

-   Confirm your Postgres is reachable
-   Confirm your connection string is correct
-   Consider moving DB credentials into environment variables
    (recommended)

------------------------------------------------------------------------

## Notebooks

Exploratory notebooks are under:

-   `ml_api/notebooks/`

------------------------------------------------------------------------

## Author

**Milad Ebrahimi**
