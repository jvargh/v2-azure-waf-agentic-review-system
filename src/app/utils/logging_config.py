"""Centralized logging configuration for all Well-Architected pillar agents.

This module provides a single initialization point so that individual agent
CLIs do not need to duplicate logging setup logic. Configuration is driven
by environment variables to allow easy tuning without code changes.

Environment Variables:
- AGENT_LOG_LEVEL: Root log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO.
- AGENT_LOG_VERBOSE: If '1', do not suppress noisy Azure/async loggers. Default: '0'.
- AGENT_LOG_FORMAT: Optional override for log format.

Usage:
    from src.app.utils.logging_config import init_logging
    init_logging()

Calling init_logging() multiple times is safe (idempotent).
"""
from __future__ import annotations

import logging
import os
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
    """Initialize root logging configuration.

    Args:
        force: If True, reconfigure even if already initialized. Use sparingly.
    """
    global _INITIALIZED
    if _INITIALIZED and not force:
        return

    level_name = os.getenv("AGENT_LOG_LEVEL", "INFO").upper().strip()
    level = getattr(logging, level_name, logging.INFO)
    log_format = os.getenv("AGENT_LOG_FORMAT", DEFAULT_FORMAT)
    verbose = os.getenv("AGENT_LOG_VERBOSE", "0") == "1"

    root = logging.getLogger()
    # Only configure if no handlers OR force requested
    if force or not root.handlers:
        logging.basicConfig(level=level, format=log_format)

    # If DEBUG level is set OR verbose flag is 1, show all logs including Azure SDK
    if not verbose and level > logging.DEBUG:
        for name in NOISY_LOGGERS:
            logging.getLogger(name).setLevel(logging.WARNING)

    _INITIALIZED = True

__all__ = ["init_logging"]
