from src.api._3_transformation_stage1.model import TransactionFeatures
import pandas as pd
from typing import Literal
from pydantic import ConfigDict


class Stage2Features(TransactionFeatures):
    high_risk_state: Literal[0, 1]
    high_risk_cities: Literal[0, 1]
    high_risk_MCC: Literal[0, 1]
    high_risk_transactions: Literal[0, 1]
    unique_mcc_count: int
    next_mcc: str | None
    mcc_changed: Literal[0, 1]
    time_diff: pd.Timedelta | None
    model_config = ConfigDict(arbitrary_types_allowed=True)
    rapid_mcc_changed: Literal[0, 1]
    high_risk_merchant: Literal[0, 1]
