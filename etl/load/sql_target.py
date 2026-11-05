from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from ..utils import add_row_hash

log = logging.getLogger("etl.load.sql")


@dataclass
class LoadStats:
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    replaced: bool = False

    @property
    def total_written(self) -> int:
        return self.inserted + self.updated


def _engine(url: str) -> Engine:
    return create_engine(url, future=True)


def _retry(fn, attempts: int = 3, base_delay: float = 0.5):
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:
            if i == attempts - 1:
                raise
            wait = base_delay * (2**i)
            log.warning(f"tentativa {i + 1} falhou ({exc}); retry em {wait:.1f}s")
            time.sleep(wait)


def load_sql(
    df: pd.DataFrame,
    *,
    url: str,
    table: str,
    mode: str,
    pk: str = "id",
) -> LoadStats:
    if pk not in df.columns:
        raise ValueError(f"PK {pk!r} não encontrada no DataFrame")

    df = add_row_hash(df, columns=[c for c in df.columns if c != "row_hash"])
    engine = _engine(url)
    stats = LoadStats()

    def _run() -> LoadStats:
        with engine.begin() as conn:
            if mode == "replace":
                df.to_sql(table, conn, if_exists="replace", index=False)
                stats.replaced = True
                stats.inserted = len(df)
                return stats

            if not inspect(conn).has_table(table):
                df.to_sql(table, conn, if_exists="fail", index=False)
                stats.inserted = len(df)
                return stats

            if mode == "append":
                df.to_sql(table, conn, if_exists="append", index=False)
                stats.inserted = len(df)
                return stats

            existing = pd.read_sql(text(f'SELECT {pk}, row_hash FROM "{table}"'), conn)
            existing_map = dict(zip(existing[pk], existing["row_hash"], strict=False))

            new_rows: list[dict] = []
            changed_rows: list[dict] = []
            for record in df.to_dict(orient="records"):
                pk_val = record[pk]
                prev = existing_map.get(pk_val)
                if prev is None:
                    new_rows.append(record)
                elif prev != record["row_hash"]:
                    changed_rows.append(record)
                else:
                    stats.unchanged += 1

            if new_rows:
                pd.DataFrame(new_rows).to_sql(table, conn, if_exists="append", index=False)
                stats.inserted = len(new_rows)
            if changed_rows:
                cols = [c for c in df.columns if c != pk]
                set_clause = ", ".join(f'"{c}" = :{c}' for c in cols)
                stmt = text(f'UPDATE "{table}" SET {set_clause} WHERE "{pk}" = :{pk}')
                conn.execute(stmt, changed_rows)
                stats.updated = len(changed_rows)
        return stats

    result = _retry(_run)
    log.info(
        f"✓ inseridas={result.inserted} atualizadas={result.updated} "
        f"inalteradas={result.unchanged} (replace={result.replaced})"
    )
    return result
