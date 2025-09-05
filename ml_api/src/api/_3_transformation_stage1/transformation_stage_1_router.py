from fastapi import APIRouter, HTTPException
import pandas as pd
from pydantic import BaseModel,field_validator
from  api._1_data_loader.load_data import load_data
from  api._2_merge_csvs.merge_data import merge_csvs
from pathlib import Path
from  api._3_transformation_stage1.transformation_stage_1 import transform_stage1
from api.router_constants import MERGED_CSV_PATH
from api.router_constants import TRANSFORM_STAGE1

router=APIRouter()

class TransformationStage1Request(BaseModel):
    merged_csv_path: Path = MERGED_CSV_PATH
    @field_validator("merged_csv_path", mode="before")
    def check_file_exists(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()) :
            raise ValueError("The CSV file is not found")
        return v
class TransformationStage1Response(BaseModel):
    transformation_stage1: Path
    message: str
    @field_validator("transformation_stage1", mode="after")
    def check_csv(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()) :
            raise ValueError("The file must be a CSV")
        return v
    
@router.post("/transformation-stage1", tags=["Transformation"])
async def transformation_stage1_endpoint(request: TransformationStage1Request):
    """
    Perform the first stage of data transformation on merged CSV files.
    """
    try:
        # Load the merged CSV file
        df=pd.read_csv(request.merged_csv_path)

        transformed_df=transform_stage1(df)
        transformed_df.to_csv(TRANSFORM_STAGE1, index=False)

        return TransformationStage1Response(transformation_stage1=TRANSFORM_STAGE1,
                                            message=f"Stage 1 Transformation completed successfully and saved to: {TRANSFORM_STAGE1}"
                                            )


    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= str(e)
        )
