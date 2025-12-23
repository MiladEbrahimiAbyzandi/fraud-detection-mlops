from sqlalchemy import create_engine
import pandas as pd
import os


class Database:
    def __init__(self):
        self.DATABASE_URL = "postgresql://neondb_owner:npg_LFzuUHeI8w5s@ep-royal-leaf-a8q3yo6t-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"
        self.engine = create_engine(self.DATABASE_URL, pool_pre_ping=True)

    def fetch_data(self, query: str) -> pd.DataFrame:
        """read from Postgres using SQL query and return pandas DataFrame"""
        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df

    def store_data(self, df: pd.DataFrame, table_name: str):
        """save data into Postgres table"""
        with self.engine.connect() as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
