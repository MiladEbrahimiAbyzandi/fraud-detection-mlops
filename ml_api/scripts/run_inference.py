from data_loader.load_data import load_data
from utils.io import load_joblib, load_json,save_json
from merge_csvs.merge_data import merge_csvs
from transformation_stage1.transformation_stage_1 import transform_stage1
from transformation_stage2.transformation_stage_2 import transform_stage2
from feature_preparation.transformation_stage3_inference import transformation_stage3_inference
import logging
from pathlib import Path

scaler= load_joblib("C:/Users/Milad/Desktop/fraud_detection/fraud-detection/ml_api/data/processed/scaler.pkl")
encoder= load_joblib("C:/Users/Milad/Desktop/fraud_detection/fraud-detection/ml_api/data/processed/encoder.pkl")
selected_columns= load_joblib("C:/Users/Milad/Desktop/fraud_detection/fraud-detection/ml_api/data/processed/selected_columns.pkl")
model= load_joblib("C:/Users/Milad/Desktop/fraud_detection/fraud-detection/ml_api/data/processed/xgboost_model.pkl")
meta= load_json("C:/Users/Milad/Desktop/fraud_detection/fraud-detection/ml_api/data/processed/metadata.json")
data= load_data(cards_path="C:/Users/Milad/Desktop/fraud_detection/fraud-detection/ml_api/src/data_loader/data/8/sd254_cards.csv",
                users_path="C:/Users/Milad/Desktop/fraud_detection/fraud-detection/ml_api/src/data_loader/data/8/sd254_users.csv",
                transaction_path="C:/Users/Milad/Desktop/fraud_detection/fraud-detection/ml_api/src/data_loader/data/8/inference.csv")
df=merge_csvs(data.cards, data.users, data.transactions)
df=transform_stage1(df)
df=transform_stage2(meta, df)
df=transformation_stage3_inference(df, encoder, scaler, selected_columns)
predictions = model.predict(df)
predictions_proba = model.predict_proba(df)[:, 1]
output = {
    "predictions": predictions.tolist(),
    "predictions_proba": predictions_proba.tolist()
}
logging.info("Inference completed successfully.")
logging.info(f"Predictions: {output['predictions']}")
logging.info(f"Prediction Probabilities: {output['predictions_proba']}")

output_path = Path("data/Prediction/predictions.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
save_json(output, output_path)

