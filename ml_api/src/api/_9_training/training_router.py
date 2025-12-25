from fastapi import APIRouter, HTTPException

# from pydantic import BaseModel, field_validator
# from pathlib import Path
from src.api._9_training.training import train

# import pandas as pd
import joblib
from src.api.router_constants import X_TRAIN_BALANCED_PATH, Y_TRAIN_BALANCED_PATH, MODEL_PATH
from src.db.db import Database
from typing import Literal

TRAINING_DESCRIPTION = """
Model Training — XGBoost or Random Forest

Trains a fraud detection model using the prepared training data (X_train, y_train).
Supported models:
- 'xgboost' (XGBClassifier)
- 'randomforest' (RandomForestClassifier)

This step also cleans feature column names (removes special characters like [ ] < >)
to ensure compatibility with model libraries (especially XGBoost).

Returns: a fitted model object.
"""
router = APIRouter()

# class TrainingRequest(BaseModel):
#     x_train_path: str = str(X_TRAIN_BALANCED_PATH)
#     y_train_path: str = str(Y_TRAIN_BALANCED_PATH)
#     model_name: str = "xgboost"

#     @field_validator("x_train_path", mode="before")
#     def check_x_train_csv(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".csv" and v.is_file()):
#             raise ValueError("The balanced X_train file must be a CSV")
#         return str(v)

#     @field_validator("y_train_path", mode="after")
#     def check_y_train_csv(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".csv" and v.is_file()):
#             raise ValueError("The balanced y_train file must be a CSV")
#         return str(v)

#     @field_validator("model_name", mode="after")
#     def check_model_name(cls, v: str):
#         v=v.lower()
#         if v not in ["xgboost", "randomforest"]:
#             raise ValueError("Invalid model name. Choose 'xgboost' or 'randomforest'.")
#         return v

# class TrainingResponse(BaseModel):
#     message: str
#     model_path: str

#     @field_validator("model_path", mode="after")
#     def check_model_path(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() in [".pkl", ".joblib"] and v.is_file()):
#             raise ValueError("the model file must be a .pkl or .joblib that exists")
#         return str(v)


@router.post("/train",
             name="Step 9 - Train a machine learning model using the balanced training dataset.",
    tags=["Training"],
    description= TRAINING_DESCRIPTION
             )

async def run_training(model_name: Literal["xgboost", "randomforest"]):
    """
    Endpoint to train a machine learning model using the balanced training dataset."""
    try:
        db = Database()
        # X_train = pd.read_csv(request.x_train_path)
        # y_train = pd.read_csv(request.y_train_path).squeeze()  # Convert DataFrame to Series if needed

        X_train = db.fetch_data('SELECT * FROM "X_train_balanced"')
        y_train = db.fetch_data('SELECT * FROM "y_train_balanced"')

        model = train(X_train, y_train, model_name=model_name)

        # TODO
        # Save the model in Google Cloud Storage

        with open(MODEL_PATH, "wb") as f:
            joblib.dump(model, f)

        return f"Model {model_name} trained and saved succesfully"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
