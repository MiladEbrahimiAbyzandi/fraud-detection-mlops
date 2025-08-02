from pydantic import BaseModel, field_validator
from typing import Literal
from datetime import datetime
import pandas as pd

class TransactionFeatures(BaseModel):
    timestamp : datetime
    transaction_hour: int | None
    Date: datetime
    day_of_week: str | None
    transaction_type: Literal["CNP", "CP"] | None
    age_group: Literal["<20", "20-30", "30-40", "40-50", "50-60", "60-70", "70+"] | None
    is_retired: Literal[0,1] | None
    years_to_retirement: float | None
    retirement_proximity: Literal["0-5", "5-10", "10-20", "20-inf"] | None
    years_since_retirement: float | None
    retirement_phase: Literal["0-5", "5-10", "10-20", "20-inf"] | None
    
    zip_income_tier: Literal["Very Low", "Low", "Medium", "High", "Very High"] | None
    income_tier: Literal["<25K", "25K-50K", "50K-100K", "100K-250K", "250K+"] | None
    amount_income_ratio: float | None
    income_relative_to_zip: float | None
    income_mismatch: Literal["<50%", "50-80%", "80-120%", "120-200%", ">200%"] | None

    debt_to_income: float | None
    high_debt_ratio: int | None
    high_debt_high_spend: int | None

    credit_utilization: float | None
    credit_util_bin: Literal["Very Low", "Low", "Medium", "High", "Maxed Out"] | None

    fico_tier: Literal[
        "Poor (<580)",
        "Fair (580-669)",
        "Good (670-739)",
        "Very Good (740-799)",
        "Exceptional (800+)",
    ] | None
    low_FICO_high_spend: Literal[0,1] | None
    low_FICO_high_DTI: Literal[0,1] | None

    account_tenure_years: float | None
    synthetic_risk:  Literal[0,1] | None
    synthetic_risk_2:  Literal[0,1] | None

    is_us_zip: bool | None
    zip_mismatch_flag: int | None

    months_to_expiry: float | None

    @field_validator("*", mode="before")
    def convert_nan_to_none(cls, v):
        if pd.isna(v):
            return None
        return v