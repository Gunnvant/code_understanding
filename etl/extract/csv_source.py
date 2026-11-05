import pandas as pd


def extract_csv(filepath: str, sep: str = ",") -> pd.DataFrame:
    return pd.read_csv(filepath, sep=sep)
