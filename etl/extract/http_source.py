from io import BytesIO, StringIO

import pandas as pd
import requests


def extract_http(url: str, timeout: int = 30) -> pd.DataFrame:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    ctype = resp.headers.get("content-type", "").lower()

    if "json" in ctype or url.endswith(".json"):
        return pd.read_json(StringIO(resp.text))
    if "parquet" in ctype or url.endswith(".parquet"):
        return pd.read_parquet(BytesIO(resp.content))
    if "excel" in ctype or url.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(resp.content))
    return pd.read_csv(StringIO(resp.text))
