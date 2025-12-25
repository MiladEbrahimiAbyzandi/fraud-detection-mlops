from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from src.api._5_metadata.metadata_extractor import metadata
from pathlib import Path
import json
import pandas as pd
from src.api.router_constants import X_TRAIN_PATH, Y_TRAIN_PATH, METADATA_PATH
from src.db.db import Database

router = APIRouter()

# class ArtifactsRequest(BaseModel):
#     x_train_path: str = str(X_TRAIN_PATH)
#     y_train_path: str = str(Y_TRAIN_PATH)

#     @field_validator("x_train_path","y_train_path", mode="before")
#     def check_files_exist(cls, v=str):
#         v=Path(v)
#         if not(v.suffix.lower()==".csv" and v.is_file()):
#             raise ValueError("The CSV file is not found")
#         return str(v)


class ArtifactsResponse(BaseModel):
    metadata: str = str(METADATA_PATH)
    message: str

    @field_validator("metadata", mode="after")
    def check_json(cls, v: str):
        v = Path(v)
        if not (v.suffix.lower() == ".json" and v.is_file()):
            raise ValueError("The output file must be a JSON which is not found")
        return str(v)

METADATA_DESCRIPTION = """
Metadata Extraction (Training Only)

Extracts reusable training metadata to be saved as an artifact and reused during inference
(without recalculating on unseen data).

This step:
- Uses X_train + y_train (prevents data leakage)
- Computes high-risk state and city lists from card-present (CP) transactions
  based on fraud rates above the overall training fraud rate
- Identifies high-risk MCC codes (fraud rate above overall baseline)
- Identifies high-risk merchants (>= 20 transactions AND fraud_rate > 0.10)
- Computes a 99th percentile threshold for amount_income_ratio = Amount / Yearly_Income_Person

Returns a JSON dictionary:
{high_risk_states, high_risk_cities, high_risk_mcc, high_risk_merchants, threshold}.
"""

@router.post("/artifacts",
             name="Step 4 - Extract data artifacts for next transformation stages.",
    tags=["Training"],
    description= METADATA_DESCRIPTION )
async def get_artifacts():
    """
    Extract data artifacts in order to apply to the next levels of data transformation on the X_train dataset.
    """
    try:
        db = Database()

        # X_train= pd.read_csv(Request.x_train_path)
        # y_train= pd.read_csv(Request.y_train_path)
        X_train = db.fetch_data('SELECT * FROM "X_train"')
        y_train = db.fetch_data('SELECT * FROM "y_train"')

        # data_metadata=metadata(X_train, y_train)

        data_metadata = metadata(X_train, y_train)

        with open(METADATA_PATH, "w") as f:
            json.dump(data_metadata, f)

        return ArtifactsResponse(
            metadata=str(METADATA_PATH), message=f"Metadata exctracted and saved to :{METADATA_PATH}"
        )

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
