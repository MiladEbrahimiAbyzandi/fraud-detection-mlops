import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

def evaluate(model: BaseEstimator, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """
    Evaluate the model on the test set.
    
    Args:
        model (BaseEstimator): The trained model to evaluate.
        X_test (pd.DataFrame): The test features.
        y_test (pd.Series): The true labels for the test set.
        
    Returns:
        dict: A dictionary containing evaluation metrics.
    """
    try:
        if not isinstance(model, BaseEstimator):
            raise ValueError("The model must be an instance of BaseEstimator.")
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1] if hasattr (model, "predict_proba") else None

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "Roc_Auc": roc_auc_score(y_test, y_prob) if y_prob is not None else None,
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()  # Convert to list for easier serialization
        }

        return metrics
    

    except Exception as e:
        print(f"Error in metadata extraction: {e}")
        return {}
    
if __name__ == "__main__":
    # Example usage
    from api._1_data_loader.load_data import load_data
    from api._2_merge_csvs.merge_data import merge_csvs
    from api._3_transformation_stage1.transformation_stage_1 import transform_stage1
    from api._4_splitter.data_splitter import split_data
    from api._5_metadata.metadata_extractor import metadata
    from api._6_transformation_stage2.transformation_stage_2 import transform_stage2
    from api._7_transformation_stage3.transformation_stage3_training import transformation_stage3_training
    from api._8_imbalance_correction.imbalance_correction import handle_imbalance
    from api._9_training.training import train

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
    
    # Evaluate the model
    metrics = evaluate(model, X_test_transformed, y_test)
    print ("Model evaluation metrics:", metrics)
    print("Model evaluation completed successfully.")