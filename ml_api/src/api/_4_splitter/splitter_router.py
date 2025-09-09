from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
from api._4_splitter.data_splitter import split_data
import pandas as pd
from api.router_constants import TRANSFORM_STAGE1, X_TRAIN_PATH, X_TEST_PATH, Y_TRAIN_PATH, Y_TEST_PATH

router=APIRouter()

class SplitterRequest(BaseModel):
    transformation_stage1_path: str = str(TRANSFORM_STAGE1)
    splite_size: float = 0.2
    random_state: int = 42

    @field_validator("transformation_stage1_path", mode="before")
    def check_file_exists(cls, v: str):
        v=Path(v)
        if not(v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The file must be a CSV")
        return str(v)
    
class SplitterResponse(BaseModel):
    X_train: str
    X_test: str
    y_train: str
    y_test: str
    message: str

    @field_validator("X_train", "X_test", "y_train", "y_test", mode="after")
    def check_csv(cls, v: str):
        v=Path(v)
        if not (v.suffix.lower() == ".csv" and v.is_file()) :
            raise ValueError("The file must be a CSV")
        return str(v)


@router.post("/data-split", tags=["splitter"])
async def data_split_endpoint(request: SplitterRequest):
    """
    Split the first stage transformed data into training and testing sets.
    """
    try:
        transformed_df = pd.read_csv(request.transformation_stage1_path)

        X_train, X_test, y_train, y_test = split_data(
            transformed_df,
            test_size=request.splite_size,
            random_state=request.random_state
        )
        X_train.to_csv(X_TRAIN_PATH, index=False)
        X_test.to_csv(X_TEST_PATH, index=False)
        y_train.to_csv(Y_TRAIN_PATH, index=False)
        y_test.to_csv(Y_TEST_PATH, index=False)


        return (
            SplitterResponse(
                X_train=str(X_TRAIN_PATH),
                X_test=str(X_TEST_PATH),
                y_train=str(Y_TRAIN_PATH),
                y_test=str(Y_TEST_PATH),
                message=f"Data splitting completed successfully. Files saved to: {X_TRAIN_PATH}, {X_TEST_PATH}, {Y_TRAIN_PATH}, {Y_TEST_PATH}"
            )

        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= str(e)
        )