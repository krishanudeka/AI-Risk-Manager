import pandas as pd
import os

TX_FILE = "uploads/manual_transactions.csv"
INV_FILE = "uploads/manual_invoices.csv"


# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)


# --------------------------------------------------
# ADD TRANSACTION
# --------------------------------------------------

def add_transaction(client_id, amount, date, ttype="income", category="Service"):

    row = {
        "client_id": client_id,
        "amount": float(amount),
        "date": pd.to_datetime(date),
        "type": ttype,
        "category": category
    }

    df_new = pd.DataFrame([row])

    if os.path.exists(TX_FILE):
        df_old = pd.read_csv(TX_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(TX_FILE, index=False)

    return df


# --------------------------------------------------
# ADD INVOICE
# --------------------------------------------------

def add_invoice(client_id, due_date, paid_date, amount):

    invoice_id = f"INV_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"

    row = {
        "invoice_id": invoice_id,
        "client_id": client_id,
        "due_date": pd.to_datetime(due_date),
        "paid_date": pd.to_datetime(paid_date),
        "amount": float(amount)
    }

    df_new = pd.DataFrame([row])

    if os.path.exists(INV_FILE):
        df_old = pd.read_csv(INV_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(INV_FILE, index=False)

    return df


# --------------------------------------------------
# LOAD MANUAL DATA
# --------------------------------------------------

def load_manual_data():

    if not os.path.exists(TX_FILE):
        raise ValueError("No manual transactions found. Add transactions first.")

    tx_df = pd.read_csv(TX_FILE)

    if os.path.exists(INV_FILE):
        inv_df = pd.read_csv(INV_FILE)
    else:
        inv_df = pd.DataFrame(columns=[
            "invoice_id",
            "client_id",
            "due_date",
            "paid_date",
            "amount"
        ])

    return tx_df, inv_df

def reset_manual_data():

    import os

    if os.path.exists("uploads/manual_transactions.csv"):
        os.remove("uploads/manual_transactions.csv")

    if os.path.exists("uploads/manual_invoices.csv"):
        os.remove("uploads/manual_invoices.csv")

    print("Manual data cleared.")