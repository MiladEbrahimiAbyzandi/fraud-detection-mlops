import pandas as pd
from fastapi import APIRouter, HTTPException

# from pydantic import BaseModel, field_validator
# from pathlib import Path
from src.api._4_splitter.data_splitter import split_data
from src.db.db import Database

# from src.api.router_constants import TRANSFORM_STAGE1, X_TRAIN_PATH, X_TEST_PATH, Y_TRAIN_PATH, Y_TEST_PATH

router = APIRouter()

# class SplitterRequest(BaseModel):
#     transformation_stage1_path: str = str(TRANSFORM_STAGE1)
#     splite_size: float = 0.2
#     random_state: int = 42

#     @field_validator("transformation_stage1_path", mode="before")
#     def check_file_exists(cls, v: str):
#         v=Path(v)
#         if not(v.suffix.lower() == ".csv" and v.is_file()):
#             raise ValueError("The file must be a CSV")
#         return str(v)

# class SplitterResponse(BaseModel):
#     X_train: str
#     X_test: str
#     y_train: str
#     y_test: str
#     message: str

#     @field_validator("X_train", "X_test", "y_train", "y_test", mode="after")
#     def check_csv(cls, v: str):
#         v=Path(v)
#         if not (v.suffix.lower() == ".csv" and v.is_file()) :
#             raise ValueError("The file must be a CSV")
#         return str(v)

SPLITTER_DESCRIPTION = """
Split Dataset (Train/Test)

Splits the prepared dataset into training and test sets using `Is_Fraud` as the target label.
The split is stratified to preserve the fraud/non-fraud class distribution in both subsets,
which is critical for imbalanced fraud detection data.

Outputs: X_train, X_test, y_train, y_test
Parameters: test_size (default=0.2), random_state (default=42)
"""

@router.post("/data-split",
             name="Step 3 - Split the first stage transformed data into training and testing sets.",
    tags=["Training"],
    description = SPLITTER_DESCRIPTION)
async def data_split_endpoint(split_size: float = 0.2, random_state: int = 42):
    """
    Split the first stage transformed data into training and testing sets.
    """
    try:
        db = Database()
        # transformed_df = pd.read_csv(request.transformation_stage1_path)
        transformed_df = db.fetch_data('SELECT * FROM "transformed_stage1"')

        X_train, X_test, y_train, y_test = split_data(transformed_df)
        # X_train.to_csv(X_TRAIN_PATH, index=False)
        # X_test.to_csv(X_TEST_PATH, index=False)
        # y_train.to_csv(Y_TRAIN_PATH, index=False)
        # y_test.to_csv(Y_TEST_PATH, index=False)
        db.store_data(X_train, "X_train")
        db.store_data(X_test, "X_test")
        db.store_data(y_test, "y_test")
        db.store_data(y_train, "y_train")

        return "Data splitting completed successfully. Files saved to databse"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
