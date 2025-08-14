import pandas as pd
from typing import Literal
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier


def train(x_train: pd.DataFrame, y_train: pd.Series, model_name: Literal["xgboost", "randomforest"]) -> object:
    """Train the model with the provided training data."""

    x_train.columns = x_train.columns.astype(str).str.replace(r"[\[\]<>]", "", regex=True)

    if model_name == "xgboost":
        model = XGBClassifier(
            use_label_encoder=False,
            eval_metric="logloss",
            max_depth=12,
            scale_pos_weight=10,
            random_state=42,
            n_jobs=-1,
        )
    elif model_name == "randomforest":
        model = RandomForestClassifier(n_estimators=100, min_samples_leaf=5, random_state=42, n_jobs=-1)
    else:
        raise ValueError("Invalid model name. Choose 'xgboost' or 'randomforest'.")

    model.fit(x_train, y_train)

    return model


if __name__ == "__main__":
    # Example usage
    from data_loader.load_data import load_data
    from merge_csvs.merge_data import merge_csvs
    from transformation_stage1.transformation_stage_1 import transform_stage1
    from splitter.data_splitter import split_data
    from metadata.metadata_extractor import metadata
    from transformation_stage2.transformation_stage_2 import transform_stage2
    from feature_preparation.transformation_stage3_training import transformation_stage3_training
    from imbalance_correction.imbalance_correction import handle_imbalance

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
    # Handle imbalance
    X_train_balanced, y_train_balanced = handle_imbalance(X_train_transformed, y_train)
    # Train the model
    model = train(X_train_balanced, y_train_balanced, model_name="xgboost")

    print("Model training completed successfully.")
