import pandas as pd
import logging
from src.db.db import Database
from src.api.router_constants import CARDS_PATH, USERS_PATH, TRANSACTIONS_PATH

logging.basicConfig(level=logging.INFO)

database = Database()

card = pd.read_csv(CARDS_PATH)
user = pd.read_csv(USERS_PATH)
transaction = pd.read_csv(TRANSACTIONS_PATH)

database.store_data(card, "card")
database.store_data(user, "user")
database.store_data(transaction, "transaction")

logging.info("raw datasets are successfully stored in database")
