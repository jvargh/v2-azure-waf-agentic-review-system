"""Hybrid LLM shadow scorer stub.

Produces an experimental structure without influencing existing pillar scoring.
To be expanded with retrieval + semantic alignment phases. For now returns placeholder
coverage metrics and rationale fields.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def run_hybrid_shadow(pillar: str, unified_corpus: str, pillar_evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Return experimental hybrid scoring payload.

    Parameters
    ----------
    pillar: Pillar name (e.g., 'reliability').
    unified_corpus: Full corpus string assembled by orchestrator.
    pillar_evidence: Map of pillar -> evidence snippets.
    """
    excerpts = pillar_evidence.get(pillar, {}).get("excerpts", []) if pillar_evidence else []
    concept_hits = len(excerpts)

    # Placeholder provisional subcategory scores (uniform 0.0)
    provisional = {
        "subcategory_scores": {},
        "explanation": "Hybrid shadow mode placeholder; retrieval & semantic scoring not yet implemented.",
    }

    return {
        "pillar": pillar,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "placeholder",
        "concept_hits": concept_hits,
        "evidence_count": len(excerpts),
        "provisional": provisional,
        "llm_rationale": None,
        "notes": "Enable retrieval index to enrich this structure in future iterations.",
    }
