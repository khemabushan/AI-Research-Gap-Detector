"""
Application-wide logging setup. Called once at startup from main.py.
"""
import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    # Quiet down noisy third-party loggers unless we're debugging.
    if level > logging.DEBUG:
        for noisy_logger in ("httpx", "sentence_transformers", "faiss"):
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)
