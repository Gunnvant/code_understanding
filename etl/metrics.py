from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

import pandas as pd
from sqlalchemy import create_engine, text

log = logging.getLogger("etl.metrics")


@dataclass
class RunMetrics:
    run_id: str
    source: str
    target: str
    table: str
    mode: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_seconds: float = 0.0
    rows_in: int = 0
    rows_out: int = 0
    rows_rejected: int = 0
    rows_inserted: int = 0
    rows_updated: int = 0
    status: str = "running"
    error: str | None = None
    rejection_summary: dict = field(default_factory=dict)

    def finish(self, status: str = "success", error: str | None = None) -> None:
        self.finished_at = datetime.now(UTC)
        self.duration_seconds = (self.finished_at - self.started_at).total_seconds()
        self.status = status
        self.error = error

    def to_row(self) -> dict:
        d = asdict(self)
        d["started_at"] = self.started_at.isoformat()
        d["finished_at"] = self.finished_at.isoformat() if self.finished_at else None
        d["rejection_summary"] = json.dumps(self.rejection_summary)
        return d


def save_run(metrics: RunMetrics, url: str, table: str = "etl_runs") -> None:
    engine = create_engine(url, future=True)
    df = pd.DataFrame([metrics.to_row()])
    try:
        with engine.begin() as conn:
            df.to_sql(table, conn, if_exists="append", index=False)
        log.info(f"métricas gravadas em {table} (run_id={metrics.run_id})")
    except Exception as exc:
        log.error(f"falha gravando métricas: {exc}")


def read_runs(url: str, table: str = "etl_runs", limit: int = 100) -> pd.DataFrame:
    engine = create_engine(url, future=True)
    try:
        with engine.connect() as conn:
            return pd.read_sql(
                text(f'SELECT * FROM "{table}" ORDER BY started_at DESC LIMIT :lim'),
                conn,
                params={"lim": limit},
            )
    except Exception:
        return pd.DataFrame()
