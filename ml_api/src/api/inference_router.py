from fastapi import APIRouter, HTTPException

# from pydantic import BaseModel, field_validator
from pathlib import Path
import joblib
import json
import pandas as pd
from src.db.db import Database

from .router_constants import DF_INFERENCE_TRANSFORMED3_PATH, INFERENCE_RESULT, MODEL_PATH

router = APIRouter()

# class inferenceRequest(BaseModel):
#     df_inference_transformed3_path: str= str(DF_INFERENCE_TRANSFORMED3_PATH)
#     model_path: str = str(MODEL_PATH)

#     @field_validator("df_inference_transformed3_path", mode="after")
#     def check_csv(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".csv" and v.is_file()):
#             raise ValueError("the file must be a CSV that exists from transfomation stage 3 inference")
#         return str(v)
#     @field_validator("model_path", mode="after")
#     def check_model(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() in [".pkl", ".joblib"] and v.is_file()):
#             raise ValueError("the model file must be a .pkl or .joblib that exists")
#         return str(v)

# class inferenceResponse(BaseModel):
#     message: str
#     inference_results_path: str = str(INFERENCE_RESULT)


@router.post("/inference")
async def run_inference():
    """
    Endpoint to perform inference using the trained model on the transformed inference data."""
    try:
        db = Database()
        model = joblib.load(MODEL_PATH)
        # df=pd.read_csv(request.df_inference_transformed3_path)
        df = db.fetch_data('SELECT * FROM "transformed_inference_data_stage3"')
        prediction = model.predict(df)
        prediction_proba = model.predict_proba(df)[:, 1]

        output = {"predictions": prediction.tolist(), "predictions_proba": prediction_proba.tolist()}

        with open(INFERENCE_RESULT, "w") as f:
            json.dump(output, f)

        return (f"Inferece completed successfully and result saved to {INFERENCE_RESULT}",)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
