import pandas as pd


def extract_parquet(filepath: str) -> pd.DataFrame:
    return pd.read_parquet(filepath)
