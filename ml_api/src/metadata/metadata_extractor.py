import pandas as pd

def metadata(X_train: pd.DataFrame, y_train: pd.Series) -> dict:
    """
    Extract EDA level metadata.
    """
    
    try:
        
        cp_transactions = df[df["transaction_type"] == "CP"]
        state_fraud_rate = cp_transactions.groupby("Merchant_State")[
            "Is_Fraud"
        ].mean()
        high_risk_states = state_fraud_rate[
            state_fraud_rate > df["Is_Fraud"].mean()
        ].index.tolist()

        # High-risk cities
        city_fraud_rate = cp_transactions.groupby("Merchant_City")[
            "Is_Fraud"
        ].mean()
        high_risk_cities = city_fraud_rate[
            city_fraud_rate > df["Is_Fraud"].mean()
        ].index.tolist()

        df["amount_income_ratio"] = (
            df["Amount"] / df["Yearly_Income_Person"]
        )
        threshold = df["amount_income_ratio"].quantile(0.99)

        # MCC features
        mcc_fraud_data = df.groupby("MCC").agg(
            fraud_count=("Is_Fraud", "sum"), fraud_rate=("Is_Fraud", "mean")
        )
        high_risk_mcc = mcc_fraud_data[
            mcc_fraud_data["fraud_rate"] > df["Is_Fraud"].mean()
        ].index.tolist()

        # High-risk merchants
        fraud_stats_by_merchant = (
            df.groupby("Merchant_Name")["Is_Fraud"]
            .agg(["count", "mean"])
            .sort_values(by="mean", ascending=False)
        )
        fraud_stats_by_merchant.columns = ["transaction_count", "fraud_rate"]
        high_risk_merchants = fraud_stats_by_merchant[
            (fraud_stats_by_merchant["transaction_count"] >= 20)
            & (fraud_stats_by_merchant["fraud_rate"] > 0.1)
        ].index

        # Convert sets/indexes to lists for JSON compatibility
        metadata_dict = {
            "high_risk_states": high_risk_states,
            "high_risk_cities": high_risk_cities,
            "high_risk_mcc": high_risk_mcc,
            "high_risk_merchants": list(
                high_risk_merchants
            ),  # convert Index to list
            "threshold": threshold,
            }
        return metadata_dict

    except Exception as e:
        print(f"Error calculating metadata : {e} ")

if __name__ == "__main__":
    # Example usage
    from data_loader.load_data import load_data
    from merge_csvs.merge_data import merge_csvs
    from transformation_stage1.transformation_stage_1 import transform_stage1
    from splitter.data_splitter import split_data

    
    data = load_data()
    df = merge_csvs(data.cards, data.users, data.transactions)
    df= transform_stage1(df)
    # Split the data
    X_train, X_test, y_train, y_test = split_data(df)
    
    metadata_dict = metadata(X_train, y_train)
    
    print("Metadata extraction completed successfully.")
    print(metadata_dict)