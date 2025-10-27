# app/core/logger.py
import logging
import sys

from app.core.config import settings


def setup_logger(name: str = "marc-ai") -> logging.Logger:
    """
    Configure structured logging for the application.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logger()
