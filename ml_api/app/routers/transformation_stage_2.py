from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
import pandas as pd
from metadata.metadata_extractor import metadata
from transformation_stage2.transformation_stage_2 import transform_stage2
from.constants import X_TRAIN_PATH, X_TEST_PATH, Y_TRAIN_PATH, X_TEST_TRANSFOMED2_PATH,X_TRAIN_TRANSFOMED2_PATH

router=APIRouter()

class TransformationStage2Request(BaseModel):
    x_train_path: Path = X_TRAIN_PATH
    x_test_path: Path = X_TEST_PATH
    y_train_path: Path = Y_TRAIN_PATH

    @field_validator("x_train_path", "x_test_path", "y_train_path", mode="before")
    def check_file_exists(cls, v: Path):
        if not(v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The CSV file is not found")
        return v
    
class TransformationStage2Response(BaseModel):
    X_train_transformed: Path
    X_test_transformed: Path
    message: str

    @field_validator("X_train_transformed", "X_test_transformed", mode="after")
    def check_csv(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()) :
            raise ValueError("The file must be a CSV")
        return v

@router.post("/transformation-stage2", tags=["Transformation"])
async def transformation_stage2_endpoint(request: TransformationStage2Request):
    """
    Perform the second stage of data transformation on split data.
    """
    try:
        X_train=pd.read_csv(request.x_train_path)
        X_test=pd.read_csv(request.x_test_path)
        y_train=pd.read_csv(request.y_train_path)

        artifacts=metadata(X_train, y_train)

        X_train_transformed=transform_stage2(artifacts, X_train)
        X_test_transformed=transform_stage2(artifacts, X_test)

        X_train_transformed.to_csv(X_TRAIN_TRANSFOMED2_PATH, index=False)
        X_test_transformed.to_csv(X_TEST_TRANSFOMED2_PATH, index=False)

        return (
            TransformationStage2Response(
                X_train_transformed=X_TRAIN_TRANSFOMED2_PATH,
                X_test_transformed=X_TEST_TRANSFOMED2_PATH,
                message=f"Second stage transformation completed successfully. Files saved to: {X_TRAIN_TRANSFOMED2_PATH}, {X_TEST_TRANSFOMED2_PATH}"
        ))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= str(e)
        )