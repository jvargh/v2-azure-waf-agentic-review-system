# Migrated from src.app.utils.cli_utils
from __future__ import annotations
import argparse, os
from typing import Optional

def create_agent_argument_parser(pillar_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"Run {pillar_name} pillar assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m backend.app.agents.<agent_module> my_arch.txt
  python -m backend.app.agents.<agent_module> my_arch.txt --cases support_cases.csv
  python -m backend.app.agents.<agent_module> my_arch.txt --log-level DEBUG
        """,
    )
    parser.add_argument("architecture_file", help="Path to architecture description file")
    parser.add_argument("--cases", dest="cases_file", help="Path to azure_support_cases.csv", default=None)
    parser.add_argument("--log-level", dest="log_level", choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"], default=None)
    return parser

def apply_log_level_override(log_level: Optional[str]) -> None:
    if log_level:
        os.environ["AGENT_LOG_LEVEL"] = log_level.upper()
__all__ = ["create_agent_argument_parser", "apply_log_level_override"]
