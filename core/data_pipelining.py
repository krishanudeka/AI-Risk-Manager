import pandas as pd
import numpy as np


# ------------------------------------------------
# CHURN LABEL GENERATION
# ------------------------------------------------

def generate_churn_label(df):

    df["churn_label"] = (
        (df["recency"] > 90) |
        (df["revenue_drop_ratio"] < 0.5) |
        ((df["payment_count"] < 3) & (df["recency"] > 45))
    ).astype(int)

    return df


# ------------------------------------------------
# ADAPTIVE DATA PIPELINE
# ------------------------------------------------

class AdaptiveDataPipeline:

    def __init__(self, tx_path=None, client_path=None, invoice_path=None,
                 tx_df=None, client_df=None, invoice_df=None):

        self.tx_path = tx_path
        self.client_path = client_path
        self.invoice_path = invoice_path

        self.tx_df = tx_df
        self.client_df = client_df
        self.invoice_df = invoice_df


    def process(self):

        # ------------------------------------------------
        # LOAD TRANSACTIONS
        # ------------------------------------------------

        if self.tx_df is not None:
            df_tx = self.tx_df.copy()
        else:
            df_tx = pd.read_csv(self.tx_path)

        df_tx = df_tx.drop_duplicates()

        df_tx = df_tx.dropna(subset=["client_id", "amount"])

        df_tx["date"] = pd.to_datetime(df_tx["date"], errors="coerce")

        df_tx = df_tx.dropna(subset=["date"])


        # Safety fallback for missing columns
        if "type" not in df_tx.columns:
            df_tx["type"] = "income"

        if "category" not in df_tx.columns:
            df_tx["category"] = "Service"


        # ------------------------------------------------
        # LOAD INVOICES
        # ------------------------------------------------

        if self.invoice_df is not None:

            df_inv = self.invoice_df.copy()

        elif self.invoice_path is not None:

            df_inv = pd.read_csv(self.invoice_path)

        else:
            # Auto-generate invoices if missing
            df_inv = df_tx.copy()

            df_inv["invoice_id"] = [
                f"INV_{i}" for i in range(len(df_inv))
            ]

            df_inv["due_date"] = df_inv["date"] - pd.Timedelta(days=30)

            df_inv["paid_date"] = df_inv["date"]

            df_inv = df_inv[[
                "invoice_id",
                "client_id",
                "due_date",
                "paid_date",
                "amount"
            ]]


        df_inv["paid_date"] = pd.to_datetime(df_inv["paid_date"], errors="coerce")
        df_inv["due_date"] = pd.to_datetime(df_inv["due_date"], errors="coerce")

        df_inv = df_inv.dropna(subset=["paid_date", "due_date"])

        df_inv["delay"] = (df_inv["paid_date"] - df_inv["due_date"]).dt.days

        avg_delays = df_inv.groupby("client_id")["delay"].mean().fillna(0)


        # ------------------------------------------------
        # FEATURE ENGINEERING
        # ------------------------------------------------

        income_df = df_tx[df_tx["type"] == "income"].sort_values(
            ["client_id", "date"]
        )

        if income_df.empty:
            raise ValueError("No income transactions found.")


        total_biz_revenue = income_df["amount"].sum()

        today = df_tx["date"].max()


        def compute_features(group):

            n = len(group)

            total_rev = group["amount"].sum()

            rev_share = (total_rev / (total_biz_revenue + 1e-9)) * 100

            gaps = group["date"].diff().dt.days

            avg_gap = gaps.mean() if n > 1 else 30

            recency = (today - group["date"].max()).days


            # ---- volatility

            volatility = gaps.std()

            if pd.isna(volatility):
                volatility = 0

            volatility = volatility / (avg_gap + 1)


            # ---- revenue trend

            revenue_trend = 0

            if n >= 3:

                try:

                    revenue_trend = np.polyfit(
                        np.arange(n),
                        group["amount"],
                        1
                    )[0]

                except:
                    revenue_trend = 0


            # ---- revenue drop

            drop_ratio = 1

            if n >= 4:

                recent = group["amount"].tail(2).mean()
                older = group["amount"].iloc[:-2].mean()

                drop_ratio = recent / (older + 1e-9)


            return pd.Series({

                "total_revenue": total_rev,
                "revenue_share_%": rev_share,
                "payment_count": n,
                "avg_gap": avg_gap,
                "recency": recency,
                "volatility": volatility,
                "revenue_trend": revenue_trend,
                "revenue_drop_ratio": drop_ratio

            })

        # ------------------------------------------------
        # CLIENT AGGREGATION
        # ------------------------------------------------

        client_stats = income_df.groupby(
            "client_id",
            group_keys=False
        ).apply(compute_features)

        # IMPORTANT: bring client_id back as column
        client_stats = client_stats.reset_index()

        # ------------------------------------------------
        # ADD PAYMENT DELAYS
        # ------------------------------------------------

        client_stats["avg_payment_delay"] = client_stats["client_id"].map(
            avg_delays
        ).fillna(0)


        client_stats = generate_churn_label(client_stats)


        print("\nChurn Distribution")
        print(client_stats["churn_label"].value_counts())


        # ------------------------------------------------
        # MONTHLY AGGREGATION (FIXED)
        # ------------------------------------------------

        # Revenue per month (income only)
        revenue_monthly = (
            df_tx[df_tx["type"] == "income"]
            .resample("MS", on="date")["amount"]
            .sum()
        )

        # Expenses per month
        expenses_monthly = (
            df_tx[df_tx["type"] == "expense"]
            .resample("MS", on="date")["amount"]
            .sum()
        )

        # Combine into one dataframe
        monthly_stats = pd.DataFrame({
            "revenue": revenue_monthly,
            "expenses": expenses_monthly
        })

        monthly_stats = monthly_stats.fillna(0)

        # Net cash flow
        monthly_stats["net_cash_flow"] = (
            monthly_stats["revenue"] - monthly_stats["expenses"]
        )

        return monthly_stats, client_stats