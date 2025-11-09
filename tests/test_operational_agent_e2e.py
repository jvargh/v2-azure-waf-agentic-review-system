"""End-to-end test for Operational Excellence agent."""

import asyncio
import json
from pathlib import Path

import pytest

from backend.app.agents.operational_agent import OperationalAgent


@pytest.mark.asyncio
async def test_operational_agent_normalizes_recommendations(monkeypatch):
    """Test OperationalAgent assessment with mocked agent framework."""
    fake_json = {
        "pillar": "operational",
        "domain_scores": {
            "OE01": {"score": 25, "title": "Define standard practices to develop and operate workload"},
            "OE02": {"score": 20, "title": "Formalize operational tasks"},
            "OE03": {"score": 30, "title": "Formalize software ideation and planning"},
            "OE04": {"score": 15, "title": "Enhance software development and quality assurance"},
            "OE05": {"score": 10, "title": "Use infrastructure as code"},
            "OE06": {"score": 5, "title": "Build workload supply chain with pipelines"},
            "OE07": {"score": 20, "title": "Design and implement monitoring system"},
            "OE08": {"score": 15, "title": "Establish structured incident management"},
            "OE09": {"score": 25, "title": "Automate repetitive tasks"},
            "OE10": {"score": 10, "title": "Design and implement automation upfront"},
            "OE11": {"score": 5, "title": "Define safe deployment practices"},
        },
        "maturity_level": "Initial",
        "recommendations": [
            {
                "title": "Implement CI/CD pipelines for automated deployments",
                "description": "Manual portal deployments pose significant risk",
                "priority": "Critical",
                "impact_score": 10,
                "pillar_codes": ["OE06"],
            },
            {
                "title": "Adopt Infrastructure as Code with Bicep or Terraform",
                "description": "No IaC practices, manual provisioning leads to drift",
                "priority": "Critical",
                "impact_score": 9,
                "pillar_codes": ["OE05"],
            },
            {
                "title": "Deploy Application Insights for observability",
                "description": "Lack of comprehensive monitoring and telemetry",
                "priority": "High",
                "impact_score": 8,
                "pillar_codes": ["OE07"],
            },
        ],
    }

    async def _fake_init(self):  # type: ignore[override]
        async def _fake_run(self_inner, task, **kw):  # noqa: ARG001
            await asyncio.sleep(0)
            return json.dumps(fake_json)
        
        await asyncio.sleep(0)
        self.agent = type("Agent", (), {"run": _fake_run})()

    monkeypatch.setattr(OperationalAgent, "_initialize_agent", _fake_init, raising=True)

    async def _fake_mcp(service: str, topic: str):  # noqa: ARG001
        await asyncio.sleep(0)
        return [
            {
                "title": "Design review checklist for Operational Excellence",
                "url": "https://learn.microsoft.com/azure/well-architected/operational-excellence/checklist",
            },
            {
                "title": "DevOps culture",
                "url": "https://learn.microsoft.com/azure/well-architected/operational-excellence/devops-culture",
            },
        ]

    monkeypatch.setattr(
        "backend.app.tools.mcp_tools.MCPDocumentationClient.search_docs",
        _fake_mcp,
        raising=False,
    )

    # Read test architecture
    fixture_path = Path(__file__).parent / "fixtures" / "operational_sample_architecture.txt"
    architecture = fixture_path.read_text(encoding="utf-8")

    # Create agent and assess
    agent = OperationalAgent()
    assessment = await agent.assess_architecture(architecture)

    # Verify assessment structure
    assert "overall_maturity_percent" in assessment.maturity
    assert len(assessment.recommendations) == 3

    # Verify domain scores
    assert assessment.domain_scores.get("OE05", {}).get("score") == 10  # IaC
    assert assessment.domain_scores.get("OE06", {}).get("score") == 5   # CI/CD
    assert assessment.domain_scores.get("OE07", {}).get("score") == 20  # Monitoring
    assert assessment.domain_scores.get("OE11", {}).get("score") == 5   # Safe deployments

    # Verify recommendations
    rec = assessment.recommendations[0]
    assert rec["title"] == "Implement CI/CD pipelines for automated deployments"
    assert rec["priority"] == "Critical"
    assert rec["impact_score"] == 10
    assert "OE06" in rec["pillar_codes"]

    # Verify markdown output can be generated
    results_markdown = agent.build_results_markdown(assessment)
    assert len(results_markdown) > 0
    assert "operational" in results_markdown.lower()
