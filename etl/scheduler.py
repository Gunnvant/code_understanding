from __future__ import annotations

import logging
import signal
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import settings
from .logging_setup import setup_logging
from .pipeline import run_pipeline

log = logging.getLogger("etl.scheduler")


def _safe_run() -> None:
    try:
        run_pipeline(settings)
    except Exception as exc:
        log.error(f"run falhou: {exc}")


def start_scheduler(cron: str) -> None:
    setup_logging(settings.etl_logs_dir)
    log.info(f"agendando: '{cron}'")
    sched = BackgroundScheduler()
    sched.add_job(_safe_run, CronTrigger.from_crontab(cron), id="etl_run")
    sched.start()
    log.info("scheduler ativo. Ctrl+C para sair.")

    stopping = {"flag": False}

    def _stop(*_):
        stopping["flag"] = True

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    while not stopping["flag"]:
        time.sleep(1)
    sched.shutdown(wait=False)
    log.info("scheduler encerrado")
