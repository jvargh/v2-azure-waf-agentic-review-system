# Migrated from src.app.utils.logging_config
from __future__ import annotations
import logging, os
from typing import Iterable
DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
NOISY_LOGGERS: Iterable[str] = (
    "azure.core.pipeline.policies.http_logging_policy",
    "azure.identity",
    "azure.monitor",
    "agent_framework",
    "asyncio",
)
_INITIALIZED = False

def init_logging(force: bool = False) -> None:
    global _INITIALIZED
    if _INITIALIZED and not force:
        return
    level_name = os.getenv("AGENT_LOG_LEVEL", "INFO").upper().strip()
    level = getattr(logging, level_name, logging.INFO)
    log_format = os.getenv("AGENT_LOG_FORMAT", DEFAULT_FORMAT)
    verbose = os.getenv("AGENT_LOG_VERBOSE", "0") == "1"
    root = logging.getLogger()
    if force or not root.handlers:
        logging.basicConfig(level=level, format=log_format)
    if not verbose and level > logging.DEBUG:
        for name in NOISY_LOGGERS:
            logging.getLogger(name).setLevel(logging.WARNING)
    _INITIALIZED = True
__all__ = ["init_logging"]
