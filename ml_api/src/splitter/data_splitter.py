import pandas as pd
import numpy as np 
from sklearn.model_selection import train_test_split

def split_data(df: pd.DataFrame, test_size=0.2, random_state=42) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        try:
            """Split data into train and test sets."""
            X = df.drop(columns=["Is_Fraud"])
            y = df["Is_Fraud"]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            print(f"Train Shape: {X_train.shape}, Test Shape: {X_test.shape}")
            
            return X_train, X_test, y_train, y_test

        except Exception as e:
            print(f"Error spliting data : {e} ")

if __name__ == "__main__":
    # Example usage
    from data_loader.load_data import load_data
    from merge_csvs.merge_data import merge_csvs
    
    data = load_data()
    df = merge_csvs(data.cards, data.users, data.transactions)
    
    X_train, X_test, y_train, y_test = split_data(df)
    
    print("Data split completed successfully.")
    print(f"Train Shape: {X_train.shape}, Test Shape: {X_test.shape}")
