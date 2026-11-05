import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler

_configured = False


def setup_logging(logs_dir: str = "logs", level: int = logging.INFO) -> logging.Logger:
    global _configured
    logger = logging.getLogger("etl")
    if _configured:
        return logger

    Path(logs_dir).mkdir(parents=True, exist_ok=True)
    logger.setLevel(level)
    logger.propagate = False

    file_handler = RotatingFileHandler(
        Path(logs_dir) / "etl.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    )
    logger.addHandler(file_handler)

    rich_handler = RichHandler(rich_tracebacks=True, show_path=False, markup=True)
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(rich_handler)

    _configured = True
    return logger
