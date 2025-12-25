from fastapi import APIRouter, HTTPException

# from pydantic import BaseModel, field_validator
from pathlib import Path
import pandas as pd
import json
from src.api._6_transformation_stage2.transformation_stage_2 import transform_stage2
from src.db.db import Database
from src.api.router_constants import (
    X_TRAIN_PATH,
    X_TEST_PATH,
    X_TEST_TRANSFOMED2_PATH,
    X_TRAIN_TRANSFOMED2_PATH,
    METADATA_PATH,
)

# from src.api._3_transformation_stage1.model import TransactionFeatures
router = APIRouter()

# class TransformationStage2Request(BaseModel):
#     x_train_path: str =str(X_TRAIN_PATH)
#     x_test_path: str = str(X_TEST_PATH)
#     metadata: str = str(METADATA_PATH)

#     @field_validator("x_train_path", "x_test_path", mode="before")
#     def check_file_exists(cls, v: str):
#         v=Path(v)
#         if not(v.suffix.lower() == ".csv" and v.is_file()):
#             raise ValueError("The CSV file is not found")
#         return str(v)
#     @field_validator("metadata", mode="before")
#     def check_metadata_exists(cls, v:str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".json" and v.is_file()):
#             raise ValueError("The metadata JSON file is not found")
#         return str(v)

# class TransformationStage2Response(BaseModel):
#     X_train_transformed: str
#     X_test_transformed: str
#     message: str

#     @field_validator("X_train_transformed", "X_test_transformed", mode="after")
#     def check_csv(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".csv" and v.is_file()) :
#             raise ValueError("The file must be a CSV")
#         return str(v)

STAGE2_DESCRIPTION = """
Stage 2 — Metadata-Based Risk Features

Adds second-stage features using a saved metadata artifact (generated from training data).
This ensures consistent feature engineering for both training and inference without recalculating
high-risk lists on unseen data.

This step:
- Uses metadata: high_risk_states, high_risk_cities, high_risk_mcc, high_risk_merchants, and a threshold
- Creates risk flags:
  - high_risk_state, high_risk_cities, high_risk_MCC, high_risk_merchant
  - high_risk_transactions (amount_income_ratio > threshold)
- Creates user behavior features:
  - unique_mcc_count (unique MCCs per user)
  - mcc_changed and rapid_mcc_changed (MCC switches within 1 hour)
- Validates output rows using Stage2Features (Pydantic) for a standardized schema.

Input: Stage 1 output + metadata artifact
Output: Stage 2 standardized feature table
"""

@router.post("/transformation-stage2",
             name="Step 5 - Second Stage of Data Transformation Based on extracted artifacts.",
    tags=["Training", "Inference"],
    description= STAGE2_DESCRIPTION )
async def transformation_stage2_endpoint():
    """
    Perform the second stage of data transformation on split data.
    """
    try:
        # X_train=pd.read_csv(request.x_train_path, parse_dates=["timestamp", "Acct_Open_Date", "Expires", "Date"]  )
        # X_test=pd.read_csv(request.x_test_path, parse_dates=["timestamp", "Acct_Open_Date", "Expires", "Date"] )

        db = Database()

        X_train = db.fetch_data('SELECT * FROM "X_train"')
        X_test = db.fetch_data('SELECT * FROM "X_test"')

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

        with open(METADATA_PATH, "r") as f:
            artifacts = json.load(f)

        X_train_transformed = transform_stage2(artifacts, X_train)
        X_test_transformed = transform_stage2(artifacts, X_test)

        db.store_data(X_train_transformed, "X_train_transformed_stage2")
        db.store_data(X_test_transformed, "X_test_transformed_stage2")

        # X_train_transformed.to_csv(X_TRAIN_TRANSFOMED2_PATH, index=False)
        # X_test_transformed.to_csv(X_TEST_TRANSFOMED2_PATH, index=False)

        return "Second stage transformation completed successfully. Tables saved to databse"

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
