from __future__ import annotations

import logging
from datetime import UTC, datetime

from .config import Settings, settings as default_settings
from .enrich import enrich
from .extract import extract
from .load import load
from .logging_setup import setup_logging
from .metrics import RunMetrics, save_run
from .quality import RejectionReport
from .snapshot import save_snapshot
from .transform import transform
from .utils import new_run_id, preview
from .validate import validate_raw

log = logging.getLogger("etl.pipeline")


def run_pipeline(cfg: Settings | None = None, *, show_preview: bool = True) -> RunMetrics:
    cfg = cfg or default_settings
    cfg.ensure_dirs()
    setup_logging(cfg.etl_logs_dir)

    run_id = new_run_id()
    metrics = RunMetrics(
        run_id=run_id,
        source=cfg.etl_input,
        target=cfg.etl_target,
        table=cfg.etl_table,
        mode=cfg.etl_mode,
        started_at=datetime.now(UTC),
    )
    log.info(f"[bold cyan]==> Run {run_id} iniciado[/]")

    try:
        df = extract(cfg.etl_input)
        metrics.rows_in = len(df)
        df = validate_raw(df)

        report = RejectionReport(run_id=run_id, output_dir=cfg.etl_rejected_dir)
        df = transform(df, report)
        df = enrich(
            df,
            validate_mx=cfg.etl_validate_mx,
            detect_anomaly=cfg.etl_detect_anomalies,
            z_threshold=cfg.etl_anomaly_zscore,
        )
        report.save()
        metrics.rows_rejected = report.total
        metrics.rejection_summary = report.summary()

        if show_preview:
            preview(df, title=f"Preview run {run_id}")

        target_url = _resolve_url(cfg)
        load_stats = load(
            df,
            target=cfg.etl_target,
            table=cfg.etl_table,
            mode=cfg.etl_mode,
            connection_url=target_url,
            parquet_dir=cfg.etl_parquet_dir,
        )
        metrics.rows_out = len(df)
        metrics.rows_inserted = load_stats.inserted
        metrics.rows_updated = load_stats.updated

        save_snapshot(df, table=cfg.etl_table, directory=cfg.etl_snapshots_dir)
        metrics.finish(status="success")
    except Exception as exc:
        log.exception("pipeline falhou")
        metrics.finish(status="failed", error=str(exc))
        if _metrics_url(cfg):
            save_run(metrics, _metrics_url(cfg))
        raise

    if _metrics_url(cfg):
        save_run(metrics, _metrics_url(cfg))
    log.info(
        f"[bold green]✓ Run {run_id} concluído em {metrics.duration_seconds:.2f}s "
        f"(in={metrics.rows_in} out={metrics.rows_out} rej={metrics.rows_rejected})[/]"
    )
    return metrics


def _resolve_url(cfg: Settings) -> str | None:
    if cfg.etl_target == "postgres":
        return cfg.postgres_url
    if cfg.etl_target == "sqlite":
        return cfg.sqlite_url
    return None


def _metrics_url(cfg: Settings) -> str | None:
    if cfg.etl_target in ("postgres", "sqlite"):
        return _resolve_url(cfg)
    return cfg.sqlite_url
