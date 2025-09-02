from fastapi import APIRouter,HTTPException
from pydantic import BaseModel, field_validator
from pathlib import Path
from data_loader.load_data import load_data
from merge_csvs.merge_data import merge_csvs
from .constants import MERGED_CSV_PATH,CARDS_PATH,USERS_PATH,TRANSACTIONS_PATH
router=APIRouter()

#----request and response models----
class MergeCSVRequest(BaseModel):
    cards_path:  Path = CARDS_PATH
    users_path: Path =  USERS_PATH
    transaction_path: Path = TRANSACTIONS_PATH
    @field_validator("cards_path", "users_path", "transaction_path", mode="before")
    def check_csv(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The file must be a CSV which already exists. please leave the paths empty to use the default paths.")
        return v
    
class MergeCSVResponse(BaseModel):
    cards_count: int
    users_count: int
    transactions_count: int
    csv_path: Path
    message: str

    @field_validator("csv_path", mode="after")
    def check_path(cls, v: Path):
        if not (v.suffix.lower() == ".csv" and v.is_file()):
            raise ValueError("The merged csv file does not exist")
        return v


@router.post("/merge-csv")
async def merge_csv_endpoint(request: MergeCSVRequest):
    """
    Load data and Merge three CSV files and return the counts of cards, users, transactions and save the merged csv file.
    """
    try:
        data= load_data(
            cards_path=request.cards_path,
            users_path=request.users_path,
            transaction_path=request.transaction_path
        )

        merged_df=merge_csvs(data.cards, data.users, data.transactions)
        merged_df.to_csv(MERGED_CSV_PATH, index=False)

        return MergeCSVResponse(
            cards_count=len(data.cards),
            users_count=len(data.users),
            transactions_count=len(data.transactions),
            csv_path=MERGED_CSV_PATH,
            message=f"The merged CSV file is saved in: {MERGED_CSV_PATH}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= str(e)
        )

    
    




