import pandas as pd
from src.api._6_transformation_stage2.model import Stage2Features


def transform_stage2(metadata: dict, data: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    try:
        """Transform data for stage 2."""

        high_risk_states = metadata["high_risk_states"]
        high_risk_cities = metadata["high_risk_cities"]
        high_risk_mcc = metadata["high_risk_mcc"]
        high_risk_merchants = metadata["high_risk_merchants"]
        threshold = metadata["threshold"]

        # Create new columns based on metadata
        data["high_risk_state"] = data["Merchant_State"].apply(lambda x: 1 if x in high_risk_states else 0)
        data["high_risk_cities"] = data["Merchant_City"].apply(lambda x: 1 if x in high_risk_cities else 0)
        data["high_risk_transactions"] = (data["amount_income_ratio"] > threshold).astype(int)
        data["high_risk_MCC"] = data["MCC"].apply(lambda x: 1 if x in high_risk_mcc else 0)
        data["unique_mcc_count"] = data.groupby("User")["MCC"].transform("nunique")
        data["next_mcc"] = data.groupby("User")["MCC"].shift(-1).astype(str)
        data["mcc_changed"] = (data["MCC"] != data["next_mcc"]).astype(int)
        data["time_diff"] = data.groupby("User")["timestamp"].diff(-1).abs()
        data["rapid_mcc_changed"] = ((data["mcc_changed"] == 1) & (data["time_diff"] <= pd.Timedelta(hours=1))).astype(
            int
        )

        data["high_risk_merchant"] = data["Merchant_Name"].apply(lambda x: 1 if x in high_risk_merchants else 0)
        validated = (Stage2Features(**row) for row in data.to_dict(orient="records"))
        df = pd.DataFrame([v.model_dump() for v in validated])
        return df

    except Exception as e:
        print(f"Error in transform_Stage2 : {e} ")


if __name__ == "__main__":
    # Example usage
    from src.api._1_data_loader.load_data import load_data
    from src.api._2_merge_csvs.merge_data import merge_csvs
    from src.api._3_transformation_stage1.transformation_stage_1 import transform_stage1
    from src.api._4_splitter.data_splitter import split_data
    from src.api._5_metadata.metadata_extractor import metadata

    data = load_data()
    df = merge_csvs(data.cards, data.users, data.transactions)
    df = transform_stage1(df)
    X_train, X_test, y_train, y_test = split_data(df)
    meta = metadata(X_train, y_train)
    X_train = transform_stage2(meta, X_train)
    X_test = transform_stage2(meta, X_test)
    print("Stage 2 transformation completed successfully.")
