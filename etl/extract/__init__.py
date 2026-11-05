from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from .csv_source import extract_csv
from .excel_source import extract_excel
from .http_source import extract_http
from .json_source import extract_json
from .parquet_source import extract_parquet

log = logging.getLogger("etl.extract")


def extract(source: str) -> pd.DataFrame:
    log.info(f"→ Extraindo: [bold]{source}[/]")

    parsed = urlparse(source)
    if parsed.scheme in ("http", "https"):
        df = extract_http(source)
    else:
        ext = Path(source).suffix.lower().lstrip(".")
        readers = {
            "csv": extract_csv,
            "tsv": lambda p: extract_csv(p, sep="\t"),
            "xlsx": extract_excel,
            "xls": extract_excel,
            "json": extract_json,
            "jsonl": lambda p: extract_json(p, lines=True),
            "parquet": extract_parquet,
            "pq": extract_parquet,
        }
        if ext not in readers:
            raise ValueError(f"Formato não suportado: {ext!r}")
        df = readers[ext](source)

    log.info(f"✓ {len(df)} linhas extraídas")
    return df


__all__ = ["extract"]
