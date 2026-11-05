import pandas as pd


def extract_excel(filepath: str, sheet_name: str | int = 0) -> pd.DataFrame:
    return pd.read_excel(filepath, sheet_name=sheet_name)
