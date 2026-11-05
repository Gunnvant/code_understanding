import hashlib
import uuid
from datetime import UTC, datetime

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()


def preview(df: pd.DataFrame, title: str = "Preview", rows: int = 5) -> None:
    table = Table(title=title)
    for col in df.columns:
        table.add_column(col)
    for _, row in df.head(rows).iterrows():
        table.add_row(*[str(v) for v in row])
    console.print(table)


def new_run_id() -> str:
    return f"{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"


def row_hash(row: pd.Series, columns: list[str] | None = None) -> str:
    cols = columns or list(row.index)
    payload = "|".join(str(row[c]) for c in cols)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def add_row_hash(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    cols = columns or [c for c in df.columns if c != "row_hash"]
    df = df.copy()
    df["row_hash"] = df.apply(lambda r: row_hash(r, cols), axis=1)
    return df
