from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
from training.training import train
import pandas as pd
import joblib


from .constants import X_TRAIN_BALANCED_PATH, Y_TRAIN_BALANCED_PATH, MODEL_PATH

router = APIRouter()

class TrainingRequest(BaseModel):
    x_train_path: Path = X_TRAIN_BALANCED_PATH
    y_train_path: Path = Y_TRAIN_BALANCED_PATH
    model_name: str = "xgboost"

    @field_validator("x_train_path", mode="before")
    def check_x_train_csv(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The balanced X_train file must be a CSV")
        return v

    @field_validator("y_train_path", mode="after")
    def check_y_train_csv(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The balanced y_train file must be a CSV")
        return v

    @field_validator("model_name", mode="after")
    def check_model_name(cls, v: str):
        if v not in ["xgboost", "randomforest"]:
            raise ValueError("Invalid model name. Choose 'xgboost' or 'randomforest'.")
        return v
    
class TrainingResponse(BaseModel):
    message: str
    model_path: Path = MODEL_PATH

    @field_validator("model_path", mode="after")
    def check_model_path(cls, v: Path):
        if not (v.suffix.lower() in [".pkl", ".joblib"] and v.is_file()):
            raise ValueError("the model file must be a .pkl or .joblib that exists")
        return v

@router.post("/train", tags=["Training"])
async def run_training(request: TrainingRequest) -> TrainingResponse:
    """
    Endpoint to train a machine learning model using the balanced training dataset."""
    try:
        X_train = pd.read_csv(request.x_train_path)
        y_train = pd.read_csv(request.y_train_path).squeeze()  # Convert DataFrame to Series if needed

        model = train(X_train, y_train, model_name=request.model_name)
        joblib.dump(model, MODEL_PATH)

        return TrainingResponse(
            message=f"Model trained and saved to {MODEL_PATH}",
            model_path=MODEL_PATH
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))