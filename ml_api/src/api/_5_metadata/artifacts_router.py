from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from api._5_metadata.metadata_extractor import metadata
from pathlib import Path
import json
import pandas as pd
from api.router_constants import X_TRAIN_PATH, Y_TRAIN_PATH, METADATA_PATH

router=APIRouter()

class ArtifactsRequest(BaseModel):
    x_train_path: str = str(X_TRAIN_PATH)
    y_train_path: str = str(Y_TRAIN_PATH)

    @field_validator("x_train_path","y_train_path", mode="before")
    def check_files_exist(cls, v=str):
        v=Path(v)
        if not(v.suffix.lower()==".csv" and v.is_file()):
            raise ValueError("The CSV file is not found")
        return str(v)
    
class ArtifactsResponse(BaseModel):
    metadata: str = str(METADATA_PATH)
    message: str
    @field_validator("metadata", mode="after")
    def check_json(cls, v: str):
        v=Path(v)
        if not (v.suffix.lower() == ".json" and v.is_file()) :
            raise ValueError("The output file must be a JSON which is not found")
        return str(v)

@router.post("/artifacts")
async def get_artifacts(Request: ArtifactsRequest):
    """
    Get data artifacts in order to apply to the next levels of data transformation on the X_train dataset.
    """
    try:
        X_train= pd.read_csv(Request.x_train_path)
        y_train= pd.read_csv(Request.y_train_path)

        data_metadata=metadata(X_train, y_train)

        with open(METADATA_PATH, "w") as f:
            json.dump(data_metadata, f)

        return ArtifactsResponse(metadata=str(METADATA_PATH),
                              message=f"Metadata exctracted and saved to :{METADATA_PATH}")
        
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail= str(e)
        )


