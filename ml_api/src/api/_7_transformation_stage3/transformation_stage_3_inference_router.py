from fastapi import APIRouter, HTTPException

# from pydantic import BaseModel, field_validator
from pathlib import Path
from src.api._7_transformation_stage3.transformation_stage3_inference import transformation_stage3_inference
from src.api.router_constants import (
    ENCODER_PATH,
    SCALER_PATH,
    SELECTED_COLUMNS_PATH,
    X_TEST_TRANSFOMED2_PATH,
    DF_INFERENCE_TRANSFORMED3_PATH,
)

# import pandas as pd
import joblib
from src.db.db import Database

router = APIRouter()
# class TransformationStage3InferenceRequest(BaseModel):
#     inference_csv_path: str = str(X_TEST_TRANSFOMED2_PATH)
#     encoder_path: str = str(ENCODER_PATH)
#     scaler_path: str = str(SCALER_PATH)
#     selected_columns_path: str = str(SELECTED_COLUMNS_PATH)


#     @field_validator("inference_csv_path", mode="before")
#     def check_file_exists(cls, v: str):
#         v=Path(v)
#         if not(v.suffix.lower() == ".csv" and v.is_file()):
#             raise ValueError("The CSV file for inference is not found")
#         return str(v)

#     @field_validator("encoder_path", "scaler_path", "selected_columns_path", mode="before")
#     def check_joblib_files(cls, v: str):
#         v=Path(v)
#         if not (v.is_file() and v.suffix.lower() ==".joblib"):
#             raise ValueError("joblib files for calling encoder, scaler, or selected columns are not found")
#         return str(v)

# class TransformationStage3InferenceResponse(BaseModel):
#     message: str
#     transfomation_stage_3_inference: str
#     @field_validator("transfomation_stage_3_inference", mode="after")
#     def check_csv_files(cls, v: str):
#         v=Path(v)
#         if not (v.is_file() and v.suffix.lower() == ".csv"):
#             raise ValueError("The final transfomed CSV file for inference is not found")
#         return str(v)
STAGE3_INFERENCE_DESCRIPTION = """
Stage 3 (Inference) — Apply Encoder/Scaler and Align Feature Columns

Transforms inference data using preprocessing artifacts produced during training.
This guarantees the model receives the same feature representation during inference as it saw during training.

This step:
- Drops unused/leakage columns (IDs, timestamps, address/card details, raw location fields, etc.)
- Applies the saved OneHotEncoder to categorical columns
- Applies the saved RobustScaler to numeric columns (after filling missing values)
- Validates that required columns exist, raising clear errors if not
- Selects and orders features using selected_columns so the output matches the trained model input

Returns: a model-ready dataframe with the exact same feature columns used in training.
"""


@router.post("/transformation-stage3-inference",
             name="Step 7 - Third Stage of Data Transformation Based on Training Artifacts for Inference.",
             tags=["Inference"],
             description= STAGE3_INFERENCE_DESCRIPTION
             )
async def transformation_stage3_inference_endpoint():
    """
    Perform the third stage of data transformation on second stage transformed data for inference.
    """
    try:
        # Load objects
        db = Database()
        df = db.fetch_data('SELECT * FROM "X_train_transformed_stage2"')

        # df = pd.read_csv(request.inference_csv_path)
        encoder = joblib.load(ENCODER_PATH)
        scaler = joblib.load(SCALER_PATH)
        selected_columns = joblib.load(SELECTED_COLUMNS_PATH)

        df = transformation_stage3_inference(df=df, encoder=encoder, scaler=scaler, selected_columns=selected_columns)

        db.store_data(df, "transformed_inference_data_stage3")
        return "Third stage transformation for inference completed successfully."

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during the third stage transformation for inference: {str(e)}"
        )
