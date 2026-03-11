import matplotlib.pyplot as plt
import pandas as pd
import shap


# ---------------------------------------------------
# PROFIT FORECAST PLOT
# ---------------------------------------------------

def plot_advanced_health(monthly_df, forecast, burnout):

    plt.style.use("dark_background")

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(
        monthly_df.index,
        monthly_df["net_cash_flow"],
        label="Historical Profit",
        marker="o"
    )

    future_dates = pd.date_range(
        start=monthly_df.index[-1],
        periods=4,
        freq="MS"
    )[1:]

    ax.plot(
        future_dates,
        forecast,
        label="AI Forecast",
        linestyle="--",
        marker="s"
    )

    ax.set_title("AI Business Intelligence: Net Cash Flow Forecast")

    if burnout > 60:
        ax.text(
            0.02,
            0.95,
            f"Burnout Alert: {burnout}%",
            transform=ax.transAxes,
            color="red"
        )

    ax.legend()

    plt.grid(alpha=0.2)

    plt.show()


# ---------------------------------------------------
# CLIENT RISK DISTRIBUTION
# ---------------------------------------------------

def plot_risk_distribution(client_df):

    risk_bins = pd.cut(
        client_df["RISK_%"],
        bins=[0, 30, 60, 100],
        labels=["Low", "Medium", "High"]
    )

    counts = risk_bins.value_counts().sort_index()

    plt.figure(figsize=(6, 6))

    plt.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=["#2ecc71", "#f1c40f", "#e74c3c"]
    )

    plt.title("Client Risk Distribution")

    plt.show()


# ---------------------------------------------------
# SHAP SUMMARY PLOT
# ---------------------------------------------------

def plot_shap_summary(model, X):

    shap_values, explainer = model.explain_predictions(X)

    if shap_values is None:
        print("Model not trained yet.")
        return

    # Handle new SHAP output format
    if len(shap_values.shape) == 3:
        shap_values = shap_values[:, :, 1]

    shap.summary_plot(shap_values, X)


# ---------------------------------------------------
# SHAP WATERFALL PLOT
# ---------------------------------------------------

def plot_shap_waterfall(model, X):

    shap_values, explainer = model.explain_predictions(X)

    if shap_values is None:
        return

    # Handle new SHAP format
    if len(shap_values.shape) == 3:
        shap_vals = shap_values[:, :, 1]
        base_val = explainer.expected_value[1]
    else:
        shap_vals = shap_values
        base_val = explainer.expected_value

    shap.plots.waterfall(
        shap.Explanation(
            values=shap_vals[0],
            base_values=base_val,
            data=X.iloc[0],
            feature_names=X.columns
        )
    )