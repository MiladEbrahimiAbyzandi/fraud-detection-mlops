import pandas as pd
from fastapi import APIRouter, HTTPException
#from pydantic import BaseModel, field_validator
#from pathlib import Path
from api._8_imbalance_correction.imbalance_correction import handle_imbalance
from api.router_constants import X_TRAIN_TRANSFOMED3_PATH, Y_TRAIN_PATH, X_TRAIN_BALANCED_PATH, Y_TRAIN_BALANCED_PATH
from db.db import Database

router = APIRouter()

# class ImbalanceCorrectionRequest(BaseModel):
#     x_train_path: str = str(X_TRAIN_TRANSFOMED3_PATH)
#     y_train_path: str = str(Y_TRAIN_PATH)

#     @field_validator("x_train_path", "y_train_path", mode="before")
#     def check_csv(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".csv" and v.is_file()):
#             raise ValueError("The file must be a CSV which already exists. please leave the X_train_path and y_train_path empty to use the default paths.")
#         return str(v)
    
# class ImbalanceCorrectionResponse(BaseModel):
#     x_train_balanced_path: str = str(X_TRAIN_BALANCED_PATH)
#     y_train_balanced_path: str = str(Y_TRAIN_BALANCED_PATH)
#     message: str
#     @field_validator("x_train_balanced_path", "y_train_balanced_path", mode="after")
#     def check_csv(cls, v: str):
#         v=Path(v)
#         if not v.suffix.lower() == ".csv":
#             raise ValueError("The file must be a CSV")
#         return str(v)

@router.post("/imbalance_correction")
async def correct_imbalance():
    """
    Endpoint to correct class imbalance in the training dataset using SMOTE.
    """
    
    try:
        # Load the datasets
        db=Database()
        X_train = db.fetch_data('SELECT * FROM "X_train_transformed_stage3"')
        y_train = db.fetch_data('SELECT * FROM "y_train"')
        # X_train = pd.read_csv(request.x_train_path)
        # y_train = pd.read_csv(request.y_train_path)

        # Perform imbalance correction
        X_train_balanced, y_train_balanced = handle_imbalance(X_train, y_train)

        # Save the balanced datasets
        X_train_balanced.to_csv(X_TRAIN_BALANCED_PATH, index=False)
        y_train_balanced.to_csv(Y_TRAIN_BALANCED_PATH, index=False)

        db.store_data(X_train_balanced,"X_train_balanced")
        db.store_data(y_train_balanced, "y_train_balanced")

        return "the training set successfully balanced and stored in database"
    except Exception as e:
        raise HTTPException(status_code=500,
                             detail=str(e))