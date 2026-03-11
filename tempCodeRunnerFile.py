import os

# -------------------------------------------------------
# PATH CONFIGURATION (PROFESSIONAL WAY)
# -------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


from core.data_pipelining import AdaptiveDataPipeline
from core.models import (
    AdaptiveIntelligenceEngine,
    ChurnPredictorML,
    BusinessHealthEngine,
    RevenueForecaster,
    HeuristicPricingOptimizer,
    CLVEngine
)

from core.visualizer import (
    plot_advanced_health,
    plot_risk_distribution,
    plot_shap_summary,
    plot_shap_waterfall
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, confusion_matrix

from core.ingestion import load_user_file
from core.mapper import auto_map_columns
from core.validator import validate_transactions
from core.manual_entry import load_manual_data
from core.dataset_builder import build_datasets_from_transactions
from core.business_risk import BusinessRiskEngine


# -------------------------------------------------------
# ANALYSIS SERVICE
# -------------------------------------------------------

def run_analysis_service():

    USE_USER_FILE = False
    USE_MANUAL_ENTRY = False

    # ------------------------------
    # MANUAL ENTRY MODE
    # ------------------------------

    if USE_MANUAL_ENTRY:

        tx_df, inv_df = load_manual_data()

        pipeline = AdaptiveDataPipeline(
            tx_df=tx_df,
            invoice_df=inv_df
        )

    # ------------------------------
    # CSV UPLOAD MODE
    # ------------------------------

    elif USE_USER_FILE:

        user_file = os.path.join(UPLOAD_DIR, "user_data.csv")
        user_df = load_user_file(user_file)

        user_df = auto_map_columns(user_df)

        user_df = validate_transactions(user_df)

        df_clients, df_invoices = build_datasets_from_transactions(user_df)

        pipeline = AdaptiveDataPipeline(
            tx_df=user_df,
            client_df=df_clients,
            invoice_df=df_invoices
        )

    # ------------------------------
    # DEFAULT DATASET
    # ------------------------------

    else:

        pipeline = AdaptiveDataPipeline(
            os.path.join(DATA_DIR, "transactions.csv"),
            os.path.join(DATA_DIR, "clients.csv"),
            os.path.join(DATA_DIR, "invoices.csv")
        )

    monthly_stats, client_stats = pipeline.process()

    feature_cols = [
        'avg_gap',
        'volatility',
        'revenue_trend',
        'revenue_share_%',
        'avg_payment_delay'
    ]

    X = client_stats[feature_cols].fillna(0)
    y = client_stats['churn_label']

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    ml_model = ChurnPredictorML()
    ml_model.train(X_train, y_train)

    y_pred = ml_model.model.predict(X_test)
    y_probs = ml_model.model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_probs)

    cm = confusion_matrix(y_test, y_pred)

    print("\n════════════════════════════════════════════════════════════")
    print("🧠 MACHINE LEARNING MODEL PERFORMANCE")
    print("════════════════════════════════════════════════════════════")

    print(f"Accuracy   : {accuracy:.3f}")
    print(f"Precision  : {precision:.3f}")
    print(f"Recall     : {recall:.3f}")
    print(f"AUC Score  : {auc:.3f}")

    print("\nConfusion Matrix")
    print(cm)

    print("\nFeature Importance")
    print("--------------------------------")

    importances = ml_model.model.feature_importances_

    for feature, score in zip(feature_cols, importances):
        print(f"{feature:<20} : {score:.3f}")

    # ------------------------------------------------
    # SHAP EXPLAINABILITY
    # ------------------------------------------------

    print("\nGenerating SHAP Explainability...")

    plot_shap_summary(ml_model, X)
    plot_shap_waterfall(ml_model, X)

    # ------------------------------------------------
    # BUSINESS INTELLIGENCE ENGINES
    # ------------------------------------------------

    ml_probs = ml_model.predict_probs(X)

    intel = AdaptiveIntelligenceEngine()
    health = BusinessHealthEngine()
    forecaster = RevenueForecaster()
    pricing = HeuristicPricingOptimizer()
    clv = CLVEngine()

    client_stats['STAGE'] = client_stats.apply(
        intel.predict_lifecycle,
        axis=1
    )

    risks = []

    for i in range(len(client_stats)):

        risk = intel.calculate_hybrid_risk(
            client_stats.iloc[i],
            ml_probs[i]
        )

        risks.append(risk)

    client_stats['RISK_%'] = risks

    client_stats['PREDICTIVE_CLV'] = client_stats.apply(
        clv.estimate_predictive_clv,
        axis=1
    )

    client_stats['PRICE_STRATEGY'] = client_stats.apply(
        pricing.suggest_adjustment,
        axis=1
    )

    burnout = health.calculate_burnout_risk(client_stats)

    profit_forecast = forecaster.forecast(
        monthly_stats['net_cash_flow']
    )

    risk_engine = BusinessRiskEngine()
    
    business_risk_score = risk_engine.calculate_risk_score(
       client_stats,
       monthly_stats,
       burnout,
       profit_forecast
    )

    risk_status = risk_engine.risk_status(business_risk_score)
    

    return {
        "burnout": burnout,
        "forecast": profit_forecast,
        "clients": client_stats,
        "monthly": monthly_stats,
        "business_risk_score": business_risk_score,
        "risk_status": risk_status,
        "ml_confidence": "High" if ml_model.is_trained else "Low"
    }

# -------------------------------------------------------
# DASHBOARD
# -------------------------------------------------------

def display_dashboard():

    data = run_analysis_service()

    print("\n" + "═" * 110)

    print(
        f"🛡️ RISK INTELLIGENCE REPORT | 🔥 BURNOUT: {data['burnout']}% | 🧠 ML CONFIDENCE: {data['ml_confidence']}"
    )

    forecast_vals = data['forecast']

    if len(forecast_vals) >= 3:

        print(
            f"📈 90-DAY PROFIT FORECAST: "
            f"${forecast_vals[0]:,.0f} -> "
            f"${forecast_vals[1]:,.0f} -> "
            f"${forecast_vals[2]:,.0f}"
        )

    print("═" * 110)

    print("\n📬 PRIORITY ACTION INBOX (Top High-Impact Tasks):")

    clients = data['clients']

    critical_clients = clients[
        clients['RISK_%'] > 40
    ].sort_values(
        'PREDICTIVE_CLV',
        ascending=False
    )

    if not critical_clients.empty:

        top_c = critical_clients.index[0]
        clv_val = critical_clients.loc[top_c, 'PREDICTIVE_CLV']
        stage = critical_clients.loc[top_c, 'STAGE']

        print(
            f"[!] RECOVER: Client {top_c} has high CLV (${clv_val:,.0f}) but is {stage}. Immediate retention needed."
        )

    if data['burnout'] > 65:

        print(
            f"[!] CAPACITY: Burnout Risk is Critical ({data['burnout']}%). Pause new projects temporarily."
        )

    upsell_target = clients[
        (clients['STAGE'] == 'STABLE') &
        (clients['RISK_%'] < 15)
    ]

    if not upsell_target.empty:

        print(
            f"[!] REVENUE: Client {upsell_target.index[0]} is highly stable. Ideal for a rate increase."
        )

    print("\nCLIENT PERFORMANCE TABLE")
    print("═" * 110)

    top_clients = clients.sort_values(
        'PREDICTIVE_CLV',
        ascending=False
    ).head(10)

    table = top_clients[
        ['STAGE', 'RISK_%', 'PREDICTIVE_CLV', 'PRICE_STRATEGY']
    ].copy()

    table['RISK_%'] = table['RISK_%'].map(lambda x: f"{x:.0f}%")
    table['PREDICTIVE_CLV'] = table['PREDICTIVE_CLV'].map(lambda x: f"${x:,.0f}")

    print(table)

    print("\n" + "═" * 110)

    plot_advanced_health(
        data['monthly'],
        data['forecast'],
        data['burnout']
    )

    plot_risk_distribution(data['clients'])


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

if __name__ == "__main__":

    display_dashboard()