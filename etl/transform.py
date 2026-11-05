from __future__ import annotations

import logging

import pandas as pd

from .quality import RejectionReport

log = logging.getLogger("etl.transform")

EMAIL_RE = r"^[^@]+@[^@]+\.[^@]+$"


def transform(df: pd.DataFrame, report: RejectionReport) -> pd.DataFrame:
    log.info("→ Transformando...")
    df = df.copy()

    missing_mask = df["nome"].isna() | df["email"].isna()
    if missing_mask.any():
        report.add(df[missing_mask], "nome_ou_email_vazio")
        df = df[~missing_mask]

    dup_email = df.duplicated(subset=["email"], keep="first")
    if dup_email.any():
        report.add(df[dup_email], "duplicata_email")
        df = df[~dup_email]

    dup_id = df.duplicated(subset=["id"], keep="first")
    if dup_id.any():
        report.add(df[dup_id], "duplicata_id")
        df = df[~dup_id]

    df["nome"] = df["nome"].astype(str).str.strip().str.title()
    df["cidade"] = df["cidade"].astype(str).str.strip().str.title()

    email_mask = df["email"].astype(str).str.match(EMAIL_RE, na=False)
    if (~email_mask).any():
        report.add(df[~email_mask], "email_invalido")
        df = df[email_mask]

    df["telefone"] = df["telefone"].astype(str).str.replace(r"\D", "", regex=True)
    df["telefone"] = df["telefone"].replace({"": None, "nan": None, "None": None})

    df["valor_compra"] = (
        df["valor_compra"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
        .replace({"nan": None, "None": None, "": None})
    )
    df["valor_compra"] = pd.to_numeric(df["valor_compra"], errors="coerce")

    negative_mask = df["valor_compra"] < 0
    if negative_mask.any():
        report.add(df[negative_mask], "valor_negativo")
        df = df[~negative_mask]

    df["data_compra"] = pd.to_datetime(df["data_compra"], errors="coerce", format="mixed")

    log.info(f"✓ {len(df)} linhas após transformação")
    return df.reset_index(drop=True)
