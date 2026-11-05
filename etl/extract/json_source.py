import pandas as pd


def extract_json(filepath: str, lines: bool = False) -> pd.DataFrame:
    return pd.read_json(filepath, lines=lines)
