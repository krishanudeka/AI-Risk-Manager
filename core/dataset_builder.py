import pandas as pd


def build_datasets_from_transactions(df_tx):

    df_tx = df_tx.copy()

    # -------------------------------------
    # CLIENTS DATASET
    # -------------------------------------

    clients = df_tx["client_id"].dropna().unique()

    df_clients = pd.DataFrame({
        "client_id": clients
    })

    df_clients["industry"] = "Unknown"
    df_clients["contract_type"] = "Project"

    # estimate base value from avg revenue
    avg_revenue = (
        df_tx.groupby("client_id")["amount"]
        .mean()
        .reset_index()
    )

    avg_revenue.rename(
        columns={"amount": "base_value"},
        inplace=True
    )

    df_clients = df_clients.merge(
        avg_revenue,
        on="client_id",
        how="left"
    )

    df_clients["base_value"] = df_clients["base_value"].fillna(0)

    # -------------------------------------
    # INVOICE DATASET
    # -------------------------------------

    df_inv = df_tx.copy()

    df_inv["invoice_id"] = [
        f"INV_{i+1}" for i in range(len(df_inv))
    ]

    df_inv["due_date"] = pd.to_datetime(df_inv["date"])

    df_inv["paid_date"] = pd.to_datetime(df_inv["date"])

    df_inv = df_inv[[
        "invoice_id",
        "client_id",
        "due_date",
        "paid_date",
        "amount"
    ]]

    return df_clients, df_inv