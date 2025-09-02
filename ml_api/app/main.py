from fastapi import FastAPI
from app.routers.health import router as health_router
from app.routers.merge_csv import router as merge_csv_router
from app.routers.transformation_stage1 import router as transformation_stage1_router
from app.routers.splitter import router as splitter_router
from app.routers.transformation_stage_2 import router as transformation_stage2_router
from app.routers.transformation_stage_3_training import router as transformation_stage3_training_router
from app.routers.transformation_stage_3_inference import router as transformation_stage_3_inference_router
from app.routers.imbalance_correction_route import router as imbalance_correction_router
from app.routers.inference import router as inference_router
from app.routers.model_evaluation import router as model_evaluation_router
from app.routers.training_router import router as training_router
app = FastAPI(
    title="Fraud Detection API",
    description="API for Transaction Fraud Detection Model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",)

app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(merge_csv_router,prefix="/api/v1", tags=["Data"])
app.include_router(transformation_stage1_router,prefix="/api/v1", tags=["Transformation"])
app.include_router(splitter_router,prefix="/api/v1", tags=["splitter"])
app.include_router(transformation_stage2_router,prefix="/api/v1", tags=["Transformation"])
app.include_router(transformation_stage3_training_router,prefix="/api/v1", tags=["Transformation"])
app.include_router(transformation_stage_3_inference_router,prefix="/api/v1", tags=["Transformation"])
app.include_router(imbalance_correction_router,prefix="/api/v1", tags=["Imbalance Correction"])
app.include_router(inference_router,prefix="/api/v1", tags=["Inference"])   
app.include_router(model_evaluation_router,prefix="/api/v1", tags=["model Evaluation"])
app.include_router(training_router,prefix="/api/v1", tags=["Training"])