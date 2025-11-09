# Multi-Section Deterministic Scoring & Legacy Filtering

This document explains the enhanced deterministic scoring pipeline and legacy raw analysis filtering.

## Overview
The unified corpus assembled by `AssessmentOrchestrator` contains up to four major sections:
1. `=== ARCHITECTURE NARRATIVE ===` – textual architecture documents.
2. `=== VISUAL TOPOLOGY INSIGHTS ===` – diagram-derived analysis and inferred structural insights.
3. `=== OPERATIONAL REALITY (SUPPORT CASES) ===` – reactive operational history from support cases.
4. `=== CONSOLIDATED PILLAR EVIDENCE ===` – merged excerpts from structured reports & inferred diagram evidence.

The pillar agent base (`pillar_agent_base.py`) now splits the corpus on these markers, computes pillar deterministic maturity for each section independently (via existing practice/gap matching), then averages the resulting section maturity percentages for an equal-weight final score. Practice scores are merged by averaging the per-section practice score values and unioning matched signals.

## Equal Weighting Rationale
- Avoids over-emphasis on any single artifact type.
- Encourages balanced improvement across architecture design, operational signals, and visual topology.
- Simplifies interpretability: each section contributes 25% (if present). Missing sections do not penalize—they are simply omitted from the average denominator.

## Legacy Raw Analysis Filtering
Legacy raw LLM blocks (e.g., "Raw LLM Analysis") are removed prior to scoring unless explicitly enabled.

Set environment variable to retain legacy blocks:
```
ENABLE_LEGACY_SECTIONS=true
```
Accepted truthy values: `1`, `true`, `yes` (case-insensitive). Default behavior: legacy blocks stripped.

Filtering heuristic: lines beginning with/containing `Raw LLM Analysis` start a skip mode until the next blank line.

## Pillar Evidence Integration
Structured `pillar_evidence` (including inferred diagram evidence) is appended to the corpus under `=== CONSOLIDATED PILLAR EVIDENCE ===` for deterministic matching and contextual enrichment.

## Recommendation Deduplication
Cross-pillar recommendations are semantically deduplicated using embeddings (OpenAI/Azure OpenAI if available) or a bag‑of‑words cosine fallback. Similarity > 0.90 merges duplicates; the first instance becomes canonical.

## Extensibility
To adjust weighting, introduce an env variable (future enhancement):
```
SECTION_WEIGHTS=architecture:0.4,visual:0.2,cases:0.2,evidence:0.2
```
If implemented, parsing would replace equal average logic.

## Developer Notes
- Private helpers: `_extract_weighted_sections`, `_compute_multi_section_maturity`, `_filter_legacy_sections`.
- Tests ensure section parsing correctness, legacy filtering, and averaging.
- No additional external dependencies were added.

## Troubleshooting
| Symptom | Likely Cause | Resolution |
|---------|--------------|-----------|
| All maturity percent = 0 | Markers missing or corpus empty | Verify orchestrator adds sections; inspect unified corpus string |
| Legacy content still present | Env var set or filtering heuristic miss | Confirm `ENABLE_LEGACY_SECTIONS` unset; check block formatting |
| Recommendations duplicates | Embedding API failure fallback threshold too low | Review logs; adjust similarity threshold in `_dedupe_semantic_recommendations` |

## References
- `backend/app/analysis/orchestrator.py` – corpus assembly & evidence consolidation.
- `src/app/agents/pillar_agent_base.py` – multi-section maturity scoring implementation.
