import pandas as pd
import logging
from typing import Tuple
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.feature_selection import VarianceThreshold
logging.basicConfig(level=logging.INFO)
def transformation_stage3_training(X_train:pd.DataFrame,
                          X_test: pd.DataFrame
                          ) -> Tuple[pd.DataFrame, pd.DataFrame, OneHotEncoder, RobustScaler, list[str]]:
    """
    Drop columns, encode categorical variables, and scale numerical features.
    """

    # unnecessary columns
    drop_cols = [
        "Year",
        "Month",
        "Day",
        "Time",
        "Merchant_Name",
        "Merchant_City",
        "Merchant_State",
        "Zip",
        "Is_Fraud",
        "Current_Age",
        "Retirement_Age",
        "Birth_Year",
        "Birth_Month",
        "Gender",
        "Address",
        "Apartment",
        "City",
        "State",
        "Zipcode",
        "Latitude",
        "Longitude",
        "Per_Capita_Income_Zipcode",
        "Yearly_Income_Person",
        "Card_Number",
        "Expires",
        "CVV",
        "Acct_Open_Date",
        "Year_PIN_last_Changed",
        "Card_on_Dark_Web",
        "timestamp",
        "Date",
        "Acct_Open_Year",
        "low_FICO_high_spend",
        "low_FICO_high_DTI",
        "next_mcc",
        "time_diff",
        "is_us_zip",
        "min_acc_open_date",
        "max_acc_open_date",
    ]
    # categorical columns
    categorical_cols = [
        "Use_Chip",
        "MCC",
        "Errors",
        "Card_Brand",
        "Card_Type",
        "Has_Chip",
        "day_of_week",
        "transaction_type",
        "age_group",
        "retirement_proximity",
        "retirement_phase",
        "zip_income_tier",
        "income_tier",
        "income_mismatch",
        "credit_util_bin",
        "fico_tier",
    ]

    #numeric columns
    numeric_cols = [
        "Amount",
        "Total_Debt",
        "FICO_Score",
        "Num_Credit_Cards",
        "Cards_Issued",
        "Credit_Limit",
        "transaction_hour",
        "years_to_retirement",
        "years_since_retirement",
        "amount_income_ratio",
        "income_relative_to_zip",
        "debt_to_income",
        "credit_utilization",
        "account_tenure_years",
        "unique_mcc_count",
        "months_to_expiry",
    ]
    
    X_train = X_train.drop(columns=drop_cols, errors="ignore")
    X_test = X_test.drop(columns=drop_cols, errors="ignore")
    encoder = OneHotEncoder(
        handle_unknown="ignore", sparse_output=False
    )
    encoded = encoder.fit_transform(X_train[categorical_cols])
    encoded_df = pd.DataFrame(
        encoded,
        columns=encoder.get_feature_names_out(categorical_cols),
        index=X_train.index,
    )
    X_train = X_train.drop(columns=categorical_cols)
    X_train = pd.concat([X_train, encoded_df], axis=1)
    
    encoded_test = encoder.transform(X_test[categorical_cols])
    encoded_test_df = pd.DataFrame(
        encoded_test,
        columns=encoder.get_feature_names_out(categorical_cols),
        index=X_test.index,
    )
    X_test = X_test.drop(columns=categorical_cols)
    X_test = pd.concat([X_test, encoded_test_df], axis=1)
    # Scaling  
    scaler = RobustScaler()
    X_train[numeric_cols] = scaler.fit_transform(
        X_train[numeric_cols].fillna(
            X_train[numeric_cols].mean()
        )
    )
    X_test[numeric_cols] = scaler.transform(
        X_test[numeric_cols].fillna(
            X_test[numeric_cols].mean()
        )
    )
    
    # Variance threshold
    selector = VarianceThreshold(threshold=0.0001)
    X_train = pd.DataFrame(
        selector.fit_transform(X_train),
        columns=X_train.columns[selector.get_support()],
    )

    selected_columns = X_train.columns.tolist()
    X_test = X_test[selected_columns]

    return X_train, X_test, encoder, scaler, selected_columns
  
if __name__ == "__main__":
    # Example usage
    # Example usage
    from api._1_data_loader.load_data import load_data
    from api._2_merge_csvs.merge_data import merge_csvs
    from api._3_transformation_stage1.transformation_stage_1 import transform_stage1
    from api._4_splitter.data_splitter import split_data
    from api._5_metadata.metadata_extractor import metadata
    from api._6_transformation_stage2.transformation_stage_2 import transform_stage2

    data = load_data()
    df = merge_csvs(data.cards, data.users, data.transactions)
    df = transform_stage1(df)
    X_train, X_test, y_train, y_test = split_data(df)
    meta = metadata(X_train, y_train)
    X_train = transform_stage2(meta, X_train)
    X_test = transform_stage2(meta, X_test)
    
    # Transform stage 3
    X_train_transformed, X_test_transformed, encoder, scaler, selected_columns = transformation_stage3_training(
        X_train=X_train, X_test=X_test
    )
    logging.info("Transformation Stage 3 completed successfully.")
    logging.info(X_train_transformed.columns)




