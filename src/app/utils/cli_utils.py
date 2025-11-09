"""Shared CLI utilities for Well-Architected pillar agents.

Provides consistent argument parsing and optional log-level override
so individual agent CLIs don't duplicate boilerplate.
"""
from __future__ import annotations

import argparse
import os
from typing import Optional


def create_agent_argument_parser(pillar_name: str) -> argparse.ArgumentParser:
    """Create standard argument parser for a pillar agent CLI.

    Args:
        pillar_name: Display name of the pillar (e.g., "Reliability", "Cost Optimization").

    Returns:
        Configured ArgumentParser with architecture_file, --cases, --log-level arguments.
    """
    parser = argparse.ArgumentParser(
        description=f"Run {pillar_name} pillar assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python -m src.app.agents.<agent_module> my_arch.txt
  python -m src.app.agents.<agent_module> my_arch.txt --cases support_cases.csv
  python -m src.app.agents.<agent_module> my_arch.txt --log-level DEBUG
        """,
    )
    parser.add_argument(
        "architecture_file",
        help="Path to architecture description file",
    )
    parser.add_argument(
        "--cases",
        dest="cases_file",
        help="Path to azure_support_cases.csv for contextual learning",
        default=None,
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Override AGENT_LOG_LEVEL environment variable",
        default=None,
    )
    return parser


def apply_log_level_override(log_level: Optional[str]) -> None:
    """Apply CLI log-level override to environment for init_logging to consume.

    Args:
        log_level: Optional log level string (DEBUG, INFO, etc.) from CLI args.
    """
    if log_level:
        os.environ["AGENT_LOG_LEVEL"] = log_level.upper()


__all__ = ["create_agent_argument_parser", "apply_log_level_override"]
