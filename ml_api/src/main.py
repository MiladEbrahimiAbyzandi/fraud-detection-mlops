from fastapi import FastAPI

from src.api._1_data_loader.health import router as health_router
from src.api._2_merge_csvs.merge_csv_router import router as merge_csv_router
from src.api._3_transformation_stage1.transformation_stage_1_router import router as transformation_stage1_router
from src.api._4_splitter.splitter_router import router as splitter_router
from src.api._5_metadata.artifacts_router import router as artifacts_router
from src.api._6_transformation_stage2.transformation_stage_2_router import router as transformation_stage2_router
from src.api._7_transformation_stage3.transformation_stage_3_inference_router import (
    router as transformation_stage_3_inference_router,
)
from src.api._7_transformation_stage3.transformation_stage_3_training_router import (
    router as transformation_stage3_training_router,
)
from src.api._8_imbalance_correction.imbalance_correction_route import router as imbalance_correction_router
from src.api._9_training.training_router import router as training_router
from src.api._10_evaluate.model_evaluation_router import router as model_evaluation_router
from src.api.inference_router import router as inference_router

description = """
## Fraud Detection API 👋

This API provides an end-to-end machine learning pipeline for fraud detection, including:
**data preparation**, **feature engineering**, **training**, **evaluation**, and **inference**.

### Main workflow

#### Training
1. **Merge CSVs**: combine cards, users, and transactions into one dataset  
2. **Transformation Stage 1**: basic feature engineering (timestamps, demographics, ratios, risk flags)  
3. **Split**: stratified train/test split using `Is_Fraud`  
4. **Metadata Artifacts**: compute training-only metadata (high-risk states/cities/MCC/merchants, thresholds)  
5. **Transformation Stage 2**: metadata-based risk and behavior features  
6. **Transformation Stage 3 (Training)**: final preprocessing for modeling (drop columns, one-hot encode, scale, feature selection)  
7. **Imbalance Correction**: SMOTE oversampling on training data only  
8. **Training**: train a model (e.g., XGBoost or Random Forest) and save it as an artifact  
9. **Evaluation**: compute metrics (accuracy, precision, recall, F1, ROC-AUC, confusion matrix)

#### Inference
1. **Transformation Stage 1 + Stage 2 + Stage 3 (Inference)**: apply the same preprocessing using saved artifacts  
2. **Inference**: load the saved model and generate predictions + probabilities for new data

### Notes
- All endpoints are under the prefix: `/api/v1`
- Use `/docs` for interactive Swagger documentation and to test endpoints
- Training-only artifacts (metadata, encoder, scaler, selected columns, model) should be reused for inference to keep behavior consistent
"""


app = FastAPI(
    title="Fraud Detection API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    description=description,
)

app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(merge_csv_router, prefix="/api/v1")
app.include_router(transformation_stage1_router, prefix="/api/v1")
app.include_router(splitter_router, prefix="/api/v1")
app.include_router(artifacts_router, prefix="/api/v1")
app.include_router(transformation_stage2_router, prefix="/api/v1")
app.include_router(
    transformation_stage3_training_router, prefix="/api/v1")
app.include_router(
    transformation_stage_3_inference_router,
    prefix="/api/v1",
)
app.include_router(
    imbalance_correction_router, prefix="/api/v1")
app.include_router(inference_router, prefix="/api/v1")
app.include_router(training_router, prefix="/api/v1")
app.include_router(
    model_evaluation_router, prefix="/api/v1")

