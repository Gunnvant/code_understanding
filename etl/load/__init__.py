from __future__ import annotations

import logging
from typing import Literal

import pandas as pd

from .parquet_target import load_parquet
from .sql_target import LoadStats, load_sql

log = logging.getLogger("etl.load")

Target = Literal["postgres", "sqlite", "parquet"]
Mode = Literal["replace", "append", "upsert"]


def load(
    df: pd.DataFrame,
    *,
    target: Target,
    table: str,
    mode: Mode,
    connection_url: str | None = None,
    parquet_dir: str | None = None,
    pk: str = "id",
) -> LoadStats:
    log.info(f"→ Carregando [bold]{target}[/]:[bold]{table}[/] (modo={mode})")
    if target == "parquet":
        if not parquet_dir:
            raise ValueError("parquet_dir é obrigatório quando target=parquet")
        return load_parquet(df, directory=parquet_dir, table=table, mode=mode)
    if target in ("postgres", "sqlite"):
        if not connection_url:
            raise ValueError("connection_url é obrigatório para targets SQL")
        return load_sql(df, url=connection_url, table=table, mode=mode, pk=pk)
    raise ValueError(f"target inválido: {target!r}")


__all__ = ["load", "LoadStats"]
