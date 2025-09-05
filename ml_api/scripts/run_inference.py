from src.api._1_data_loader.load_data import load_data
from src.api.utils.io import load_joblib, load_json,save_json
from src.api._2_merge_csvs.merge_data import merge_csvs
from src.api._3_transformation_stage1.transformation_stage_1 import transform_stage1
from src.api._6_transformation_stage2.transformation_stage_2 import transform_stage2
from src.api._7_transformation_stage3.transformation_stage3_inference import transformation_stage3_inference
import logging
from pathlib import Path
from datetime import datetime
from src.api._1_data_loader.constants import CARDS_CSV_PATH, USERS_CSV_PATH

# set up loading artifacts and data
base_path=Path(__file__).parent.parent / "data" / "processed"
input_folders=sorted([f for f in base_path.iterdir() if f.is_dir()])
latest_run=input_folders[-1]
inference_path=Path(__file__).parent.parent/"src"/"raw_data"/"data"/"8"/"inference.csv"


scaler= load_joblib(latest_run/"scaler.pkl")
encoder= load_joblib(latest_run/"encoder.pkl")
selected_columns= load_joblib(latest_run/"selected_columns.pkl")
model= load_joblib(latest_run/"xgboost_model.pkl")
meta= load_json(latest_run/"metadata.json")
data= load_data(cards_path= CARDS_CSV_PATH,
                users_path=USERS_CSV_PATH,
                transaction_path=inference_path)
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

result_folder=Path(__file__).parent.parent / "data" / "Prediction"
stamped_folder=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_path = result_folder / stamped_folder / "inference_results.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
save_json(output, output_path)

