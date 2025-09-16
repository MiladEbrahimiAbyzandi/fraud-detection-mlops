from fastapi import APIRouter,HTTPException
from pydantic import BaseModel, field_validator,Field
from pathlib import Path
from  api._1_data_loader.load_data import load_data
from  api._2_merge_csvs.merge_data import merge_csvs
from  api.router_constants import MERGED_CSV_PATH,CARDS_PATH,USERS_PATH,TRANSACTIONS_PATH
router=APIRouter()

#----request and response models----
class MergeCSVRequest(BaseModel):
    cards_path: str = Field(default=str(CARDS_PATH))
    users_path: str = Field(default=str(USERS_PATH))
    transaction_path: str = Field(default=str(TRANSACTIONS_PATH))
    @field_validator("cards_path", "users_path", "transaction_path", mode="before")
    def check_csv(cls, v: str):
        path=Path(v)
        if not (path.suffix.lower() == ".csv" and path.is_file()):
            raise ValueError("The file must be a CSV which already exists. please leave the paths empty to use the default paths.")
        return str(path)
    
class MergeCSVResponse(BaseModel):
    cards_count: int
    users_count: int
    transactions_count: int
    csv_path: str
    message: str

    @field_validator("csv_path", mode="after")
    def check_path(cls, v: str):
        path=Path(v)
        if not (path.suffix.lower() == ".csv" and path.is_file()):
            raise ValueError("The merged csv file does not exist")
        return str(path)


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
            csv_path=str(MERGED_CSV_PATH),
            message=f"The merged CSV file is saved in: {MERGED_CSV_PATH}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= str(e)
        )

    
    




