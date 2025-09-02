from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
import joblib
import json

from .constants import DF_INFERENCE_TRANSFORMED3_PATH, INFERENCE_RESULT,MODEL_PATH

router = APIRouter()

class inferenceRequest(BaseModel):
    df_inference_transformed3_path: Path= DF_INFERENCE_TRANSFORMED3_PATH
    model_path: Path = MODEL_PATH

    @field_validator("df_inference_transformed3_path", mode="after")
    def check_csv(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("the file must be a CSV that exists from transfomation stage 3 inference")
        return v
    @field_validator("model_path", mode="after")
    def check_model(cls, v: Path):
        if not (v.suffix.lower() in [".pkl", ".joblib"] and v.is_file()):
            raise ValueError("the model file must be a .pkl or .joblib that exists")
        return v

class inferenceResponse(BaseModel):
    message: str
    inference_results_path: Path = INFERENCE_RESULT

@router.post("/inference")
async def run_inference(request: inferenceRequest) -> inferenceResponse:
    """
    Endpoint to perform inference using the trained model on the transformed inference data."""
    try:
        model=joblib.load(request.model_path)

        prediction=model.predict(request.df_inference_transformed3_path)
        prediction_proba=model.predict_proba(request.df_inference_transformed3_path)[:, 1]
        
        output={
            "predictions": prediction.tolist(),
            "predictions_proba": prediction_proba.tolist()
        }

        json.dump(output, INFERENCE_RESULT)
        
        return inferenceResponse(
            message=f"Inferece completed successfully and result saved to {INFERENCE_RESULT}", 
            inference_results_path=INFERENCE_RESULT
        )
    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))