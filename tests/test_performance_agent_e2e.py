"""End-to-end test for Performance Efficiency agent."""

import asyncio
import json

import pytest

from backend.app.agents.performance_agent import PerformanceAgent


@pytest.mark.asyncio
async def test_performance_agent_normalizes_recommendations(monkeypatch):
    """Test PerformanceAgent assessment with mocked agent framework."""
    sample_architecture = """
    Azure AKS deployment single region, no autoscale, manual incident response.
    No load tests, no profiling, limited telemetry, synchronous service calls.
    Cosmos DB single region, no partition key optimization, high RU waste.
    No capacity forecasting or documented SLOs.
    Critical user journey latency spikes unmonitored.
    Manual scaling via portal. No performance regression tracking.
    """

    fake_json = {
        "pillar": "performance",
        "domain_scores": {
            "PE01": {"score": 30, "title": "Performance Targets & SLIs/SLOs"},
            "PE02": {"score": 25, "title": "Capacity & Demand Planning"},
            "PE03": {"score": 55, "title": "Service & Architecture Selection"},
            "PE04": {"score": 40, "title": "Data Collection & Telemetry"},
            "PE05": {"score": 35, "title": "Scaling & Partitioning Strategy"},
            "PE06": {"score": 20, "title": "Performance Testing & Benchmarking"},
            "PE07": {"score": 38, "title": "Code & Runtime Optimization"},
            "PE08": {"score": 30, "title": "Data Usage Optimization"},
            "PE09": {"score": 28, "title": "Critical Flow Optimization"},
            "PE10": {"score": 45, "title": "Operational Load Efficiency"},
            "PE11": {"score": 50, "title": "Live Issue Triage & Remediation"},
            "PE12": {"score": 32, "title": "Continuous Optimization & Feedback Loop"}
        },
        "maturity_level": "Developing",
        "recommendations": [
            {
                "title": "Implement Autoscale for AKS and Cosmos DB",
                "description": "Introduce HPA and partition-aware scaling to reduce waste and handle spikes.",
                "priority": "Critical",
                "impact_score": 9,
                "pillar_codes": ["PE05", "PE02"]
            },
            {
                "title": "Introduce Load & Stress Testing Pipeline",
                "description": "Automate performance regression detection and baseline establishment.",
                "priority": "High",
                "impact_score": 8,
                "pillar_codes": ["PE06", "PE01"]
            },
            {
                "title": "Adopt Systematic Profiling & Hot Path Optimization",
                "description": "Use tracing and profiling to optimize top latency contributors.",
                "priority": "Medium",
                "impact_score": 7,
                "pillar_codes": ["PE07", "PE09"]
            }
        ]
    }

    async def _fake_init(self):  # type: ignore[override]
        async def _fake_run(self_inner, task, **kw):  # noqa: ARG001
            await asyncio.sleep(0)
            return json.dumps(fake_json)
        
        await asyncio.sleep(0)
        self.agent = type("Agent", (), {"run": _fake_run})()

    monkeypatch.setattr(PerformanceAgent, "_initialize_agent", _fake_init, raising=True)

    async def _fake_mcp(service: str, topic: str):  # noqa: ARG001
        await asyncio.sleep(0)
        return [
            {
                "title": "Performance Efficiency checklist",
                "url": "https://learn.microsoft.com/azure/well-architected/performance/checklist",
            },
            {
                "title": "Performance Efficiency principles",
                "url": "https://learn.microsoft.com/azure/well-architected/performance/principles",
            },
        ]

    monkeypatch.setattr(
        "backend.app.tools.mcp_tools.MCPDocumentationClient.search_docs",
        _fake_mcp,
        raising=False,
    )

    # Create agent and assess
    agent = PerformanceAgent()
    assessment = await agent.assess_architecture(sample_architecture)
    
    # Verify assessment structure (maturity comes from scoring engine, not LLM)
    assert "overall_maturity_percent" in assessment.maturity
    assert len(assessment.recommendations) == 3
    
    # Verify domain scores
    assert assessment.domain_scores.get("PE01", {}).get("score") == 30
    assert assessment.domain_scores.get("PE05", {}).get("score") == 35
    assert assessment.domain_scores.get("PE06", {}).get("score") == 20
    assert assessment.domain_scores.get("PE10", {}).get("score") == 45
    
    # Verify recommendations
    rec = assessment.recommendations[0]
    assert rec["title"] == "Implement Autoscale for AKS and Cosmos DB"
    assert rec["priority"] == "Critical"
    assert rec["impact_score"] == 9
    assert "PE05" in rec["pillar_codes"]
    
    # Verify markdown output can be generated
    results_markdown = agent.build_results_markdown(assessment)
    assert len(results_markdown) > 0
    assert "performance" in results_markdown.lower()
