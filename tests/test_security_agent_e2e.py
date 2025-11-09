"""Async end-to-end style test for the SecurityAgent using mocked dependencies."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict

import importlib
import pytest

import sys

_SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

SecurityAgent = None  # type: ignore
DOMAIN_TITLES: Dict[str, str] = {}


class _FakeLLMAgent:
    """Minimal async fake implementing .run returning an object with `.text`."""

    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

    async def run(self, prompt: str):  # noqa: ARG002 - prompt unused in fake
        class Response:
            text: str

        resp = Response()
        resp.text = json.dumps(self._payload)
        await asyncio.sleep(0)
        return resp


@pytest.mark.asyncio
async def test_security_agent_normalizes_recommendations(monkeypatch):
    global SecurityAgent, DOMAIN_TITLES

    if SecurityAgent is None:
        try:
            pillar_agent_base = importlib.import_module("app.agents.pillar_agent_base")
            security_constants = importlib.import_module("app.agents.security_constants")
            security_agent_module = importlib.import_module("app.agents.security_agent")
        except SystemExit:
            pytest.skip("Agent framework not installed; skipping security agent test")

        monkeypatch.setattr(pillar_agent_base, "AGENT_FRAMEWORK_AVAILABLE", True)
        SecurityAgent = getattr(security_agent_module, "SecurityAgent")
        DOMAIN_TITLES = security_constants.DOMAIN_TITLES

    fake_json: Dict[str, Any] = {
        "overall_score": 76,
        "domain_scores": {code: {"score": 70, "title": title} for code, title in DOMAIN_TITLES.items()},
        "recommendations": [
            {
                "title": "Enforce MFA",
                "description": "Require multifactor authentication for all admin roles",
                "priority": 1,
                "impact_score": 9,
                "pillar_codes": ["SE05"],
            },
            {
                "title": "Centralize logging",
                "description": "Integrate workload telemetry with Microsoft Sentinel",
                "priority": 2,
                "impact_score": 7,
                "pillar_codes": ["SE10"],
            },
        ],
    }

    async def _fake_init(self):  # type: ignore[override]
        await asyncio.sleep(0)
        self.agent = _FakeLLMAgent(fake_json)

    monkeypatch.setattr(SecurityAgent, "_initialize_agent", _fake_init, raising=True)

    async def _fake_mcp(service: str, topic: str):  # noqa: ARG001
        await asyncio.sleep(0)
        return [
            {
                "title": "Design review checklist for Security",
                "url": "https://learn.microsoft.com/azure/well-architected/security/checklist",
            },
            {
                "title": "Security design principles",
                "url": "https://learn.microsoft.com/azure/well-architected/security/principles",
            },
        ]

    try:
        agent = SecurityAgent(enable_mcp=True)
    except SystemExit:
        pytest.skip("Agent framework initialization failed; skipping security agent test")
    if agent.mcp_manager:
        monkeypatch.setattr(agent.mcp_manager, "get_service_documentation", _fake_mcp, raising=True)

    sample_architecture = Path("tests/fixtures/security_sample_architecture.txt").read_text(encoding="utf-8")
    assessment = await agent.assess_architecture(sample_architecture)

    assert assessment.overall_score == 76
    assert len(assessment.domain_scores) == len(DOMAIN_TITLES)
    for code, title in DOMAIN_TITLES.items():
        assert assessment.domain_scores[code]["title"] == title

    assert assessment.recommendations, "Expected recommendations list to be populated"
    assert all("severity" in rec for rec in assessment.recommendations)
    assert assessment.mcp_references, "Expected MCP references to be collected"
    assert "overall_maturity_percent" in assessment.maturity
