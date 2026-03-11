import pandas as pd


def validate_transactions(df):

    required = ["client_id", "amount", "date"]

    for col in required:

        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # convert date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # convert amount
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # remove invalid rows
    df = df.dropna(subset=["client_id", "amount", "date"])

    # remove duplicates
    df = df.drop_duplicates()

    # defaults
    if "type" not in df.columns:
        df["type"] = "income"

    if "category" not in df.columns:
        df["category"] = "Service"

    df = df.sort_values("date")

    return df