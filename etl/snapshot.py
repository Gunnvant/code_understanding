from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

log = logging.getLogger("etl.snapshot")


def save_snapshot(df: pd.DataFrame, *, table: str, directory: str = "snapshots") -> Path:
    out_dir = Path(directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"{table}_{ts}.parquet"
    df.to_parquet(path, index=False)
    log.info(f"snapshot salvo: {path}")
    return path


def list_snapshots(table: str, directory: str = "snapshots") -> list[Path]:
    out_dir = Path(directory)
    if not out_dir.exists():
        return []
    return sorted(out_dir.glob(f"{table}_*.parquet"))
