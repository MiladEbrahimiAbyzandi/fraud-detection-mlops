from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
from api._7_transformation_stage3.transformation_stage3_inference import transformation_stage3_inference
from api.router_constants import ENCODER_PATH, SCALER_PATH, SELECTED_COLUMNS_PATH, INFERENCE_DATA_PATH, DF_INFERENCE_TRANSFORMED3_PATH

router=APIRouter()
class TransformationStage3InferenceRequest(BaseModel):
    inference_csv_path: Path = INFERENCE_DATA_PATH
    encoder_path: Path = ENCODER_PATH
    scaler_path: Path = SCALER_PATH
    selected_columns_path: Path = SELECTED_COLUMNS_PATH


    @field_validator("inference_csv_path", mode="before")
    def check_file_exists(cls, v: Path):
        if not(v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The CSV file for inference is not found")
        return v
    
    @field_validator("encoder_path", "scaler_path", "selected_columns_path", mode="before")
    def check_joblib_files(cls, v: Path):
        if not (v.is_file() and v.suffix.lower() ==".joblib"):
            raise ValueError("joblib files for calling encoder, scaler, or selected columns are not found")
        return v
    
class TransformationStage3InferenceResponse(BaseModel):
    message: str
    transfomation_stage_3_inference: Path 
    @field_validator("transfomation_stage_3_inference", mode="after")
    def check_csv_files(cls, v: Path):
        if not (v.is_file() and v.suffix.lower() == ".csv"):
            raise ValueError("The final transfomed CSV file for inference is not found")
        return v

@router.post("/transformation-stage3-inference", tags=["Transformation"])
async def transformation_stage3_inference_endpoint(request: TransformationStage3InferenceRequest):
    """
    Perform the third stage of data transformation on second stage transformed data for inference.
    """
    try:
        
        df=transformation_stage3_inference(
            inference_csv_path=request.inference_csv_path,
            encoder_path=request.encoder_path,
            scaler_path=request.scaler_path,
            selected_columns_path=request.selected_columns_path
        )

        df.to_csv(DF_INFERENCE_TRANSFORMED3_PATH, index=False)
        return (
            TransformationStage3InferenceResponse(
                transfomation_stage_3_inference=DF_INFERENCE_TRANSFORMED3_PATH,
                message=f"Third stage transformation for inference completed successfully. File saved to: {DF_INFERENCE_TRANSFORMED3_PATH}"
        ))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during the third stage transformation for inference: {str(e)}"
        )

    


        