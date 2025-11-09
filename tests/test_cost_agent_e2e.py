"""End-to-end test for Cost Optimization agent."""

import asyncio
import json
from pathlib import Path

import pytest

from backend.app.agents.cost_agent import CostAgent


@pytest.mark.asyncio
async def test_cost_agent_normalizes_recommendations(monkeypatch):
    """Test CostAgent assessment with mocked agent framework."""
    fake_json = {
        "pillar": "cost",
        "domain_scores": {
            "CO01": {"score": 35, "title": "Create a culture of financial responsibility"},
            "CO02": {"score": 25, "title": "Create and maintain a cost model"},
            "CO03": {"score": 20, "title": "Collect and review cost data"},
            "CO04": {"score": 30, "title": "Set spending guardrails"},
            "CO05": {"score": 15, "title": "Get the best rates from providers"},
            "CO06": {"score": 40, "title": "Align usage to billing increments"},
            "CO07": {"score": 25, "title": "Optimize component costs"},
            "CO08": {"score": 20, "title": "Optimize environment costs"},
            "CO09": {"score": 45, "title": "Optimize flow costs"},
            "CO10": {"score": 30, "title": "Optimize data costs"},
            "CO11": {"score": 50, "title": "Optimize code costs"},
            "CO12": {"score": 25, "title": "Optimize scaling costs"},
            "CO13": {"score": 35, "title": "Optimize personnel time"},
            "CO14": {"score": 30, "title": "Consolidate resources and responsibility"},
        },
        "maturity_level": "Initial",
        "recommendations": [
            {
                "title": "Implement Azure Cost Management with budgets and alerts",
                "description": "No cost tracking or budgets configured",
                "priority": "Critical",
                "impact_score": 9,
                "pillar_codes": ["CO03", "CO02"],
            },
            {
                "title": "Purchase Azure Reservations for predictable workloads",
                "description": "All resources using pay-as-you-go pricing",
                "priority": "High",
                "impact_score": 8,
                "pillar_codes": ["CO05"],
            },
            {
                "title": "Implement auto-shutdown for nonproduction environments",
                "description": "Dev/test running 24/7 on premium tiers",
                "priority": "High",
                "impact_score": 7,
                "pillar_codes": ["CO08"],
            },
        ],
    }

    async def _fake_init(self):  # type: ignore[override]
        async def _fake_run(self_inner, task, **kw):  # noqa: ARG001
            await asyncio.sleep(0)
            return json.dumps(fake_json)
        
        await asyncio.sleep(0)
        self.agent = type("Agent", (), {"run": _fake_run})()

    monkeypatch.setattr(CostAgent, "_initialize_agent", _fake_init, raising=True)

    async def _fake_mcp(service: str, topic: str):  # noqa: ARG001
        await asyncio.sleep(0)
        return [
            {
                "title": "Design review checklist for Cost Optimization",
                "url": "https://learn.microsoft.com/azure/well-architected/cost/checklist",
            },
            {
                "title": "Cost optimization design principles",
                "url": "https://learn.microsoft.com/azure/well-architected/cost/principles",
            },
        ]

    monkeypatch.setattr(
        "backend.app.tools.mcp_tools.MCPDocumentationClient.search_docs",
        _fake_mcp,
        raising=False,
    )

    # Read test architecture
    fixture_path = Path(__file__).parent / "fixtures" / "cost_sample_architecture.txt"
    architecture = fixture_path.read_text(encoding="utf-8")

    # Create agent and assess
    agent = CostAgent()
    assessment = await agent.assess_architecture(architecture)
    
    # Verify assessment structure (maturity comes from scoring engine, not LLM)
    assert "overall_maturity_percent" in assessment.maturity
    assert len(assessment.recommendations) == 3
    
    # Verify domain scores
    assert assessment.domain_scores.get("CO01", {}).get("score") == 35
    assert assessment.domain_scores.get("CO03", {}).get("score") == 20
    assert assessment.domain_scores.get("CO05", {}).get("score") == 15
    assert assessment.domain_scores.get("CO08", {}).get("score") == 20
    
    # Verify recommendations
    rec = assessment.recommendations[0]
    assert rec["title"] == "Implement Azure Cost Management with budgets and alerts"
    assert rec["priority"] == "Critical"
    assert rec["impact_score"] == 9
    assert "CO03" in rec["pillar_codes"]
    
    # Verify markdown output can be generated
    results_markdown = agent.build_results_markdown(assessment)
    assert len(results_markdown) > 0
    assert "cost" in results_markdown.lower()
