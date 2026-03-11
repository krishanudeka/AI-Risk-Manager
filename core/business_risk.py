import numpy as np


class BusinessRiskEngine:

    def calculate_risk_score(self, client_stats, monthly_stats, burnout, forecast):

        # ------------------------------
        # 1. High risk client ratio
        # ------------------------------

        high_risk_clients = (client_stats["RISK_%"] > 60).sum()
        total_clients = len(client_stats)

        client_risk_ratio = (high_risk_clients / total_clients) * 100


        # ------------------------------
        # 2. Revenue volatility
        # ------------------------------

        revenue = monthly_stats["revenue"]

        volatility = revenue.std() / (revenue.mean() + 1e-9)

        volatility_score = min(volatility * 100, 100)


        # ------------------------------
        # 3. Forecast trend
        # ------------------------------

        if len(forecast) >= 2:

            trend = forecast[-1] - forecast[0]

            if trend < 0:
                forecast_risk = 70
            else:
                forecast_risk = 20

        else:
            forecast_risk = 40


        # ------------------------------
        # 4. Combine all signals
        # ------------------------------

        risk_score = (
            0.4 * burnout +
            0.3 * client_risk_ratio +
            0.2 * volatility_score +
            0.1 * forecast_risk
        )

        return round(min(risk_score, 100), 1)


    def risk_status(self, score):

        if score < 30:
            return "Healthy"

        if score < 60:
            return "Moderate Risk"

        if score < 80:
            return "High Risk"

        return "Critical"