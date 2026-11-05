from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .sql_target import LoadStats

log = logging.getLogger("etl.load.parquet")


def load_parquet(df: pd.DataFrame, *, directory: str, table: str, mode: str) -> LoadStats:
    out_dir = Path(directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{table}.parquet"
    stats = LoadStats()

    if mode == "replace" or not path.exists():
        df.to_parquet(path, index=False)
        stats.inserted = len(df)
        stats.replaced = mode == "replace"
        log.info(f"✓ {len(df)} linhas escritas em {path}")
        return stats

    existing = pd.read_parquet(path)
    if mode == "append":
        combined = pd.concat([existing, df], ignore_index=True)
        stats.inserted = len(df)
    else:
        combined = pd.concat([existing, df], ignore_index=True).drop_duplicates(
            subset=["id"], keep="last"
        )
        stats.inserted = len(combined) - len(existing)
        stats.updated = len(df) - stats.inserted

    combined.to_parquet(path, index=False)
    log.info(f"✓ inseridas={stats.inserted} atualizadas={stats.updated} em {path}")
    return stats
