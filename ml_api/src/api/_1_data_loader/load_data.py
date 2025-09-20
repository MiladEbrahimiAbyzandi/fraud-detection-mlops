from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from api._1_data_loader.models import Card, User, Transaction, RawData
from  api._1_data_loader.constants import CARDS_CSV_PATH, USERS_CSV_PATH, TRANSACTIONS_CSV_PATH, COLUMNS_TO_RENAME
from db.db import Database
def csv_to_pydantic_model(csv_path: str, model: BaseModel) -> list[BaseModel]:
    """
    Convert a CSV file to a pydantic model.
    """
    df = pd.read_csv(csv_path)
    df = df.rename(columns=COLUMNS_TO_RENAME)
    return [model(**row) for row in df.to_dict(orient="records")]


def load_data(cards_path : str | Path = CARDS_CSV_PATH,
              users_path :str | Path = USERS_CSV_PATH,
              transaction_path : str | Path = TRANSACTIONS_CSV_PATH) -> RawData:
    """
    Load data from a CSV file.
    """
    cards = csv_to_pydantic_model(csv_path=cards_path, model=Card)
    users = csv_to_pydantic_model(csv_path=users_path, model=User)
    transactions = csv_to_pydantic_model(csv_path=transaction_path, model=Transaction)
    return RawData(cards=cards, users=users, transactions=transactions)

def load_data_from_database(
    CardModel: BaseModel, 
    UserModel: BaseModel, 
    TransactionModel: BaseModel
) -> RawData:
    """
    Load data from the database and return as RawData.
    """
    db = Database()

    # --- Card table ---
    cards_df = db.fetch_data('SELECT * FROM "card"')
    cards_df =  cards_df.rename(columns=COLUMNS_TO_RENAME)
    cards = [CardModel(**row) for row in cards_df.to_dict(orient="records")]

    # --- User table ---
    users_df = db.fetch_data('SELECT * FROM "user"')
    users_df = users_df.rename(columns=COLUMNS_TO_RENAME)
    users = [UserModel(**row) for row in users_df.to_dict(orient="records")]

    # --- Transaction table ---
    transactions_df = db.fetch_data('SELECT * FROM "transaction"')
    transactions_df = transactions_df.rename(columns=COLUMNS_TO_RENAME)
    transactions = [TransactionModel(**row) for row in transactions_df.to_dict(orient="records")]

    return RawData(cards=cards, users=users, transactions=transactions)



    

    # cards = csv_to_pydantic_model(csv_path=cards_path, model=Card)
    # users = csv_to_pydantic_model(csv_path=users_path, model=User)
    # transactions = csv_to_pydantic_model(csv_path=transaction_path, model=Transaction)
    # return RawData(cards=cards, users=users, transactions=transactions)



if __name__ == "__main__":
    data = load_data()
    print(data)
