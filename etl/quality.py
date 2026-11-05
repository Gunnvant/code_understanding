from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger("etl.quality")


class RejectionReport:
    def __init__(self, run_id: str, output_dir: str = "rejected"):
        self.run_id = run_id
        self.output_dir = Path(output_dir)
        self._chunks: list[pd.DataFrame] = []

    def add(self, df: pd.DataFrame, reason: str) -> None:
        if df.empty:
            return
        chunk = df.copy()
        chunk["_reason"] = reason
        chunk["_run_id"] = self.run_id
        self._chunks.append(chunk)
        log.warning(f"rejeitadas ({reason}): {len(chunk)}")

    @property
    def total(self) -> int:
        return sum(len(c) for c in self._chunks)

    def to_dataframe(self) -> pd.DataFrame:
        if not self._chunks:
            return pd.DataFrame()
        return pd.concat(self._chunks, ignore_index=True)

    def save(self) -> Path | None:
        if not self._chunks:
            return None
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"rejected_{self.run_id}.csv"
        self.to_dataframe().to_csv(path, index=False)
        log.info(f"relatório de rejeitadas salvo em: {path}")
        return path

    def summary(self) -> dict[str, int]:
        if not self._chunks:
            return {}
        return self.to_dataframe()["_reason"].value_counts().to_dict()
