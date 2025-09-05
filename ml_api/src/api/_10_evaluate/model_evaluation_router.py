from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator 
from pathlib import Path
import joblib
import pandas as pd
import json
from api._10_evaluate.evaluate import evaluate
from api.router_constants import X_TEST_TRANSFORMED3_PATH, Y_TEST_PATH, MODEL_PATH, EVALUATION_METRICS_PATH


router = APIRouter()
class EvaluationRequest(BaseModel):
    x_test_path: Path = X_TEST_TRANSFORMED3_PATH
    y_test_path: Path = Y_TEST_PATH
    model_path: Path = MODEL_PATH
    @field_validator("x_test_path","y_test_path", mode="before")
    def check_csv(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The file must be a CSV")
        return v
    @field_validator("model_path", mode="after")
    def check_model(cls, v: Path):
        if not (v.suffix.lower() in [".pkl", ".joblib"] and v.is_file()):
            raise ValueError("the model file must be a .pkl or .joblib that exists")
        return v
    
class EvaluationResponse(BaseModel):
    metrics: Path
    message: str
    @field_validator("metrics", mode="after")
    def check_json(cls, v: Path):
        if not (v.suffix.lower() == ".json" and v.is_file()):
            raise ValueError("The metrics file must be a JSON")
        return v
    
@router.post("/evaluate", tags=["Evaluation"])
async def run_evaluation(request: EvaluationRequest) -> EvaluationResponse:
    """
    Endpoint to evaluate the trained model on the test dataset and save evaluation metrics."""
    try:
        X_test = pd.read_csv(request.x_test_path)
        y_test = pd.read_csv(request.y_test_path).squeeze()  # Convert DataFrame to Series if needed
        model = joblib.load(request.model_path)
        metrics = evaluate(model, X_test, y_test)

        with open(EVALUATION_METRICS_PATH, "w") as f:
            json.dump(metrics, f)

        return EvaluationResponse(
            metrics=EVALUATION_METRICS_PATH,
            message=f"Model evaluation completed successfully and metrics saved to {EVALUATION_METRICS_PATH}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))