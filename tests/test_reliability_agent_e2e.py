"""End-to-end style test for ReliabilityAgent integrating (mocked) LLM + MCP.

This test does NOT hit real Azure services. It monkeypatches the agent's
initialization and MCP documentation retrieval so we can exercise:
  * Architecture assessment flow
  * LLM JSON parsing & recommendation normalization
  * MCP reference collection (truncation to 3 refs)
  * Deterministic maturity scoring integration

If the Microsoft Agent Framework is not installed (module raises SystemExit),
the test is skipped automatically.
"""

import asyncio
import json
import sys
import pathlib
import pytest
from typing import Any, Dict, List

# Ensure src path
_SRC_PATH = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

ReliabilityAgent = None  # will import lazily inside test


def _print_banner(title: str):
    print(f"\n=== {title} ===")


def _log_assert(desc: str, **ctx):
    print(f"  -> ASSERT: {desc}")
    for k, v in ctx.items():
        print(f"     {k} = {v}")


class _FakeLLMAgent:
    """Minimal async fake implementing .run(prompt) -> object with .text."""

    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

    async def run(self, prompt: str):
        class R:
            pass
        r = R()
        # We ignore the prompt and just return the injected JSON payload
        r.text = json.dumps(self.payload)
        await asyncio.sleep(0)
        return r


@pytest.mark.asyncio
async def test_reliability_agent_llm_mcp_integration(monkeypatch):
    # Lazy import to avoid failing at collection time if framework missing
    global ReliabilityAgent
    if ReliabilityAgent is None:
        try:
            from app.agents.reliability_agent import ReliabilityAgent as _RA
            ReliabilityAgent = _RA
        except Exception:
            pytest.skip("Agent framework not available; skipping e2e agent test")
    name = "reliability_agent_llm_mcp_integration"
    _print_banner(f"TEST START: {name}")
    architecture = """
    Web app on Azure App Service with single region SQL Database. No backups, no geo-redundancy,
    missing health probes, no retry policies, and no disaster recovery strategy documented.
    """.strip()

    fake_json = {
        "overall_score": 82,
        "domain_scores": {
            "RE01": {"score": 75, "title": "Reliability-Focused Design Foundations"},
            "RE02": {"score": 70, "title": "Identify and Rate User and System Flows"},
            "RE03": {"score": 65, "title": "Perform Failure Mode Analysis (FMA)"},
            "RE04": {"score": 80, "title": "Define Reliability and Recovery Targets"},
            "RE05": {"score": 78, "title": "Add Redundancy at Different Levels"},
            "RE06": {"score": 72, "title": "Implement a Timely and Reliable Scaling Strategy"},
            "RE07": {"score": 85, "title": "Strengthen Resiliency with Self-Preservation and Self-Healing"},
            "RE08": {"score": 60, "title": "Test for Resiliency and Availability Scenarios"},
            "RE09": {"score": 55, "title": "Implement Structured, Tested, and Documented BCDR Plans"},
            "RE10": {"score": 68, "title": "Measure and Model the Solution's Health Indicators"},
        },
        "recommendations": [
            {
                "title": "Add Geo-Redundant Backups",
                "description": "Enable geo-redundant backups for SQL Database",
                "priority": "High",
                "impact_score": 8,
                "pillar_codes": ["RE09"]
            },
            {
                "title": "Introduce Health Probes",
                "description": "Configure health probes and auto-healing for App Service",
                "priority": "Medium",
                "impact_score": 6,
                "pillar_codes": ["RE07"]
            }
        ],
        "mcp_references": [  # Will be ignored in final assessment (we supply our own list)
            {"title": "Ignored Ref", "url": "https://example.com/ignore"}
        ]
    }

    # Stub MCP references (5 so truncation to 3 can be verified)
    stub_docs = [
        {"title": f"Ref {i}", "url": f"https://learn.microsoft.com/en-us/azure/doc{i}"}
        for i in range(1, 6)
    ]

    # Monkeypatch _initialize_agent to inject our fake LLM agent
    async def _fake_init(self):  # self is ReliabilityAgent instance
        # Simulate async initialization latency
        await asyncio.sleep(0)
        self.agent = _FakeLLMAgent(fake_json)

    monkeypatch.setattr(ReliabilityAgent, "_initialize_agent", _fake_init, raising=True)

    # Monkeypatch MCP manager method if present
    async def _fake_get_docs(service_name: str, topic: str):  # noqa: ARG001
        await asyncio.sleep(0)
        return stub_docs

    # Instantiate agent with MCP enabled so call path executes
    agent = ReliabilityAgent(enable_mcp=True)
    if agent.mcp_manager:  # Replace its method
        monkeypatch.setattr(agent.mcp_manager, "get_service_documentation", _fake_get_docs, raising=True)

    assessment = await agent.assess_architecture(architecture)

    # Assertions with logging
    _log_assert("overall score matches fake JSON", expected=82, actual=assessment.overall_score)
    assert assessment.overall_score == 82

    _log_assert("domain scores propagated", domain_scores=assessment.domain_scores)
    assert assessment.domain_scores.get("RE05", {}).get("score") == 78  # Add Redundancy at Different Levels
    assert assessment.domain_scores.get("RE09", {}).get("score") == 55  # BCDR Plans
    assert assessment.domain_scores.get("RE07", {}).get("score") == 85  # Self-Preservation/Self-Healing

    _log_assert("recommendations normalized with severity", recs=assessment.recommendations)
    assert len(assessment.recommendations) == 2
    # Each recommendation should now contain a severity integer
    assert all("severity" in r for r in assessment.recommendations)

    _log_assert("MCP references truncated to 3", count=len(assessment.mcp_references))
    assert len(assessment.mcp_references) == 3

    maturity = assessment.maturity
    _log_assert("deterministic maturity contains overall percent", percent=maturity.get("overall_maturity_percent"))
    assert "overall_maturity_percent" in maturity

    _print_banner(f"TEST END: {name}")
    print("Assessment excerpt:")
    print(json.dumps({
        "overall_score": assessment.overall_score,
        "mcp_refs": assessment.mcp_references,
        "first_rec": assessment.recommendations[0]
    }, indent=2))
