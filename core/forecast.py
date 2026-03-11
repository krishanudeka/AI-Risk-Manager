import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def revenue_forecast():

    transactions = pd.read_csv("data/transactions.csv")

    transactions["date"] = pd.to_datetime(transactions["date"])

    monthly = transactions.groupby(
        transactions["date"].dt.to_period("M")
    )["amount"].sum().reset_index()

    monthly["month_number"] = np.arange(len(monthly))

    X = monthly[["month_number"]]
    y = monthly["amount"]

    model = LinearRegression()
    model.fit(X, y)

    future_months = np.arange(len(monthly), len(monthly) + 3).reshape(-1,1)

    predictions = model.predict(future_months)

    forecast = []

    for i,p in enumerate(predictions):
        forecast.append({
            "month": f"Month {i+1}",
            "revenue": round(float(p),2)
        })

    return forecast


def churn_forecast():

    clients = pd.read_csv("data/clients.csv")

    high_risk = clients[clients["risk"] > 0.2]

    churn_prediction = []

    for i,row in high_risk.iterrows():

        churn_prediction.append({
            "client": row["client_id"],
            "probability": round(row["risk"]*100,2),
            "expected_exit":"60 days"
        })

    return churn_prediction