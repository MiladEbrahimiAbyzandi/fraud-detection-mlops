import json
import joblib
import pandas as pd
from typing import Any
from pathlib import Path
def save_json(data:dict, filepath:str | Path) -> None:
    """ Save a dictionary as a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data,f,indent=4)

def load_json(filepath:str | Path) -> dict:
    """ Load a dictionary from a JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def save_joblib(obj: Any , filepath:str | Path) -> None:
    """ Save a model or any object using joblib."""
    joblib.dump(obj, filepath)

def load_joblib(filepath:str | Path) -> Any:
    """ Load a model or any object using joblib."""
    return joblib.load(filepath)

def save_csv(df: pd.DataFrame, filepath: str | Path) -> None:
    """ Save a DataFrame as a CSV file."""
    df.to_csv(filepath, index=False)

def load_csv(filepath: str | Path) -> pd.DataFrame:
    """ Load a DataFrame from a CSV file."""
    return pd.read_csv(filepath)
