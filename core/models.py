import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from prophet import Prophet
import shap


# ---------------------------------------------------
# CHURN PREDICTION MODEL
# ---------------------------------------------------

class ChurnPredictorML:

    def __init__(self):

        self.model = RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42
        )

        self.is_trained = False

    def train(self, X, y):

        scores = cross_val_score(
            self.model,
            X,
            y,
            cv=5,
            scoring="roc_auc"
        )

        print("\nCross Validation AUC:", scores)
        print("Mean AUC:", scores.mean())

        self.model.fit(X, y)

        self.is_trained = True

    def predict_probs(self, X):

        if not self.is_trained:
            return np.zeros(len(X))

        return self.model.predict_proba(X)[:, 1] * 100

    def explain_predictions(self, X):

        if not self.is_trained:
            return None, None

        explainer = shap.TreeExplainer(self.model)

        shap_values = explainer.shap_values(X)

        return shap_values, explainer


# ---------------------------------------------------
# REVENUE FORECASTER
# ---------------------------------------------------

class RevenueForecaster:

    def forecast(self, series):

        df = series.reset_index()

        df.columns = ["ds", "y"]

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False
        )

        model.fit(df)

        future = model.make_future_dataframe(
            periods=3,
            freq="MS"
        )

        forecast = model.predict(future)

        return forecast["yhat"].tail(3).tolist()


# ---------------------------------------------------
# REVENUE ANOMALY DETECTION
# ---------------------------------------------------

class RevenueAnomalyDetector:

    def detect(self, series):

        mean = series.mean()
        std = series.std()

        threshold = mean - 2 * std

        anomalies = series[series < threshold]

        return anomalies


# ---------------------------------------------------
# ADAPTIVE INTELLIGENCE ENGINE
# ---------------------------------------------------

class AdaptiveIntelligenceEngine:

    def predict_lifecycle(self, row):

        if row["payment_count"] <= 2:
            return "NEW"

        if row["recency"] > 60:
            return "CHURNED"

        if row["revenue_trend"] < -10:
            return "DECLINING"

        if row["revenue_trend"] > 10:
            return "GROWING"

        if row["volatility"] < 0.2:
            return "STABLE"

        return "ACTIVE"

    def calculate_hybrid_risk(self, row, ml_prob):

        rule_risk = 0

        if row["recency"] > (row["avg_gap"] * 1.5):
            rule_risk += 50

        if row["volatility"] > 0.5:
            rule_risk += 30

        rule_risk = min(rule_risk, 100)

        ml_weight = min(row["payment_count"] / 15, 0.8)

        final = (ml_prob * ml_weight) + (rule_risk * (1 - ml_weight))

        return round(final, 1)


# ---------------------------------------------------
# BUSINESS HEALTH ENGINE
# ---------------------------------------------------

class BusinessHealthEngine:

    def calculate_burnout_risk(self, client_stats):

        total = len(client_stats)

        if total == 0:
            return 0

        # ---------------------------
        # 1. High Risk Clients
        # ---------------------------

        high_risk_ratio = (
            (client_stats["RISK_%"] > 60).sum() / total
        )

        # ---------------------------
        # 2. Revenue Volatility
        # ---------------------------

        volatility = client_stats["volatility"].mean()

        volatility = min(volatility, 1)

        # ---------------------------
        # 3. Client Dependency
        # ---------------------------

        top_share = (
            client_stats["revenue_share_%"].max() / 100
        )

        # ---------------------------
        # Weighted Burnout Score
        # ---------------------------

        burnout = (
            0.4 * high_risk_ratio +
            0.3 * volatility +
            0.3 * top_share
        )

        burnout = burnout * 100

        return round(min(burnout, 100), 1)

# ---------------------------------------------------
# PRICING OPTIMIZER
# ---------------------------------------------------

class HeuristicPricingOptimizer:

    def suggest_adjustment(self, row):

        if row["RISK_%"] > 60:
            return "Retention Discount (-10%)"

        if row["STAGE"] == "DECLINING":
            return "Reduce Rate 10%"

        if row["STAGE"] == "GROWING":
            return "Premium Rate (+15%)"

        if row["STAGE"] == "STABLE":
            return "Standard Increase (+5%)"

        return "Maintain Rate"


# ---------------------------------------------------
# CLV ENGINE
# ---------------------------------------------------

class CLVEngine:

    def estimate_predictive_clv(self, row):

        months = row["payment_count"] * row["avg_gap"] / 30

        months = max(months, 0.5)

        tenure = min(months / 12, 2)

        avg_month = row["total_revenue"] / months

        if row["STAGE"] == "CHURNED":
            mult = 0.8

        elif row["STAGE"] == "DECLINING":
            mult = 1.2

        elif row["STAGE"] == "GROWING":
            mult = 2.5

        else:
            mult = 1.8

        clv = avg_month * months * mult * tenure

        return round(clv, 2)