"""Teste end-to-end usando SQLite."""
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from etl.config import Settings
from etl.pipeline import run_pipeline


def test_pipeline_end_to_end(sample_csv, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = Settings(
        etl_input=str(sample_csv),
        etl_target="sqlite",
        etl_table="clientes_test",
        etl_mode="replace",
        etl_sqlite_path=str(tmp_path / "etl.db"),
        etl_logs_dir=str(tmp_path / "logs"),
        etl_rejected_dir=str(tmp_path / "rejected"),
        etl_snapshots_dir=str(tmp_path / "snapshots"),
        etl_parquet_dir=str(tmp_path / "out"),
        etl_validate_mx=False,
    )
    metrics = run_pipeline(cfg, show_preview=False)
    assert metrics.status == "success"
    assert metrics.rows_in == 7
    assert metrics.rows_rejected >= 3
    assert metrics.rows_out > 0

    engine = create_engine(cfg.sqlite_url, future=True)
    with engine.connect() as conn:
        rows = pd.read_sql(text('SELECT * FROM clientes_test'), conn)
    assert len(rows) == metrics.rows_out

    # snapshot existe
    assert any(Path(cfg.etl_snapshots_dir).glob("clientes_test_*.parquet"))
    # rejeitados gravados
    assert any(Path(cfg.etl_rejected_dir).glob("rejected_*.csv"))
