from pydantic import BaseModel
import pandas as pd
from data_loader.models import Card, User, Transaction, RawData
from data_loader.constants import CARDS_CSV_PATH, USERS_CSV_PATH, TRANSACTIONS_CSV_PATH, COLUMNS_TO_RENAME


def csv_to_pydantic_model(csv_path: str, model: BaseModel) -> list[BaseModel]:
    """
    Convert a CSV file to a pydantic model.
    """
    df = pd.read_csv(csv_path)
    df = df.rename(columns=COLUMNS_TO_RENAME)
    return [model(**row) for row in df.to_dict(orient="records")]


def load_data() -> RawData:
    """
    Load data from a CSV file.
    """
    cards = csv_to_pydantic_model(csv_path=CARDS_CSV_PATH, model=Card)
    users = csv_to_pydantic_model(csv_path=USERS_CSV_PATH, model=User)
    transactions = csv_to_pydantic_model(csv_path=TRANSACTIONS_CSV_PATH, model=Transaction)
    return RawData(cards=cards, users=users, transactions=transactions)


if __name__ == "__main__":
    data = load_data()
    print(data)
