# Migrated from src.app.tools.mcp_tools with import path adjustments
from __future__ import annotations
import logging
from typing import List, Dict, Any
logger = logging.getLogger(__name__)
try:
    from agent_framework import HostedMCPTool
    from agent_framework.azure import AzureAIAgentClient
    from azure.identity.aio import AzureCliCredential
    _AF_AVAILABLE = True
except ImportError:
    _AF_AVAILABLE = False
try:
    from opentelemetry import trace
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False
    trace = None
LEARN_BASE = "https://learn.microsoft.com"
_STATIC_FALLBACK_REFS: Dict[str, List[Dict[str, Any]]] = {"reliability": [{"title": "Azure Well-Architected Framework - Reliability","url": f"{LEARN_BASE}/en-us/azure/architecture/framework/reliability/","summary": "Core principles and guidance for reliability in Azure architectures.","relevance": 0.95}],}
class MCPDocumentationClient:
    def __init__(self, enable_network: bool = True):
        self.enable_network = enable_network and _AF_AVAILABLE
    async def fetch_pillar_references(self, pillar: str, query: str, max_items: int = 6) -> List[Dict[str, Any]]:
        fallback = _STATIC_FALLBACK_REFS.get(pillar.lower(), _STATIC_FALLBACK_REFS.get("reliability", []))
        if not self.enable_network:
            return fallback[:max_items]
        prompt = f"List key Microsoft Learn documentation pages (title - URL) that help improve Azure architecture outcomes for the {pillar} pillar related to '{query}'. Only include Microsoft Learn links."
        try:
            async with AzureCliCredential() as credential, AzureAIAgentClient(async_credential=credential) as chat_client:
                try:
                    await chat_client.setup_azure_ai_observability()
                except Exception:
                    pass
                agent = chat_client.create_agent(name=f"{pillar.title()}DocsAgent", instructions="Return bullet list of title and URL", tools=HostedMCPTool(name="Microsoft Learn MCP", url="https://learn.microsoft.com/api/mcp", approval_mode="never_require"))
                result = await agent.run(prompt)
                text = getattr(result, "text", str(result))
                refs = self._parse_reference_lines(text)
                return (refs or fallback)[:max_items]
        except Exception:
            return fallback[:max_items]
    @staticmethod
    def _parse_reference_lines(text: str) -> List[Dict[str, Any]]:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        results: List[Dict[str, Any]] = []
        for line in lines:
            if LEARN_BASE not in line:
                continue
            parts = line.split(LEARN_BASE, 1)
            title = parts[0].strip("- •:\t") or "Azure Documentation"
            url = LEARN_BASE + parts[1].strip()
            results.append({"title": title[:160], "url": url, "summary": "", "relevance": 0.80})
        return results
class MCPToolManager:
    def __init__(self):
        self._client = MCPDocumentationClient()
    async def get_service_documentation(self, service_name: str, topic: str = "reliability") -> List[Dict[str, Any]]:
        query = f"{service_name} {topic}".strip()
        pillar = (service_name or topic or "reliability").lower().replace(" ", "_")
        refs = await self._client.fetch_pillar_references(pillar, query)
        return [{"title": r.get("title",""),"url": r.get("url",""),"summary": r.get("summary",""),"relevance": r.get("relevance",0.0)} for r in refs]
__all__ = ["MCPDocumentationClient","MCPToolManager"]
