from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np
import pandas as pd

log = logging.getLogger("etl.enrich")


@lru_cache(maxsize=4096)
def _has_mx(domain: str) -> bool:
    try:
        import dns.resolver

        answers = dns.resolver.resolve(domain, "MX", lifetime=3.0)
        return len(answers) > 0
    except Exception:
        return False


def validate_email_mx(df: pd.DataFrame) -> pd.DataFrame:
    log.info("→ Validando MX de emails (pode ser lento)...")
    domains = df["email"].astype(str).str.split("@").str[-1].str.lower()
    df = df.copy()
    df["email_mx_valid"] = domains.apply(_has_mx)
    invalid = (~df["email_mx_valid"]).sum()
    log.info(f"  emails com MX inválido: {invalid}")
    return df


def detect_anomalies(df: pd.DataFrame, column: str = "valor_compra", z_threshold: float = 3.0) -> pd.DataFrame:
    df = df.copy()
    df["is_anomaly"] = False
    series = df[column].dropna()
    if len(series) < 5:
        return df
    mean, std = series.mean(), series.std(ddof=0)
    if std == 0 or np.isnan(std):
        return df
    zscores = (df[column] - mean).abs() / std
    df["is_anomaly"] = (zscores > z_threshold).fillna(False)
    flagged = df["is_anomaly"].sum()
    if flagged:
        log.info(f"  anomalias detectadas em {column}: {flagged} (z>{z_threshold})")
    return df


def enrich(
    df: pd.DataFrame,
    *,
    validate_mx: bool = False,
    detect_anomaly: bool = True,
    z_threshold: float = 3.0,
) -> pd.DataFrame:
    if validate_mx:
        df = validate_email_mx(df)
    if detect_anomaly:
        df = detect_anomalies(df, z_threshold=z_threshold)
    return df
