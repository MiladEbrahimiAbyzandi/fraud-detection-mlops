import pandas as pd
import logging
from data_loader.load_data import load_data
from merge_csvs.merge_data import merge_csvs
from transformation_stage1.transformation_stage_1 import transform_stage1
from splitter.data_splitter import split_data
from metadata.metadata_extractor import metadata
from transformation_stage2.transformation_stage_2 import transform_stage2
from feature_preparation.transformation_stage3_training import transformation_stage3_training
from imbalance_correction.imbalance_correction import handle_imbalance
from training.training import train
from evaluate.evaluate import evaluate
from utils.io import save_joblib
from pathlib import Path


logging.basicConfig(level=logging.INFO)
path= Path(__file__).parent.parent / "data" / "processed"
path.mkdir(parents=True, exist_ok=True)

data= load_data()
df = merge_csvs(data.cards, data.users, data.transactions)
df = transform_stage1(df)
X_train, X_test, y_train, y_test = split_data(df)
meta = metadata(X_train, y_train)
save_joblib(meta, path / "metadata.pkl")
X_train = transform_stage2(meta, X_train)
X_test = transform_stage2(meta, X_test)
# Transform stage 3

X_train_transformed, X_test_transformed, encoder, scaler, selected_columns = transformation_stage3_training(X_train=X_train, X_test=X_test)
save_joblib(encoder, path / "encoder.pkl")
save_joblib(scaler, path / "scaler.pkl")
save_joblib(selected_columns, path / "selected_columns.pkl")

# Handle imbalance
X_train_balanced, y_train_balanced = handle_imbalance(X_train_transformed, y_train)
# Train the model   
model = train(X_train_balanced, y_train_balanced, model_name="xgboost")
# Save the model
save_joblib(model, path / "xgboost_model.pkl")
# Evaluate the model
metrics = evaluate(model, X_test_transformed, y_test)
logging.info(f"Model evaluation metrics:{metrics}")
logging.info("Model training completed successfully.")
