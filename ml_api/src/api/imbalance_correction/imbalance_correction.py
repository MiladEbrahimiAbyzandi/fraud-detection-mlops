import pandas as pd
import logging
from imblearn.over_sampling import SMOTE

def handle_imbalance(X_train: pd.DataFrame, y_train: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """Apply SMOTE."""

    smote = SMOTE(sampling_strategy=1.0, random_state=42)
    X_train, y_train = smote.fit_resample(X_train, y_train)
    logging.info(f"SMOTE Train Shape: {X_train.shape}, Fraud: {y_train.sum()}")
    return X_train, y_train

if __name__ == "__main__":
    # Example usage
    from data_loader.load_data import load_data
    from merge_csvs.merge_data import merge_csvs
    from transformation_stage1.transformation_stage_1 import transform_stage1
    from splitter.data_splitter import split_data
    from metadata.metadata_extractor import metadata
    from transformation_stage2.transformation_stage_2 import transform_stage2
    from feature_preparation.transformation_stage3_training import transformation_stage3_training

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
    logging.info("Imbalance handling completed successfully.")