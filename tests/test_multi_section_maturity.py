import os
import types
from typing import List

import pytest

# Import module under test
from src.app.agents.pillar_agent_base import BasePillarAgent, compute_pillar_scores, summarize_scores
from backend.utils.scoring.scoring import PillarScores

class DummyAgent(BasePillarAgent):
    """Minimal stub skipping heavy initialization (agent framework)."""
    def __init__(self):
        # Bypass BasePillarAgent __init__ (which requires Azure libs)
        self.pillar_code = "reliability"
        self.pillar_display_name = "Reliability"

@pytest.fixture
def dummy_agent():
    return DummyAgent()

@pytest.fixture
def corpus_text() -> str:
    return (
        "=== ARCHITECTURE NARRATIVE ===\n" +
        "Resilient services deployed across zones. Retry logic present." +
        "\n=== VISUAL TOPOLOGY INSIGHTS ===\n" +
        "Diagram shows multi-region failover and autoscale group." +
        "\n=== OPERATIONAL REALITY (SUPPORT CASES) ===\n" +
        "Historical incidents involve configuration drift and missing health probes." +
        "\n=== CONSOLIDATED PILLAR EVIDENCE ===\n" +
        "FAILOVER documented; health metrics partially defined." +
        "\nRaw LLM Analysis (Legacy)\nThis block should be removed when legacy disabled.\n\n"  # trailing blank ends legacy block
    )

@pytest.fixture
def monkeypatch_scores(monkeypatch):
    # Predefined maturity percents per section to test averaging
    percents = [40.0, 60.0, 80.0, 20.0]
    calls = {"i": 0}

    def _fake_compute(text: str, pillar: str = "reliability") -> PillarScores:  # type: ignore
        i = calls["i"]
        pct = percents[i] if i < len(percents) else 50.0
        calls["i"] += 1
        return PillarScores(
            pillar=pillar,
            version="1.0",
            overall_maturity_percent=pct,
            scale={},
            practice_scores=[],
            recommendations=[],
            gap_results=[],
            framework=None,
        )

    # Monkeypatch the imported symbol inside pillar_agent_base
    monkeypatch.setattr("src.app.agents.pillar_agent_base.compute_pillar_scores", _fake_compute)
    return percents

def test_section_extraction(dummy_agent, corpus_text):
    sections = dummy_agent._extract_weighted_sections(corpus_text)
    assert len(sections) == 4, f"Expected 4 sections, got {len(sections)}"
    assert all(len(s) > 0 for s in sections)

def test_legacy_filtering_removes_block(dummy_agent, corpus_text):
    # legacy disabled by default
    filtered = dummy_agent._filter_legacy_sections(corpus_text)
    assert "Raw LLM Analysis" not in filtered
    # Enable legacy via env
    os.environ["ENABLE_LEGACY_SECTIONS"] = "true"
    with_legacy = dummy_agent._filter_legacy_sections(corpus_text)
    assert "Raw LLM Analysis" in with_legacy
    os.environ.pop("ENABLE_LEGACY_SECTIONS", None)

def test_multi_section_average(dummy_agent, corpus_text, monkeypatch_scores):
    sections = dummy_agent._extract_weighted_sections(corpus_text)
    summary = dummy_agent._compute_multi_section_maturity(sections)
    expected_avg = sum(monkeypatch_scores) / len(monkeypatch_scores)
    assert summary["overall_maturity_percent"] == pytest.approx(expected_avg, rel=1e-3)

def test_fallback_single_section(dummy_agent):
    text = "No markers here; entire text considered one section."  # no markers
    sections = dummy_agent._extract_weighted_sections(text)
    assert len(sections) == 1
