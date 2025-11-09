import json
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional

CATALOG_DIR = Path(__file__).parent

@lru_cache(maxsize=8)
def load_expected_concepts(pillar: str) -> Optional[Dict[str, List[str]]]:
    """Load curated expected concepts for a pillar if available.

    Returns mapping of Subcategory Title -> List[str] or None if no curated catalog.
    """
    filename = f"{pillar.lower()}_expected_concepts.json"
    path = CATALOG_DIR / filename
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        subs = data.get("subcategories")
        if isinstance(subs, dict):
            # Normalize values (unique, preserve order)
            normalized = {}
            for k, v in subs.items():
                if isinstance(v, list):
                    seen = set()
                    ordered = []
                    for item in v:
                        if not isinstance(item, str):
                            continue
                        low = item.strip()
                        if not low or low in seen:
                            continue
                        seen.add(low)
                        ordered.append(low)
                    normalized[k] = ordered
            return normalized
    except Exception:
        return None
    return None

__all__ = ["load_expected_concepts"]
