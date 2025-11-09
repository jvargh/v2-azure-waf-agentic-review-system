"""Pytest configuration: ensure the project's src directory is importable.

This avoids needing editable installs during local development. If a proper
package structure (e.g., pyproject.toml with packages) is later added, this
shim can be removed.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
