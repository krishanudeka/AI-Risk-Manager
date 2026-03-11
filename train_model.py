import joblib
import pandas as pd

from core.data_pipelining import AdaptiveDataPipeline
from core.models import ChurnPredictorML

print("Running training pipeline...")

pipeline = AdaptiveDataPipeline(
    tx_path="data/transactions.csv",
    client_path="data/clients.csv",
    invoice_path="data/invoices.csv"
)

monthly, clients = pipeline.process()

features = [
    "avg_gap",
    "volatility",
    "revenue_trend",
    "revenue_share_%",
    "avg_payment_delay"
]

X = clients[features].fillna(0)
y = clients["churn_label"]

model = ChurnPredictorML()

model.train(X, y)

joblib.dump(model.model, "models_saved/churn_model.pkl")

print("Model saved successfully.")