from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
import joblib
import pandas as pd
import json
from src.api._10_evaluate.evaluate import evaluate
from src.api.router_constants import X_TEST_TRANSFORMED3_PATH, Y_TEST_PATH, MODEL_PATH, EVALUATION_METRICS_PATH
from src.db.db import Database

router = APIRouter()
# class EvaluationRequest(BaseModel):
#     x_test_path: str = str(X_TEST_TRANSFORMED3_PATH)
#     y_test_path: str = str(Y_TEST_PATH)
#     model_path: str = str(MODEL_PATH)
#     @field_validator("x_test_path","y_test_path", mode="before")
#     def check_csv(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".csv" and v.is_file()):
#             raise ValueError("The file must be a CSV")
#         return str(v)
#     @field_validator("model_path", mode="after")
#     def check_model(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() in [".pkl", ".joblib"] and v.is_file()):
#             raise ValueError("the model file must be a .pkl or .joblib that exists")
#         return str(v)

# class EvaluationResponse(BaseModel):
#     metrics: str = str(EVALUATION_METRICS_PATH)
#     message: str
#     @field_validator("metrics", mode="after")
#     def check_json(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".json" and v.is_file()):
#             raise ValueError("The metrics file must be a JSON")
#         return str(v)


@router.post("/evaluate")
async def run_evaluation():
    """
    Endpoint to evaluate the trained model on the test dataset and save evaluation metrics."""
    try:
        db = Database()
        # X_test = pd.read_csv(request.x_test_path)
        # y_test = pd.read_csv(request.y_test_path).squeeze()  # Convert DataFrame to Series if needed
        X_test = db.fetch_data('SELECT * FROM "X_test_transformed_stage3"')
        y_test = db.fetch_data('SELECT * FROM "y_test"')

        model = joblib.load(MODEL_PATH)
        metrics = evaluate(model, X_test, y_test)

        with open(EVALUATION_METRICS_PATH, "w") as f:
            json.dump(metrics, f)

        return {
            "message": f"Model evaluation completed successfully and metrics saved to {EVALUATION_METRICS_PATH}",
            "metrics": metrics,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
