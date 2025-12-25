from fastapi import APIRouter, HTTPException
import pandas as pd

# from pydantic import BaseModel,field_validator
# from  api._1_data_loader.load_data import load_data
# from  api._2_merge_csvs.merge_data import merge_csvs
# from pathlib import Path
from src.api._3_transformation_stage1.transformation_stage_1 import transform_stage1
from src.db.db import Database
# from src.api.router_constants import MERGED_CSV_PATH
# from src.api.router_constants import TRANSFORM_STAGE1

router = APIRouter()

# class TransformationStage1Request(BaseModel):
#     merged_csv_path: str = str(MERGED_CSV_PATH)
#     @field_validator("merged_csv_path", mode="before")
#     def check_file_exists(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".csv" and v.is_file()) :
#             raise ValueError("The CSV file is not found")
#         return str(v)
# class TransformationStage1Response(BaseModel):
#     transformation_stage1: str
#     message: str
#     @field_validator("transformation_stage1", mode="after")
#     def check_csv(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".csv" and v.is_file()) :
#             raise ValueError("The file must be a CSV")
#         return str(v)

STAGE1_DESCRIPTION = """
Stage 1 — Core Feature Engineering & Schema Validation

Transforms merged raw data into a model-ready dataset by:
- Building a full transaction timestamp and extracting time features (hour, day of week)
- Creating transaction channel feature (online=CNP vs in-person=CP)
- Engineering demographic/retirement features (age groups, retirement proximity)
- Creating income and ZIP comparison features (income tiers, mismatch indicators)
- Creating debt/credit risk features (DTI, utilization bins, FICO tiers)
- Adding synthetic fraud risk signals and ZIP mismatch checks
- Computing months-to-expiry
- Validating every row using the TransactionFeatures schema (Pydantic) for consistent output

Returns the transformed dataset in a standardized schema for both training and inference.
"""

@router.post("/transformation-stage1",
             name="Step 2 - First Stage of Data Transformation on Merged CSV files.",
    tags=["Training", "Inference"],
    description= STAGE1_DESCRIPTION
             )
async def transformation_stage1_endpoint():
    """
    Perform the first stage of data transformation on merged CSV files.
    """
    try:
        # Load the merged transaction file from database

        db = Database()

        df = db.fetch_data('SELECT * FROM "merged_data"')

        transformed_df = transform_stage1(df)
        db.store_data(transformed_df, "transformed_stage1")

        return "Stage 1 Transformation completed successfully and saved to the databse"

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
