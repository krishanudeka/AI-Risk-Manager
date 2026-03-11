from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
import joblib
import os
import random

from core.data_pipelining import AdaptiveDataPipeline
from core.models import (
    AdaptiveIntelligenceEngine,
    BusinessHealthEngine,
    RevenueForecaster,
    CLVEngine,
    HeuristicPricingOptimizer
)
from core.business_risk import BusinessRiskEngine
from fastapi.responses import FileResponse
from core.forecast import revenue_forecast, churn_forecast
from core.ingestion import load_user_file
from core.mapper import auto_map_columns
from core.validator import validate_transactions
from core.dataset_builder import build_datasets_from_transactions


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
EXPORT_DIR = "exports"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# clear uploads on server start
for f in os.listdir(UPLOAD_DIR):
    os.remove(os.path.join(UPLOAD_DIR, f))

MODEL_PATH = "models_saved/churn_model.pkl"
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None


# ------------------------------
# PIPELINE
# ------------------------------

def run_pipeline(tx, clients=None, invoices=None):

    pipeline = AdaptiveDataPipeline(
        tx_df=tx,
        client_df=clients,
        invoice_df=invoices
    )

    return pipeline.process()


# ------------------------------
# LOAD DATA FROM UPLOADS
# ------------------------------

def load_uploaded_data():

    files = os.listdir(UPLOAD_DIR)

    if len(files) == 0:
        return None, None, None

    processed_dfs = []

    for file in files:

        path = os.path.join(UPLOAD_DIR, file)

        try:
            # -----------------------------
            # LOAD FILE
            # -----------------------------
            df = load_user_file(path)

            # -----------------------------
            # MAP COLUMNS
            # -----------------------------
            df = auto_map_columns(df)

            # -----------------------------
            # VALIDATE
            # -----------------------------
            df = validate_transactions(df)

            processed_dfs.append(df)

        except Exception as e:
            print(f"[UPLOAD WARNING] {file} skipped: {e}")

    if len(processed_dfs) == 0:
        return None, None, None

    # -----------------------------
    # MERGE DATA
    # -----------------------------

    combined_df = pd.concat(processed_dfs, ignore_index=True)

    # -----------------------------
    # BUILD CLIENT + INVOICE DATASETS
    # -----------------------------

    clients_df, invoices_df = build_datasets_from_transactions(combined_df)

    return combined_df, clients_df, invoices_df


# ------------------------------
# MAIN ANALYSIS FUNCTION
# ------------------------------

def analyze_data():

    tx, clients, invoices = load_uploaded_data()

    print("Transactions rows:", 0 if tx is None else len(tx))
    print("Clients rows:", 0 if clients is None else len(clients))
    print("Invoices rows:", 0 if invoices is None else len(invoices))

    if tx is None:
        return None, None

    monthly, clients_df = run_pipeline(tx, clients, invoices)

    features = [
        "avg_gap",
        "volatility",
        "revenue_trend",
        "revenue_share_%",
        "avg_payment_delay"
    ]

    X = clients_df[features].fillna(0)

    ml_probs = model.predict_proba(X)[:,1]*100 if model else [0]*len(X)

    intel = AdaptiveIntelligenceEngine()
    pricing = HeuristicPricingOptimizer()
    clv = CLVEngine()

    # lifecycle stage
    clients_df["STAGE"] = clients_df.apply(
        intel.predict_lifecycle,
        axis=1
    )

    # risk score
    risks = []

    for i in range(len(clients_df)):

        r = intel.calculate_hybrid_risk(
            clients_df.iloc[i],
            ml_probs[i]
        )

        risks.append(r)

    clients_df["RISK_%"] = risks

    # CLV
    clients_df["PREDICTIVE_CLV"] = clients_df.apply(
        clv.estimate_predictive_clv,
        axis=1
    )

    # pricing strategy
    clients_df["PRICE_STRATEGY"] = clients_df.apply(
        pricing.suggest_adjustment,
        axis=1
    )

    return monthly, clients_df


# ------------------------------
# FILE UPLOAD
# ------------------------------

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):

    # clear old uploads
    for f in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, f))

    saved = []

    for file in files:

        filename = file.filename.lower()

        if not (filename.endswith(".csv") or filename.endswith(".xlsx") or filename.endswith(".xls")):
            continue

        path = os.path.join(UPLOAD_DIR, file.filename)

        with open(path, "wb") as buffer:
            buffer.write(await file.read())

        saved.append(file.filename)

    return {
        "status": "files uploaded successfully",
        "files": saved
    }


# ------------------------------
# DASHBOARD
# ------------------------------

@app.get("/dashboard")
def get_dashboard():

    if len(os.listdir(UPLOAD_DIR)) == 0:
        return {"no_data": True}

    monthly, clients_df = analyze_data()

    if clients_df is None:
        return {"no_data": True}

    revenue_trend = monthly.reset_index()
    revenue_trend["date"] = revenue_trend["date"].astype(str)

    lifecycle_distribution = clients_df["STAGE"].value_counts().to_dict()

    # ------------------------------
    # ANALYTICS
    # ------------------------------

    health = BusinessHealthEngine()
    risk_engine = BusinessRiskEngine()
    forecaster = RevenueForecaster()

    burnout = health.calculate_burnout_risk(clients_df)

    if burnout < 20:
       burnout_status = "Healthy"

    elif burnout < 40:
       burnout_status = "Moderate"

    elif burnout < 60:
       burnout_status = "High"

    else:
       burnout_status = "Critical"

    forecast_vals = forecaster.forecast(
        monthly["net_cash_flow"]
    )

    forecast_data = []

    for i, v in enumerate(forecast_vals):

        forecast_data.append({
            "month": f"M{i+1}",
            "forecast": float(v),
            "lower": float(v*0.85),
            "upper": float(v*1.15)
        })

    # dependency risk

    client_rev = clients_df[["client_id","PREDICTIVE_CLV"]].copy()

    client_rev = client_rev.sort_values(
        "PREDICTIVE_CLV",
        ascending=False
    )

    total_rev = client_rev["PREDICTIVE_CLV"].sum()

    dependency = {
        "top_client":
            round((client_rev.iloc[0]["PREDICTIVE_CLV"]/total_rev)*100,1),

        "top_5_clients":
            round((client_rev.head(5)["PREDICTIVE_CLV"].sum()/total_rev)*100,1)
    }

    business_risk_score = risk_engine.calculate_risk_score(
        clients_df,
        monthly,
        burnout,
        forecast_vals
    )

    risk_status = risk_engine.risk_status(business_risk_score)

    # alerts

    alerts = []

    high_risk = clients_df[clients_df["RISK_%"] > 60]

    if not high_risk.empty:

        c = high_risk.iloc[0]

        alerts.append(
            f"Recover client {c['client_id']} high CLV risk"
        )

    if burnout > 60:

        alerts.append("Burnout risk high. Reduce workload.")

    # top clients

    top_clients = clients_df.sort_values(
        "PREDICTIVE_CLV",
        ascending=False
    ).head(10)

    return {

        "summary": {
            "total_clients": len(clients_df),
            "high_risk_clients": int((clients_df["RISK_%"] > 60).sum())
        },

        "burnout": burnout,

        "risk_score": business_risk_score,

        "risk_status": risk_status,

        "dependency_risk": dependency,

        "forecast": forecast_data,

        "financial_trend":
            revenue_trend[
                ["date","revenue","expenses","net_cash_flow"]
            ].to_dict(orient="records"),

        "risk_distribution":
            clients_df.get("churn_label", pd.Series()).value_counts().to_dict(),

        "lifecycle_distribution":
            lifecycle_distribution,

        "heatmap":
            clients_df[[
                "client_id",
                "RISK_%",
                "PREDICTIVE_CLV",
                "volatility"
            ]].to_dict(orient="records"),

        "risk_matrix":
            clients_df[[
                "client_id",
                "PREDICTIVE_CLV",
                "RISK_%"
            ]].to_dict(orient="records"),

        "churn_forecast":
            clients_df[
                clients_df["RISK_%"] > 60
            ][[
                "client_id",
                "RISK_%",
                "PREDICTIVE_CLV"
            ]].to_dict(orient="records"),

        "top_clients":
            top_clients[[
                "client_id",
                "PREDICTIVE_CLV",
                "RISK_%",
                "STAGE",
                "PRICE_STRATEGY"
            ]].to_dict(orient="records"),

        "alerts": alerts
    }


# ------------------------------
# CLIENT LIST
# ------------------------------

@app.get("/clients")
def get_clients():

    # if user has not uploaded anything
    if len(os.listdir(UPLOAD_DIR)) == 0:
        return {"no_data": True}

    monthly, clients_df = analyze_data()

    if clients_df is None:
        return {"no_data": True}

    return {
        "clients":
        clients_df[[
            "client_id",
            "PREDICTIVE_CLV",
            "RISK_%",
            "STAGE",
            "PRICE_STRATEGY"
        ]].to_dict(orient="records")
    }


# ------------------------------
# DOWNLOAD CLIENT LIST
# ------------------------------

@app.get("/download-clients")
def download_clients():

    monthly, clients_df = analyze_data()

    if clients_df is None:
        return {"error": "no data"}

    path = os.path.join(EXPORT_DIR,"client_analysis.csv")

    clients_df.to_csv(path,index=False)

    return FileResponse(
        path,
        media_type="text/csv",
        filename="client_analysis.csv"
    )


# ------------------------------
# MANUAL ENTRY
# ------------------------------

@app.post("/manual-entry")
async def manual_entry(data: dict):

    clients = data["clients"]

    clients_df = pd.DataFrame(clients)

    transactions = []

    for c in clients:

        base = c["base_value"]

        for i in range(6):

            variation = random.uniform(0.8,1.2)

            transactions.append({
                "date": f"2024-0{i+1}-01",
                "client_id": c["client_id"],
                "amount": round(base * variation,2),
                "type": "income",
                "category": "Service"
            })

    tx_df = pd.DataFrame(transactions)

    clients_df.to_csv(os.path.join(UPLOAD_DIR,"clients_manual.csv"),index=False)
    tx_df.to_csv(os.path.join(UPLOAD_DIR,"transactions_manual.csv"),index=False)

    return {"status":"manual data saved"}

@app.get("/forecast")
def get_forecast():

    if len(os.listdir(UPLOAD_DIR)) == 0:
        return {"no_data": True}

    monthly, clients_df = analyze_data()

    if clients_df is None:
        return {"no_data": True}

    # ------------------------------
    # REVENUE FORECAST
    # ------------------------------

    forecaster = RevenueForecaster()

    forecast_vals = forecaster.forecast(
        monthly["net_cash_flow"]
    )

    forecast_data = []

    for i,v in enumerate(forecast_vals):

        forecast_data.append({
            "month": f"M{i+1}",
            "revenue": float(v)
        })

    next_month = float(forecast_vals[0])
    next_quarter = float(sum(forecast_vals))

    # simple confidence estimate
    confidence = 80 + (len(monthly) % 10)

    # ------------------------------
    # HIGH RISK CLIENTS
    # ------------------------------

    high_risk = clients_df[
        clients_df["RISK_%"] > 60
    ][[
        "client_id",
        "RISK_%",
        "PREDICTIVE_CLV"
    ]]

    high_risk_clients = []

    revenue_at_risk = 0

    for _,row in high_risk.iterrows():

        risk_revenue = row["PREDICTIVE_CLV"] * (row["RISK_%"]/100)

        revenue_at_risk += risk_revenue

        high_risk_clients.append({
            "client": row["client_id"],
            "probability": round(row["RISK_%"],1),
            "clv": round(row["PREDICTIVE_CLV"],2),
            "revenue_risk": round(risk_revenue,2)
        })

    # ------------------------------
    # CHURN FORECAST (MONTHLY)
    # ------------------------------

    churn_forecast = []

    churn_count = len(high_risk_clients)

    for i in range(3):

        expected = int(churn_count * (0.3 + i*0.2))

        loss = revenue_at_risk * (0.25 + i*0.2)

        churn_forecast.append({
            "month": f"M{i+1}",
            "expected_churn": expected,
            "revenue_loss": round(loss,2)
        })

    return {

        "summary":{
            "next_month_revenue": round(next_month,2),
            "next_quarter_revenue": round(next_quarter,2),
            "confidence": confidence,
            "revenue_at_risk": round(revenue_at_risk,2)
        },

        "revenue_forecast": forecast_data,

        "high_risk_clients": high_risk_clients,

        "churn_forecast": churn_forecast
    }