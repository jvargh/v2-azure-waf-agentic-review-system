"""Artifact normalization and pillar evidence inference utilities.

Provides helpers to:
- Collect pillar_evidence across all artifact structured reports
- Infer diagram pillar evidence when absent using embedding or keyword similarity
- Consolidate and deduplicate excerpts per pillar

Embedding Strategy:
Attempts Azure OpenAI or OpenAI embeddings if environment configuration is present.
Falls back to simple token overlap cosine (bag-of-words) without external dependencies.

This module keeps dependencies light; it does not introduce new packages.
"""
from __future__ import annotations

import os
import math
import logging
from typing import Dict, List, Any, Iterable, Tuple

logger = logging.getLogger(__name__)

# Pillar vocabulary (expandable); phrases tuned for similarity scoring
PILLAR_VOCAB: Dict[str, List[str]] = {
    "reliability": ["resilience", "failover", "high availability", "redundancy", "retry", "fault domain"],
    "security": ["encryption", "identity", "rbac", "threat", "firewall", "access control", "zero trust"],
    "performance": ["latency", "throughput", "scalability", "autoscale", "optimize", "load"],
    "operational": ["monitoring", "observability", "telemetry", "automation", "deployment", "runbook"],
    "cost": ["cost", "spend", "savings", "optimize cost", "reserved instance", "rightsizing"],
}

MAX_EXCERPTS_PER_PILLAR = 5

# ---------------------------------------------------------------------------
# Embedding helpers (optional)
# ---------------------------------------------------------------------------

def _embed_texts(texts: List[str], llm_provider=None) -> List[List[float]]:
    """Attempt to embed texts using LLMProvider if provided; fallback to OpenAI/Azure OpenAI if configured; final fallback to bag-of-words vector.
    Returns list of embedding vectors (each a list[float]).
    """
    # Priority 1: Use injected llm_provider if available
    if llm_provider:
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Cannot use run_until_complete in running loop; schedule and await manually not possible here (sync fn)
                # Fallback to legacy path
                pass
            else:
                embeddings = loop.run_until_complete(llm_provider.embed(texts))
                if embeddings:
                    return embeddings
        except Exception as e:
            logger.debug("LLMProvider embedding failed: %s", e)
    
    # Priority 2: Try legacy OpenAI client (package openai should be available per requirements)
    try:
        from openai import OpenAI  # type: ignore
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
        if api_key:
            client = OpenAI()
            # Model name heuristic; allow override via env EMBEDDING_MODEL
            model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
            resp = client.embeddings.create(model=model, input=texts)
            return [d.embedding for d in resp.data]
    except Exception as e:  # pragma: no cover - defensive
        logger.debug("Embedding API unavailable or failed: %s", e)

    # Fallback: simple bag-of-words TF vector
    vocab: Dict[str, int] = {}
    vectors: List[List[float]] = []
    tokenized: List[List[str]] = []
    for t in texts:
        tokens = [tok for tok in t.lower().split() if tok.isalpha()]
        tokenized.append(tokens)
        for tok in tokens:
            if tok not in vocab:
                vocab[tok] = len(vocab)
    size = len(vocab)
    for tokens in tokenized:
        vec = [0.0] * size
        for tok in tokens:
            idx = vocab.get(tok)
            if idx is not None:
                vec[idx] += 1.0
        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        vec = [v / norm for v in vec]
        vectors.append(vec)
    return vectors


def _cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b)) / ((math.sqrt(sum(x * x for x in a)) or 1.0) * (math.sqrt(sum(y * y for y in b)) or 1.0))

# ---------------------------------------------------------------------------
# Evidence inference
# ---------------------------------------------------------------------------

def infer_diagram_pillar_evidence(diagram_text_blocks: List[str], llm_provider=None) -> Dict[str, Dict[str, Any]]:
    """Infer pillar evidence from diagram textual blocks (topology insights, llm_analysis, component names).
    Uses embedding similarity of sentences vs pillar vocabulary phrases.
    """
    combined = "\n".join(diagram_text_blocks)
    sentences: List[str] = []
    for raw in combined.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        # Split rudimentary by period segmentation
        parts = [p.strip() for p in raw.replace(";", ".").split(".") if p.strip()]
        for p in parts:
            if 8 <= len(p) <= 240:
                sentences.append(p)
    if not sentences:
        return {}

    # Prepare pillar representative phrases
    pillar_phrases: List[str] = []
    pillar_index: List[Tuple[str, str]] = []  # (pillar, phrase)
    for pillar, phrases in PILLAR_VOCAB.items():
        for phrase in phrases:
            pillar_phrases.append(phrase)
            pillar_index.append((pillar, phrase))

    # Embed sentences + pillar phrases
    sentence_embeddings = _embed_texts(sentences, llm_provider)
    phrase_embeddings = _embed_texts(pillar_phrases, llm_provider)

    # Score sentences against each pillar via max cosine to any phrase
    pillar_scores: Dict[str, List[Tuple[float, str]]] = {p: [] for p in PILLAR_VOCAB.keys()}
    for si, sent_vec in enumerate(sentence_embeddings):
        for (pillar, phrase), phrase_vec in zip(pillar_index, phrase_embeddings):
            score = _cosine(sent_vec, phrase_vec)
            # Threshold tuned modestly; treat >0.25 as semantic relatedness in fallback embedding mode
            if score > 0.25:
                pillar_scores[pillar].append((score, sentences[si]))

    inferred: Dict[str, Dict[str, Any]] = {}
    for pillar, scored in pillar_scores.items():
        # Deduplicate by normalized lowercase slice
        seen = set()
        scored_sorted = sorted(scored, key=lambda x: x[0], reverse=True)
        excerpts: List[str] = []
        for score, text in scored_sorted:
            key = text.lower()[:160]
            if key in seen:
                continue
            seen.add(key)
            excerpts.append(text[:240])
            if len(excerpts) >= MAX_EXCERPTS_PER_PILLAR:
                break
        if excerpts:
            inferred[pillar] = {"count": len(excerpts), "excerpts": excerpts, "inferred": True}
    return inferred

# ---------------------------------------------------------------------------
# Consolidation
# ---------------------------------------------------------------------------

def collect_and_infer_pillar_evidence(documents: List[Dict[str, Any]], analysis_results: Dict[str, Dict[str, Any]], llm_provider=None) -> Dict[str, Dict[str, Any]]:
    """Collect pillar evidence from structured reports; infer for diagrams when absent.
    Returns consolidated pillar evidence dict.
    """
    consolidated: Dict[str, Dict[str, Any]] = {}

    def _merge(pillar: str, excerpts: List[str], inferred: bool = False):
        entry = consolidated.setdefault(pillar, {"excerpts": [], "count": 0})
        for ex in excerpts:
            norm = ex.lower()[:160]
            if norm not in {e.lower()[:160] for e in entry["excerpts"]}:
                entry["excerpts"].append(ex)
        entry["count"] = len(entry["excerpts"])
        if inferred:
            entry["inferred"] = True

    for doc in documents:
        structured_report = doc.get("structured_report") or analysis_results.get(doc.get("id"), {}).get("structured_report")
        if structured_report and structured_report.get("pillar_evidence"):
            for pillar, data in structured_report["pillar_evidence"].items():
                _merge(pillar, data.get("excerpts", []), inferred=data.get("inferred", False))
        # Diagram inference if missing
        if doc.get("category") == "diagram":
            sr = structured_report or {}
            if not sr.get("pillar_evidence"):
                analysis = analysis_results.get(doc.get("id"), {})
                blocks: List[str] = []
                if analysis.get("llm_analysis"):
                    blocks.append(analysis["llm_analysis"])
                if analysis.get("topology_insights"):
                    blocks.extend(analysis["topology_insights"])
                # Include any raw_text if present
                if doc.get("raw_text"):
                    blocks.append(doc["raw_text"])
                inferred = infer_diagram_pillar_evidence(blocks, llm_provider)
                for pillar, data in inferred.items():
                    _merge(pillar, data.get("excerpts", []), inferred=True)

    # Cap excerpts per pillar
    for pillar, data in consolidated.items():
        if len(data["excerpts"]) > MAX_EXCERPTS_PER_PILLAR:
            data["excerpts"] = data["excerpts"][:MAX_EXCERPTS_PER_PILLAR]
            data["count"] = len(data["excerpts"])
    return consolidated
