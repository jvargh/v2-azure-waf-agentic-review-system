# Pillar Agent Replication Plan

## Overview
**REQUIRED:** Summarize the reliability agent architecture, shared utilities, scoring pipeline, documentation alignment, and testing strategy so new pillar agents (Security, Cost Optimization, Operational Excellence, Performance Efficiency) can mirror the same lightweight pattern.

## 1. Reliability Agent Lifecycle (REQUIRED)
- Reference `src/app/agents/reliability_agent.py` (`ReliabilityAssessment`, `ReliabilityAgent.assess_architecture`, `_parse_response`, `main`).
- Describe CLI invocation, config loading, assessment flow, markdown generation, JSON handling.

## 2. Shared Utilities & Prompts
- `src/app/prompts/reliability_agent_instructions.txt` — REQUIRED: JSON contract (scores, recommendations, references), prompt naming.
- `src/app/tools/mcp_tools.py` — REQUIRED: MCP manager, fallback behavior, link normalization.
- `src/utils/env_utils.py` — OPTIONAL: env detection helpers reused across pillars.
- `src/app/agents/reliability_agent.py` constants import pattern — REQUIRED: domain titles, pillar code usage.
- Naming conventions — REQUIRED: `src/app/agents/<pillar>_constants.py`, `<Pillar>Agent` classes, `<pillar>_pillar.json`, `<pillar>_agent_instructions.txt`.

## 3. Scoring Pipeline & Azure References (REQUIRED)
- `src/utils/scoring/reliability_pillar.json` — structure (`pillar`, `practices`, weights, signals, categories, `references` array).
- `src/utils/scoring/scoring.py` — JSON loading (`load_pillar`), practice scoring, maturity computation, tolerance for extra fields.
- Shared `references` array must include stable markdown links for each pillar:
  - Security → [Security Checklist](https://learn.microsoft.com/en-us/azure/well-architected/security/checklist) plus every SE link from that page.
  - Cost Optimization → [Cost Optimization Checklist](https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/checklist) plus each CO link.
  - Operational Excellence → [Operational Excellence Checklist](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/checklist) plus each OE link.
  - Performance Efficiency → [Performance Efficiency Checklist](https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/checklist) plus each PE link.

## 4. Documentation Alignment (REQUIRED)
- Cross-check `README.md`, `src/docs/AGENT_REPLICATION_BLUEPRINT.md`, `src/docs/ReliabilityPillar.txt`.
- Enumerate mismatches (terminology, file paths, schema notes) and tag REQUIRED updates vs OPTIONAL enhancements per pillar.

## 5. Testing Pattern (REQUIRED)
- `tests/test_reliability_agent_e2e.py` — domain coverage, recommendation schema (priority, impact_score, pillar_codes, severity), maturity data.
- `tests/test_mcp_tools.py` — MCP availability toggles and fallbacks.
- `tests/conftest.py` — fixtures/utilities new pillars should reuse.
- Fixture naming rule: `tests/fixtures/<pillar>_sample_architecture.txt` (300–500 words, mixes good/bad patterns, triggers ≥5 codes).

## 6. Post-Pillar Follow-Up (REQUIRED once all pillars ship)
- After Security, Cost Optimization, Operational Excellence, and Performance Efficiency agents are complete, promote refactoring to a shared `PillarAgent` base class (extract duplicated logic from `src/app/agents/reliability_agent.py`, unify prompts/scoring hooks).
- Consider unified CLI (`--pillar`), schema validation helper, JSON artifact output, and caching as secondary enhancements.

## Appendices (OPTIONAL)
- Pillar replication checklist with checkboxes (constants, prompts, scoring JSON, tests, docs).
- Troubleshooting table summarizing common issues (missing titles, parse errors, schema drift).