from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
from src.api.utils.io import save_joblib
import pandas as pd
from src.db.db import Database
from src.api._7_transformation_stage3.transformation_stage3_training import transformation_stage3_training
from src.api.router_constants import (
    X_TRAIN_TRANSFOMED2_PATH,
    X_TEST_TRANSFOMED2_PATH,
    X_TEST_TRANSFORMED3_PATH,
    X_TRAIN_TRANSFOMED3_PATH,
    ENCODER_PATH,
    SCALER_PATH,
    SELECTED_COLUMNS_PATH,
)

STAGE3_TRAINING_DESCRIPTION = """
Stage 3 (Training) — Encode, Scale, and Select Features

Prepares Stage 2 data for model training by converting it into a fully numeric, model-ready matrix.
This step also produces preprocessing artifacts that must be reused during inference.

This step:
- Drops unused/leakage columns (IDs, raw timestamps, address/card details, raw location fields, etc.)
- One-hot encodes categorical columns using OneHotEncoder(handle_unknown="ignore")
- Scales numeric columns with RobustScaler (robust to outliers), filling missing values with training means
- Removes near-constant features using VarianceThreshold(threshold=0.0001)
- Aligns X_test columns to match X_train using the selected feature list

Returns:
X_train_transformed, X_test_transformed, encoder, scaler, selected_columns.
"""

router = APIRouter()

# class TransformationStage3Request(BaseModel):
#     X_train_transfomed : str = str(X_TRAIN_TRANSFOMED2_PATH)
#     X_test_transfomed : str = str(X_TEST_TRANSFOMED2_PATH)

#     @field_validator("X_train_transfomed", "X_test_transfomed", mode="before")
#     def check_file_exists(cls, v: str):
#         v=Path(v)
#         if not(v.suffix.lower() == ".csv" and v.is_file()):
#             raise ValueError("The CSV file is not found")
#         return str(v)

# class TransformationStage3Response(BaseModel):
#     X_train_transformed3: str
#     X_test_transformed3: str
#     encoder_path: str
#     scaler_path: str
#     selected_columns_path: str
#     message: str

# @field_validator("X_train_transformed3", "X_test_transformed3", mode="after")
# def check_csv_files(cls, v: str):
#     v=Path(v)
#     if not (v.is_file() and v.suffix.lower() == ".csv"):
#         raise ValueError("The file must be a CSV")
#     return str(v)

# @field_validator("encoder_path", "scaler_path", "selected_columns_path", mode="after")
# def check_joblib_files(cls, v: str):
#     v=Path(v)
#     if not (v.is_file() and v.suffix.lower() ==".joblib"):
#         raise ValueError("The file must be a joblib file")
#     return str(v)


@router.post("/transformation-stage3",
             name="Step 6 - Third Stage of Data Transformation on Second Stage Transformed data for Training.",
    tags=["Training"],
    description= STAGE3_TRAINING_DESCRIPTION
             )
async def transformation_stage3_training_endpoint():
    """
    Perform the third stage of data transformation on second stage transformed data for training.
    """
    try:
        # X_train_transformed=pd.read_csv(request.X_train_transfomed)
        # X_test_transformed=pd.read_csv(request.X_test_transfomed)

        db = Database()

        X_train_transformed = db.fetch_data('SELECT * FROM "X_train_transformed_stage2"')
        X_test_transformed = db.fetch_data('SELECT * FROM "X_test_transformed_stage2"')

        X_train_transformed3, X_test_transformed3, encoder, scaler, selected_columns = transformation_stage3_training(
            X_train=X_train_transformed, X_test=X_test_transformed
        )
        # X_train_transformed3.to_csv(X_TRAIN_TRANSFOMED3_PATH, index=False)
        # X_test_transformed3.to_csv(X_TEST_TRANSFORMED3_PATH, index=False)
        db.store_data(X_train_transformed3, "X_train_transformed_stage3")
        db.store_data(X_test_transformed3, "X_test_transformed_stage3")
        save_joblib(encoder, ENCODER_PATH)
        save_joblib(scaler, SCALER_PATH)
        save_joblib(selected_columns, SELECTED_COLUMNS_PATH)

        return "Third stage transformation completed successfully. Transfomed datasets saved to database and encoder scaler and selected columns list saved to local storage."
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
