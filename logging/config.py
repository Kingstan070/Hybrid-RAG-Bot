# logging/config.py
import logging
from pathlib import Path
from datetime import datetime


def get_logger(name: str, level=logging.INFO):
    """Create a modular logger for any module."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_path = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        fh = logging.FileHandler(file_path)
        sh = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        fh.setFormatter(formatter)
        sh.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(sh)

    return logger
