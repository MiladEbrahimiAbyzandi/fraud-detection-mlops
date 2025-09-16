from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
from api._7_transformation_stage3.transformation_stage3_inference import transformation_stage3_inference
from api.router_constants import ENCODER_PATH, SCALER_PATH, SELECTED_COLUMNS_PATH, X_TEST_TRANSFOMED2_PATH, DF_INFERENCE_TRANSFORMED3_PATH
import pandas as pd
import joblib

router=APIRouter()
class TransformationStage3InferenceRequest(BaseModel):
    inference_csv_path: str = str(X_TEST_TRANSFOMED2_PATH)
    encoder_path: str = str(ENCODER_PATH)
    scaler_path: str = str(SCALER_PATH)
    selected_columns_path: str = str(SELECTED_COLUMNS_PATH)


    @field_validator("inference_csv_path", mode="before")
    def check_file_exists(cls, v: str):
        v=Path(v)
        if not(v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The CSV file for inference is not found")
        return str(v)
    
    @field_validator("encoder_path", "scaler_path", "selected_columns_path", mode="before")
    def check_joblib_files(cls, v: str):
        v=Path(v)
        if not (v.is_file() and v.suffix.lower() ==".joblib"):
            raise ValueError("joblib files for calling encoder, scaler, or selected columns are not found")
        return str(v)
    
class TransformationStage3InferenceResponse(BaseModel):
    message: str
    transfomation_stage_3_inference: str
    @field_validator("transfomation_stage_3_inference", mode="after")
    def check_csv_files(cls, v: str):
        v=Path(v)
        if not (v.is_file() and v.suffix.lower() == ".csv"):
            raise ValueError("The final transfomed CSV file for inference is not found")
        return str(v)

@router.post("/transformation-stage3-inference")
async def transformation_stage3_inference_endpoint(request: TransformationStage3InferenceRequest):
    """
    Perform the third stage of data transformation on second stage transformed data for inference.
    """
    try:
        # Load objects
        df = pd.read_csv(request.inference_csv_path)
        encoder = joblib.load(request.encoder_path)
        scaler = joblib.load(request.scaler_path)
        selected_columns = joblib.load(request.selected_columns_path)

        df=transformation_stage3_inference(
            df=df,
            encoder=encoder,
            scaler=scaler,
            selected_columns=selected_columns
        )

        df.to_csv(DF_INFERENCE_TRANSFORMED3_PATH, index=False)
        return (
            TransformationStage3InferenceResponse(
                transfomation_stage_3_inference=str(DF_INFERENCE_TRANSFORMED3_PATH),
                message=f"Third stage transformation for inference completed successfully. File saved to: {DF_INFERENCE_TRANSFORMED3_PATH}"
        ))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during the third stage transformation for inference: {str(e)}"
        )

    


        