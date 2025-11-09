"""Generic pillar scoring loader and proxy.

This module is data-driven: each pillar is defined by a JSON file named
"<pillar>_pillar.json" located in the same directory. The JSON schema is:

{
  "pillar": "reliability",
  "version": "1.0",
  "scale": { "0": "Absent", ... },
  "practices": [
     {
       "code": "RE01",
       "title": "...",
       "weight": 8,
       "signals": ["multi-region", ...],
       "recommendations": [
          {"id": "re01-1", "title": "..", "description": "..", "priority": 1}
       ]
     }
  ],
  "signals_catalog": { "signal": "description" }
}

Scoring Heuristic (enhanced):
    Practices MAY define a "scoring" block:
        {
            "mode": "proportional" | "tiered" | "binary",
            "signals": ["slo", ...],
            "signal_weights": {"slo": 2, ...},
            "signal_aliases": {"slo": ["service level objective", ...]}
        }

    Matching:
        - A signal is considered present if its token or any alias phrase appears (case-insensitive) as a whole word/phrase.
        - We aggregate matched base signal names (not aliases) and compute coverage.

    Modes:
        proportional: score = round( (matched_weight / total_weight) * 5 )
        tiered: coverage->score mapping: <25%=1, <50%=2, <75%=3, <100%=4, 100%=5 (0 if none)
        binary: none=0, some but <50% weight ->2, >=50% but <100% ->4, 100% ->5

    Legacy Support:
        If no scoring block present, falls back to legacy simple proportional over practice["signals"].

    Overall maturity percent = (sum(practice_score * practice_weight) / (5 * sum(practice_weights))).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import re

BASE_DIR = Path(__file__).parent


class PillarNotFoundError(FileNotFoundError):
    pass


@dataclass
class PracticeScore:
    code: str
    title: str
    weight: float  # practice weight in pillar weighting
    score: int  # 0-5
    matched_signals: List[str]  # base signal identifiers matched
    total_signals: int  # total distinct signals considered
    coverage: float  # matched_weight / total_weight (0-1) for scoring signals
    mode: str  # scoring mode used

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "title": self.title,
            "weight": self.weight,
            "score": self.score,
            "matched_signals": self.matched_signals,
            "total_signals": self.total_signals,
            "coverage": round(self.coverage, 3),
            "mode": self.mode,
        }


@dataclass
class PillarScores:
    pillar: str
    version: str
    overall_maturity_percent: float
    scale: Dict[str, str]
    practice_scores: List[PracticeScore]
    recommendations: List[Dict[str, Any]]
    gap_results: List[Dict[str, Any]]
    framework: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pillar": self.pillar,
            "version": self.version,
            "overall_maturity_percent": self.overall_maturity_percent,
            "scale": self.scale,
            "practice_scores": [p.to_dict() for p in self.practice_scores],
            "recommendations": self.recommendations,
            "gaps": self.gap_results,
        }


def _pillar_file_name(pillar: str) -> str:
    return f"{pillar.lower()}_pillar.json"


def list_pillars() -> List[str]:
    """Return list of available pillar names based on * _pillar.json files."""
    return [p.name.split("_pillar.json")[0] for p in BASE_DIR.glob("*_pillar.json")]


def load_pillar(pillar: str) -> Dict[str, Any]:
    file_path = BASE_DIR / _pillar_file_name(pillar)
    if not file_path.exists():
        raise PillarNotFoundError(f"Pillar definition not found: {file_path}")
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _phrase_present(text: str, phrase: str) -> bool:
    """Return True if phrase (already lowercase) appears as a standalone word/phrase.

    Uses a conservative regex with word boundaries at ends where possible.
    """
    phrase = phrase.strip()
    if not phrase:
        return False
    # Allow spaces inside phrase; enforce boundary on start/end tokens
    boundary_pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(boundary_pattern, text) is not None


def _match_scoring_signals(text: str, scoring_conf: Dict[str, Any]) -> Dict[str, Any]:
    signals: List[str] = scoring_conf.get("signals", [])
    weights: Dict[str, float] = scoring_conf.get("signal_weights", {}) or dict.fromkeys(signals, 1.0)
    aliases: Dict[str, List[str]] = scoring_conf.get("signal_aliases", {}) or {}

    matched = []
    matched_weight = 0.0
    total_weight = sum(weights.get(s, 1) for s in signals) or 0.0
    if total_weight == 0:
        return {"matched": matched, "matched_weight": 0.0, "total_weight": 0.0}

    for sig in signals:
        base_terms = [sig.lower()]
        for alias in aliases.get(sig, []):
            base_terms.append(str(alias).lower())
        if any(_phrase_present(text, term) for term in base_terms):
            matched.append(sig)
            matched_weight += weights.get(sig, 1)
    coverage = matched_weight / total_weight if total_weight else 0.0
    return {
        "matched": matched,
        "matched_weight": matched_weight,
        "total_weight": total_weight,
        "coverage": coverage,
    }


def _score_from_coverage(mode: str, coverage: float, any_matched: bool, full_match: bool) -> int:
    if not any_matched:
        return 0
    if mode == "proportional":
        return int(round(coverage * 5))
    if mode == "tiered":
        thresholds = [(1.0, 5), (0.75, 4), (0.5, 3), (0.25, 2), (0.0, 1)]
        for t, sc in thresholds:
            if coverage >= t - 1e-9 and (t < 1.0 or full_match):
                return sc
        return 1
    if mode == "binary":
        if full_match:
            return 5
        return 4 if coverage >= 0.5 else 2
    return int(round(coverage * 5))


def _score_practice(practice: Dict[str, Any], text: str, override_weight: Optional[float] = None) -> PracticeScore:
    scoring_conf = practice.get("scoring")
    if scoring_conf:
        mode = scoring_conf.get("mode", "proportional").lower()
        match_info = _match_scoring_signals(text, scoring_conf)
        coverage = match_info["coverage"]
        any_matched = bool(match_info["matched"])
        full_match = coverage >= 0.999
        score = _score_from_coverage(mode, coverage, any_matched, full_match)
        matched = match_info["matched"]
        total_signals = len(scoring_conf.get("signals", []))
    else:
        # Legacy fallback using flat signals list
        signals: List[str] = practice.get("signals", [])
        matched = []
        for sig in signals:
            if _phrase_present(text, sig.lower()):
                matched.append(sig)
        if signals:
            coverage = len(matched) / len(signals)
            score = int(round(coverage * 5))
        else:
            coverage = 0.0
            score = 0
        total_signals = len(signals)
        mode = "legacy-proportional"

    return PracticeScore(
        code=practice.get("code"),
        title=practice.get("title", ""),
        weight=float(override_weight if override_weight is not None else practice.get("weight", 0)),
        score=score,
        matched_signals=matched,
        total_signals=total_signals,
        coverage=coverage,
        mode=mode,
    )


def _collect_recommendations(practice: Dict[str, Any], practice_score: PracticeScore) -> List[Dict[str, Any]]:
    """Collect high-severity recommendations for low scoring practices.

    Normalization rules (Option B):
        Input keys accepted: severity | execution_priority | priority (legacy)
        Output key: severity
        Severity scale: 1 Critical, 2 High, 3 Medium, 4 Low, 5 Informational
        Selection heuristic: only surface severity <=2 when practice score <=2.
    """
    recs: List[Dict[str, Any]] = []
    for rec in practice.get("recommendations", []):
        severity_raw = rec.get("severity") or rec.get("execution_priority") or rec.get("priority") or 5
        try:
            severity = int(severity_raw)
        except (TypeError, ValueError):
            severity = 5
        if practice_score.score <= 2 and severity <= 2:
            normalized = {k: v for k, v in rec.items() if k not in ("priority", "execution_priority")}
            normalized["severity"] = severity
            normalized["practice"] = practice_score.code
            recs.append(normalized)
    return recs


def _evaluate_gaps(text: str, gaps_def: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Evaluate defined gaps using regex-based pattern matching.

    Improvements over prior substring logic:
      - Case-insensitive matching.
      - Word/phrase boundary handling to avoid partial word false positives.
      - Supports simple alternation via the pattern author including (a|b) groups.
      - Normalizes whitespace in both source text and patterns.
      - Returns which patterns matched exactly (original author strings).

    Pattern authoring guidance (implicit contract):
      - Provide raw phrases (e.g. "single region", "no backup") or regex groups (e.g. "no (backup|disaster recovery)").
      - Tool will automatically wrap plain alphanumeric/space patterns with word boundary style matching.
    """
    import re

    # Pre-normalize text (lower, collapse internal whitespace)
    norm_text = re.sub(r"\s+", " ", text.lower())
    results: List[Dict[str, Any]] = []
    for gap in gaps_def:
        raw_patterns: List[str] = gap.get("patterns", [])
        matched_patterns: List[str] = []
        compiled: List[tuple[str, re.Pattern]] = []
        for raw in raw_patterns:
            raw_norm = re.sub(r"\s+", " ", raw.strip().lower())
            # Heuristic: if pattern contains regex meta chars assume author supplied regex; else build safe boundary pattern.
            if re.search(r"[\(\)\|\[\]\?\+\*]", raw_norm):
                pattern_str = raw_norm
            else:
                # Escape then allow spaces -> \s+ and add word boundaries around first/last token.
                tokens = raw_norm.split()
                if not tokens:
                    continue
                # Build pattern ensuring flexible whitespace between tokens.
                escaped_tokens = [re.escape(t) for t in tokens]
                middle = r"\s+".join(escaped_tokens)
                pattern_str = fr"\b{middle}\b"
            try:
                compiled.append((raw, re.compile(pattern_str, re.IGNORECASE)))
            except re.error:
                # Fallback: skip invalid pattern
                continue
        for original, regex in compiled:
            if regex.search(norm_text):
                matched_patterns.append(original)
        results.append({
            "id": gap.get("id"),
            "label": gap.get("label"),
            "detail": gap.get("detail"),
            "practice": gap.get("practice"),
            "matched": bool(matched_patterns),
            "matchedPatterns": matched_patterns,
            "recommendationHintKeywords": gap.get("recommendation_hint_keywords", [])
        })
    return results


def compute_pillar_scores(architecture_text: str, pillar: str = "reliability") -> PillarScores:
    """Compute deterministic maturity scores for a given pillar including gap analysis."""
    data = load_pillar(pillar)
    text = architecture_text.lower()

    practice_scores: List[PracticeScore] = []
    recommendations: List[Dict[str, Any]] = []
    total_weight = 0.0
    weighted_scores = 0.0

    weights_map: Dict[str, Any] = data.get("weights", {})

    for practice in data.get("practices", []):
        code = practice.get("code")
        override_weight = weights_map.get(code) if code and code in weights_map else None
        ps = _score_practice(practice, text, override_weight=override_weight)
        practice_scores.append(ps)
        total_weight += ps.weight
        weighted_scores += ps.score * ps.weight
        recommendations.extend(_collect_recommendations(practice, ps))

    overall_percent = 0.0
    if total_weight:
        overall_percent = (weighted_scores / (5 * total_weight)) * 100

    gap_results = _evaluate_gaps(text, data.get("gaps", []))

    return PillarScores(
        pillar=data.get("pillar", pillar),
        version=data.get("version", "1.0"),
        overall_maturity_percent=round(overall_percent, 2),
        scale=data.get("scale", {}),
        practice_scores=practice_scores,
        recommendations=recommendations,
        gap_results=gap_results,
        framework=data.get("framework"),
    )


def summarize_scores(scores: PillarScores) -> Dict[str, Any]:
    """Return a condensed summary including gap analysis."""
    gaps = scores.gap_results
    matched = [g for g in gaps if g.get("matched")]
    unmatched = [g for g in gaps if not g.get("matched")]
    return {
        "pillar": scores.pillar,
        "overall_maturity_percent": scores.overall_maturity_percent,
        "practice_scores": [
            {
                "code": p.code,
                "score": p.score,
                "weight": p.weight,
                "matched_signals": p.matched_signals,
                "coverage": round(p.coverage, 3),
                "mode": p.mode,
            }
            for p in scores.practice_scores
        ],
        "recommendations": scores.recommendations,
        "gaps": gaps,
        "matched_gap_count": len(matched),
        "unmatched_gap_count": len(unmatched),
        "framework": scores.framework,
    }


__all__ = [
    "list_pillars",
    "load_pillar",
    "compute_pillar_scores",
    "summarize_scores",
    "reliability_category_breakdown",
    "PillarScores",
    "PracticeScore",
    "PillarNotFoundError",
]


def reliability_category_breakdown(scores: PillarScores) -> Dict[str, Any]:
    """Return high-level reliability subcategory percentages derived from practice scores.

    Mapping rationale (data-driven approximation, can be refined later):
      - High Availability: RE05 (Redundancy), RE06 (Scaling Strategy), RE07 (Self-Healing & Resilience Patterns), RE10 (Health Indicators & Monitoring)
      - Disaster Recovery: RE04 (Reliability & Recovery Targets), RE09 (BCDR Planning)
      - Fault Tolerance: RE03 (Failure Mode Analysis), RE07 (Self-Healing & Resilience Patterns), RE08 (Resiliency & Chaos Testing)
      - Backup Strategy: RE04 (Reliability & Recovery Targets), RE09 (BCDR Planning)  # includes targets + DR artifacts
      - Monitoring: RE10 (Health Indicators & Monitoring), RE08 (Resiliency & Chaos Testing)

    Each category percent = average( (practice_score/5)*100 ) across included practices (simple mean).
    Practices not present default to 0 (should not occur under current pillar definition).
    """
    # Build lookup of practice code -> score (0-5)
    code_to_score = {p.code: p.score for p in scores.practice_scores}

    def pct(code: str) -> float:
        return (code_to_score.get(code, 0) / 5.0) * 100.0

    # Updated mappings per latest specification from user
    mappings: Dict[str, List[str]] = {
        "Reliability-Focused Design Foundations": ["RE01", "RE02", "RE03"],
        "Reliability Objectives & Health Metrics": ["RE04", "RE10"],
        "Resilient Architecture & Scaling Strategies": ["RE05", "RE06", "RE07"],
        "Reliability Testing & Chaos Validation": ["RE08"],
        "Recovery & Continuity Preparedness": ["RE09"],
    }

    categories: Dict[str, float] = {}
    for name, codes in mappings.items():
        if codes:
            categories[name] = round(sum(pct(c) for c in codes) / len(codes), 2)
        else:
            categories[name] = 0.0

    # Include expanded practice detail for markdown convenience
    practice_details = {p.code: p.title for p in scores.practice_scores}
    category_practices = {
        name: [
            {"code": c, "title": practice_details.get(c, "") , "percent": round((code_to_score.get(c,0)/5.0)*100.0,2)}
            for c in codes
        ]
        for name, codes in mappings.items()
    }
    return {
        "pillar": scores.pillar,
        "overall_maturity_percent": scores.overall_maturity_percent,
        "categories": categories,
        "category_practices": category_practices,
    }
