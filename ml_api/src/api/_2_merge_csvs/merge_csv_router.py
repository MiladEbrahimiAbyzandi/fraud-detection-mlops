from fastapi import APIRouter, HTTPException

# from pydantic import BaseModel, field_validator,Field
# from pathlib import Path
# from  api._1_data_loader.load_data import load_data
from src.api._1_data_loader.load_data import load_data_from_database
from src.api._1_data_loader.models import Card, Transaction, User
from src.api._2_merge_csvs.merge_data import merge_csvs

from src.db.db import Database
# from  api.router_constants import MERGED_CSV_PATH,CARDS_PATH,USERS_PATH,TRANSACTIONS_PATH

router = APIRouter()

# ----request and response models----
# class MergeCSVRequest(BaseModel):
#     cards_path: str = Field(default=str(CARDS_PATH))
#     users_path: str = Field(default=str(USERS_PATH))
#     transaction_path: str = Field(default=str(TRANSACTIONS_PATH))
#     @field_validator("cards_path", "users_path", "transaction_path", mode="before")
#     def check_csv(cls, v: str):
#         path=Path(v)
#         if not (path.suffix.lower() == ".csv" and path.is_file()):
#             raise ValueError("The file must be a CSV which already exists. please leave the paths empty to use the default paths.")
#         return str(path)

# class MergeCSVResponse(BaseModel):
#     cards_count: int
#     users_count: int
#     transactions_count: int
#     csv_path: str
#     message: str

#     @field_validator("csv_path", mode="after")
#     def check_path(cls, v: str):
#         path=Path(v)
#         if not (path.suffix.lower() == ".csv" and path.is_file()):
#             raise ValueError("The merged csv file does not exist")
#         return str(path)
MERGE_CSV_DESCRIPTION_MARKDOWN = """
### Merge CSVs
Step 1 - Load data and Merge three CSV files and return the counts of cards, users, transactions and save the merged csv file.
"""


@router.post(
    "/merge-csv",
    name="Step 1 - Load data and Merge three CSV files and return the counts of cards, users, transactions and save the merged csv file.",
    description=MERGE_CSV_DESCRIPTION_MARKDOWN,
)
async def merge_csv_endpoint():
    """
    Load data and Merge three CSV files and return the counts of cards, users, transactions and save the merged csv file.
    """
    try:
        db = Database()

        data = load_data_from_database(Card, User, Transaction)
        merged_df = merge_csvs(data.cards, data.users, data.transactions)

        db.store_data(merged_df, "merged_data")

        return "the merged transaction dataset successfully loaded to the databse"

        # merged_df.to_csv(MERGED_CSV_PATH, index=False)

        # return MergeCSVResponse(
        #     cards_count=len(data.cards),
        #     users_count=len(data.users),
        #     transactions_count=len(data.transactions),
        #     csv_path=str(MERGED_CSV_PATH),
        #     message=f"The merged CSV file is saved in: {MERGED_CSV_PATH}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
