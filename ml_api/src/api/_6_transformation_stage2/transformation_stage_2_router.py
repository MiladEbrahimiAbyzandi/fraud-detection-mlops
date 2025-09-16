from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
import pandas as pd
import json
from api._6_transformation_stage2.transformation_stage_2 import transform_stage2
from api.router_constants import X_TRAIN_PATH, X_TEST_PATH, X_TEST_TRANSFOMED2_PATH,X_TRAIN_TRANSFOMED2_PATH, METADATA_PATH
from api._3_transformation_stage1.model import TransactionFeatures
router=APIRouter()

class TransformationStage2Request(BaseModel):
    x_train_path: str =str(X_TRAIN_PATH)
    x_test_path: str = str(X_TEST_PATH)
    metadata: str = str(METADATA_PATH)

    @field_validator("x_train_path", "x_test_path", mode="before")
    def check_file_exists(cls, v: str):
        v=Path(v)
        if not(v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The CSV file is not found")
        return str(v)
    @field_validator("metadata", mode="before")
    def check_metadata_exists(cls, v:str):
        v=Path(v)
        if not (v.suffix.lower() == ".json" and v.is_file()):
            raise ValueError("The metadata JSON file is not found")
        return str(v)
    
class TransformationStage2Response(BaseModel):
    X_train_transformed: str
    X_test_transformed: str
    message: str

    @field_validator("X_train_transformed", "X_test_transformed", mode="after")
    def check_csv(cls, v: str):
        v=Path(v)
        if not (v.suffix.lower() == ".csv" and v.is_file()) :
            raise ValueError("The file must be a CSV")
        return str(v)

@router.post("/transformation-stage2", tags=["Transformation"])
async def transformation_stage2_endpoint(request: TransformationStage2Request):
    """
    Perform the second stage of data transformation on split data.
    """
    try:
        X_train=pd.read_csv(request.x_train_path, parse_dates=["timestamp", "Acct_Open_Date", "Expires", "Date"]  )
        X_test=pd.read_csv(request.x_test_path, parse_dates=["timestamp", "Acct_Open_Date", "Expires", "Date"] )
        
        # try:
        #     X_train=load_X_train.copy()
        #     X_test=load_X_test.copy()
        #     validated_train=(TransactionFeatures(**row) for row in X_train.to_dict(orient="records"))
        #     validated_test=(TransactionFeatures(**row) for row in X_test.to_dict(orient="records"))
        #     X_train=pd.DataFrame([v.model_dump() for v in validated_train])
        #     X_test=pd.DataFrame([v.model_dump() for v in validated_test])
        
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"Data validation error: {e}"
        #     )
            
        with open(request.metadata, "r") as f:
            artifacts=json.load(f)

        X_train_transformed=transform_stage2(artifacts, X_train)
        X_test_transformed=transform_stage2(artifacts, X_test)

        X_train_transformed.to_csv(X_TRAIN_TRANSFOMED2_PATH, index=False)
        X_test_transformed.to_csv(X_TEST_TRANSFOMED2_PATH, index=False)

        return TransformationStage2Response(
                X_train_transformed=str(X_TRAIN_TRANSFOMED2_PATH),
                X_test_transformed=str(X_TEST_TRANSFOMED2_PATH),
                message=f"Second stage transformation completed successfully. Files saved to: {X_TRAIN_TRANSFOMED2_PATH}, {X_TEST_TRANSFOMED2_PATH}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= str(e)
        )