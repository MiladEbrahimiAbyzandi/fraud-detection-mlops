from fastapi import FastAPI
from api._1_data_loader.health import router as health_router
from api._2_merge_csvs.merge_csv_router import router as merge_csv_router
from api._3_transformation_stage1.transformation_stage_1_router import router as transformation_stage1_router
from api._4_splitter.splitter_router import router as splitter_router
from api._6_transformation_stage2.transformation_stage_2_router import router as transformation_stage2_router
from api._7_transformation_stage3.transformation_stage_3_training_router import router as transformation_stage3_training_router
from api._7_transformation_stage3.transformation_stage_3_inference_router import router as transformation_stage_3_inference_router
from api._8_imbalance_correction.imbalance_correction_route import router as imbalance_correction_router
from api.inference_router import router as inference_router
from api._10_evaluate.model_evaluation_router import router as model_evaluation_router
from api._9_training.training_router import router as training_router
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