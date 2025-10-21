import pandas as pd
import numpy as np
from src.api._3_transformation_stage1.model import TransactionFeatures


def transform_stage1(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform first stage of data transformation and feature engineering
    Return pandas dataframe
    """

    # Convert categorical columns to category type
    categorical_cols = [
        "Card_Type",
        "Gender",
        "Card_Brand",
        "Use_Chip",
        "Has_Chip",
        "Card_on_Dark_Web",
    ]
    for col in categorical_cols:
        df[col] = df[col].astype("category")

    # Create timestamp
    df["datetime_str"] = (
        df["Year"].astype(str)
        + "-"
        + df["Month"].astype(str).str.zfill(2)
        + "-"
        + df["Day"].astype(str).str.zfill(2)
        + " "
        + df["Time"]
    )
    df["timestamp"] = pd.to_datetime(df["datetime_str"], format="%Y-%m-%d %H:%M")
    df.drop(["datetime_str"], axis=1, inplace=True)

    # Transaction Hour
    df["transaction_hour"] = pd.to_datetime(df["Time"], format="%H:%M").dt.hour

    #  Date and Day of Week
    df["Date"] = pd.to_datetime(
        df[["Year", "Month", "Day"]].astype(str).agg("-".join, axis=1),
        errors="coerce",
    )
    df["day_of_week"] = df["Date"].dt.day_name()

    # Transaction Type
    df["transaction_type"] = df["Merchant_City"].apply(lambda x: "CNP" if x.strip().lower() == "online" else "CP")

    # Age-related features
    df["age_group"] = pd.cut(
        df["Current_Age"],
        bins=[0, 20, 30, 40, 50, 60, 70, 110],
        labels=["<20", "20-30", "30-40", "40-50", "50-60", "60-70", "70+"],
    )
    df["is_retired"] = (df["Retirement_Age"] <= df["Current_Age"]).astype(int)
    df["years_to_retirement"] = np.where(
        df["is_retired"] == 0,
        df["Retirement_Age"] - df["Current_Age"],
        np.nan,
    )
    df["retirement_proximity"] = pd.cut(
        df["years_to_retirement"],
        bins=[0, 5, 10, 20, np.inf],
        labels=["0-5", "5-10", "10-20", "20-inf"],
    )
    df["years_since_retirement"] = np.where(
        df["is_retired"] == 1,
        -df["Retirement_Age"] + df["Current_Age"],
        np.nan,
    )
    df["retirement_phase"] = pd.cut(
        df["years_since_retirement"],
        bins=[0, 5, 10, 20, np.inf],
        labels=["0-5", "5-10", "10-20", "20-inf"],
    )

    # Income and zip tiers
    df["zip_income_tier"] = pd.cut(
        df["Per_Capita_Income_Zipcode"],
        bins=[0, 30000, 60000, 100000, 200000, np.inf],
        labels=["Very Low", "Low", "Medium", "High", "Very High"],
    )
    df["income_tier"] = pd.cut(
        df["Yearly_Income_Person"],
        bins=[0, 25000, 50000, 100000, 250000, np.inf],
        labels=["<25K", "25K-50K", "50K-100K", "100K-250K", "250K+"],
    )
    df["amount_income_ratio"] = np.where(
        df["Yearly_Income_Person"].notna() & (df["Yearly_Income_Person"] != 0),
        df["Amount"] / df["Yearly_Income_Person"],
        np.nan,
    )
    df["income_relative_to_zip"] = np.where(
        df["Per_Capita_Income_Zipcode"].notna() & (df["Per_Capita_Income_Zipcode"] != 0),
        df["Yearly_Income_Person"] / df["Per_Capita_Income_Zipcode"],
        0,
    )

    df["income_mismatch"] = pd.cut(
        df["income_relative_to_zip"],
        bins=[0, 0.5, 0.8, 1.2, 2, np.inf],
        labels=["<50%", "50-80%", "80-120%", "120-200%", ">200%"],
    )

    # --------------------
    df["debt_to_income"] = np.where(
        df["Yearly_Income_Person"].notna() & (df["Yearly_Income_Person"] != 0),
        df["Total_Debt"] / df["Yearly_Income_Person"],
        np.nan,
    )

    df["high_debt_ratio"] = np.where(df["debt_to_income"] > 2 & (df["debt_to_income"].notna()), 1, 0)
    df["high_debt_high_spend"] = (
        (df["Total_Debt"] > 0.5 * df["Yearly_Income_Person"]) & (df["Amount"] > 0.1 * df["Yearly_Income_Person"])
    ).astype(int)
    df["credit_utilization"] = df["Total_Debt"] / df["Credit_Limit"]
    df["credit_utilization"] = df["credit_utilization"].replace([np.inf, -np.inf], np.nan)
    df["credit_util_bin"] = pd.cut(
        df["credit_utilization"],
        bins=[0, 0.1, 0.3, 0.5, 0.7, np.inf],
        labels=["Very Low", "Low", "Medium", "High", "Maxed Out"],
    )
    df["fico_tier"] = pd.cut(
        df["FICO_Score"],
        bins=[300, 580, 670, 740, 800, 850],
        labels=[
            "Poor (<580)",
            "Fair (580-669)",
            "Good (670-739)",
            "Very Good (740-799)",
            "Exceptional (800+)",
        ],
    )
    df["low_FICO_high_spend"] = ((df["FICO_Score"] < 671) & (df["Amount"] > 0.1 * df["Yearly_Income_Person"])).astype(
        int
    )
    df["low_FICO_high_DTI"] = ((df["FICO_Score"] < 670) & (df["debt_to_income"] > 2)).astype(int)

    # Synthetic fraud
    df["account_tenure_years"] = -(df["Acct_Open_Date"] - df["timestamp"]).dt.days / 365
    df["synthetic_risk"] = ((df["FICO_Score"] >= 740) & (df["account_tenure_years"] < 2)).astype(int)
    df["synthetic_risk_2"] = ((df["Num_Credit_Cards"] > 4) & (df["high_debt_ratio"] == 1)).astype(int)
    # Zip mismatch
    df["is_us_zip"] = df["Zip"].str.match(r"^\d{4,5}$")
    df["zip_mismatch_flag"] = ((df["Zip"] != df["Zipcode"]) & df["is_us_zip"]).astype(int)

    # Expiry
    df["months_to_expiry"] = (df["Expires"] - df["timestamp"]).dt.days / 30

    # Validate the transformed data
    validated = [TransactionFeatures(**row) for row in df.to_dict(orient="records")]
    df = pd.DataFrame([v.model_dump() for v in validated])

    return df


if __name__ == "__main__":
    # Example usage
    from src.api._1_data_loader.load_data import load_data
    from src.api._2_merge_csvs.merge_data import merge_csvs

    data = load_data()
    df = merge_csvs(data.cards, data.users, data.transactions)
    df = transform_stage1(df)
    print(df)
