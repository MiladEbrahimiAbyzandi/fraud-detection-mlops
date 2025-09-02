import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
from imbalance_correction.imbalance_correction import handle_imbalance
from .constants import X_TRAIN_TRANSFOMED3_PATH, Y_TRAIN_PATH, X_TRAIN_BALANCED_PATH, Y_TRAIN_BALANCED_PATH


router = APIRouter()

class ImbalanceCorrectionRequest(BaseModel):
    x_train_path: Path = X_TRAIN_TRANSFOMED3_PATH
    y_train_path: Path = Y_TRAIN_PATH

    @field_validator("x_train_path", "y_train_path", mode="before")
    def check_csv(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The file must be a CSV which already exists. please leave the X_train_path and y_train_path empty to use the default paths.")
        return v
    
class ImbalanceCorrectionResponse(BaseModel):
    x_train_balanced_path: Path = X_TRAIN_BALANCED_PATH
    y_train_balanced_path: Path = Y_TRAIN_BALANCED_PATH
    message: str
    @field_validator("x_train_balanced_path", "y_train_balanced_path", mode="after")
    def check_csv(cls, v: Path):
        if not v.suffix.lower() == ".csv":
            raise ValueError("The file must be a CSV")
        return v

@router.post("/imbalance_correction")
async def correct_imbalance(request: ImbalanceCorrectionRequest) -> ImbalanceCorrectionResponse:
    """
    Endpoint to correct class imbalance in the training dataset using SMOTE.
    """
    
    try:
        # Load the datasets
        X_train = pd.read_csv(request.x_train_path)
        y_train = pd.read_csv(request.y_train_path)

        # Perform imbalance correction
        X_train_balanced, y_train_balanced = handle_imbalance(X_train, y_train)

        # Save the balanced datasets
        X_train_balanced.to_csv(X_TRAIN_BALANCED_PATH, index=False)
        y_train_balanced.to_csv(Y_TRAIN_BALANCED_PATH, index=False)

        return ImbalanceCorrectionResponse(
            x_train_balanced_path=X_TRAIN_BALANCED_PATH,
            y_train_balanced_path=Y_TRAIN_BALANCED_PATH,
            message=f"Imbalance correction completed successfully, and balanced datasets are saved to: {X_TRAIN_BALANCED_PATH} and {Y_TRAIN_BALANCED_PATH}"
        )
    except Exception as e:
        raise HTTPException(status_code=500,
                             detail=str(e))