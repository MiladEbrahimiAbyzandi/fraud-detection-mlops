from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
from api._9_training.training import train
import pandas as pd
import joblib
from api.router_constants import X_TRAIN_BALANCED_PATH, Y_TRAIN_BALANCED_PATH, MODEL_PATH

router = APIRouter()

class TrainingRequest(BaseModel):
    x_train_path: str = str(X_TRAIN_BALANCED_PATH)
    y_train_path: str = str(Y_TRAIN_BALANCED_PATH)
    model_name: str = "xgboost"

    @field_validator("x_train_path", mode="before")
    def check_x_train_csv(cls, v: str):
        v=Path(v)
        if not (v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The balanced X_train file must be a CSV")
        return str(v)

    @field_validator("y_train_path", mode="after")
    def check_y_train_csv(cls, v: str):
        v=Path(v)
        if not (v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The balanced y_train file must be a CSV")
        return str(v)

    @field_validator("model_name", mode="after")
    def check_model_name(cls, v: str):
        v=v.lower()
        if v not in ["xgboost", "randomforest"]:
            raise ValueError("Invalid model name. Choose 'xgboost' or 'randomforest'.")
        return v
    
class TrainingResponse(BaseModel):
    message: str
    model_path: str 

    @field_validator("model_path", mode="after")
    def check_model_path(cls, v: str):
        v=Path(v)
        if not (v.suffix.lower() in [".pkl", ".joblib"] and v.is_file()):
            raise ValueError("the model file must be a .pkl or .joblib that exists")
        return str(v)

@router.post("/train", tags=["Training"])
async def run_training(request: TrainingRequest) -> TrainingResponse:
    """
    Endpoint to train a machine learning model using the balanced training dataset."""
    try:
        X_train = pd.read_csv(request.x_train_path)
        y_train = pd.read_csv(request.y_train_path).squeeze()  # Convert DataFrame to Series if needed

        model = train(X_train, y_train, model_name=request.model_name)

        with open(MODEL_PATH, "wb") as f:
            joblib.dump(model,f)

        return TrainingResponse(
            message=f"Model trained and saved to {MODEL_PATH}",
            model_path=str(MODEL_PATH)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))