from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
from api.utils.io import save_joblib
import pandas as pd
from api._7_transformation_stage3.transformation_stage3_training import transformation_stage3_training
from api.router_constants import X_TRAIN_TRANSFOMED2_PATH, X_TEST_TRANSFOMED2_PATH, X_TEST_TRANSFORMED3_PATH, X_TRAIN_TRANSFOMED3_PATH, ENCODER_PATH, SCALER_PATH, SELECTED_COLUMNS_PATH


router=APIRouter()

class TransformationStage3Request(BaseModel):
    X_train_transfomed : Path = X_TRAIN_TRANSFOMED2_PATH
    X_test_transfomed : Path = X_TEST_TRANSFOMED2_PATH

    @field_validator("X_train_transfomed", "X_test_transfomed", mode="before")
    def check_file_exists(cls, v: Path):
        if not(v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The CSV file is not found")
        return v

class TransformationStage3Response(BaseModel):
    X_train_transformed3: Path
    X_test_transformed3: Path
    encoder_path: Path
    scaler_path: Path
    selected_columns_path: Path
    message: str

    @field_validator("X_train_transformed3", "X_test_transformed3", mode="after")
    def check_csv_files(cls, v: Path):
        if not (v.is_file() and v.suffix.lower() == ".csv"):
            raise ValueError("The file must be a CSV")
        return v

    @field_validator("encoder_path", "scaler_path", "selected_columns_path", mode="after")
    def check_joblib_files(cls, v: Path):
        if not (v.is_file() and v.suffix.lower() ==".joblib"):
            raise ValueError("The file must be a joblib file")
        return v
    

@router.post("/transformation-stage3", tags=["Transformation"])
async def transformation_stage3_training_endpoint(request: TransformationStage3Request):
    """
    Perform the third stage of data transformation on second stage transformed data for training.
    """
    try:
        X_train_transformed=pd.read_csv(request.X_train_transfomed)
        X_test_transformed=pd.read_csv(request.X_test_transfomed)

        X_train_transformed3, X_test_transformed3, encoder, scaler, selected_columns = transformation_stage3_training(
        X_train=X_train_transformed, X_test=X_test_transformed)
        X_train_transformed3.to_csv(X_TRAIN_TRANSFOMED3_PATH, index=False)
        X_test_transformed3.to_csv(X_TEST_TRANSFORMED3_PATH, index=False)
        save_joblib(encoder, ENCODER_PATH) 
        save_joblib(scaler, SCALER_PATH)
        save_joblib(selected_columns, SELECTED_COLUMNS_PATH) 

        return (
            TransformationStage3Response(
                X_train_transformed3=X_TRAIN_TRANSFOMED3_PATH,
                X_test_transformed3=X_TEST_TRANSFORMED3_PATH,
                encoder_path=ENCODER_PATH,
                scaler_path=SCALER_PATH,
                selected_columns_path=SELECTED_COLUMNS_PATH,
                message=f"Third stage transformation completed successfully. Files saved to: {X_TRAIN_TRANSFOMED3_PATH}, {X_TEST_TRANSFORMED3_PATH}, {ENCODER_PATH}, {SCALER_PATH}, {SELECTED_COLUMNS_PATH}"
        ))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= str(e)
        )
        