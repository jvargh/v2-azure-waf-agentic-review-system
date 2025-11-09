"""Minimal Azure AI Foundry Hosted MCP integration.
Returns Microsoft Learn reliability references with HostedMCPTool; falls back to static list if unavailable."""

from __future__ import annotations

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:  # Agent Framework imports (Hosted MCP pattern)
    from agent_framework import HostedMCPTool
    from agent_framework.azure import AzureAIAgentClient
    from azure.identity.aio import AzureCliCredential
    _AF_AVAILABLE = True
except ImportError:  # Libraries not present
    _AF_AVAILABLE = False

# OpenTelemetry for trace enrichment
try:
    from opentelemetry import trace
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False
    trace = None

LEARN_BASE = "https://learn.microsoft.com"

_STATIC_FALLBACK_REFS: Dict[str, List[Dict[str, Any]]] = {
    "reliability": [
        {
            "title": "Azure Well-Architected Framework - Reliability",
            "url": f"{LEARN_BASE}/en-us/azure/architecture/framework/reliability/",
            "summary": "Core principles and guidance for reliability in Azure architectures.",
            "relevance": 0.95,
        },
        {
            "title": "Reliability checklist",
            "url": f"{LEARN_BASE}/en-us/azure/well-architected/reliability/checklist",
            "summary": "Design review checklist for the Reliability pillar (RE01-RE10).",
            "relevance": 0.92,
        },
        {
            "title": "Reliability patterns",
            "url": f"{LEARN_BASE}/en-us/azure/architecture/framework/reliability/reliability-patterns",
            "summary": "Circuit breaker, bulkhead, retry, and related resilience patterns.",
            "relevance": 0.85,
        },
    ],
    "security": [
        {
            "title": "Azure Well-Architected Framework - Security",
            "url": f"{LEARN_BASE}/en-us/azure/architecture/framework/security/",
            "summary": "Security guidance aligned with Azure Well-Architected best practices.",
            "relevance": 0.95,
        },
        {
            "title": "Security checklist",
            "url": f"{LEARN_BASE}/en-us/azure/well-architected/security/checklist",
            "summary": "Design review checklist for Security pillar items SE:01-SE:12.",
            "relevance": 0.92,
        },
        {
            "title": "Zero Trust guidance center",
            "url": f"{LEARN_BASE}/en-us/security/zero-trust/azure-well-architected-security",
            "summary": "Zero Trust-aligned implementation tactics for Azure workloads.",
            "relevance": 0.88,
        },
    ],
    "cost_optimization": [
        {
            "title": "Azure Well-Architected Framework - Cost Optimization",
            "url": f"{LEARN_BASE}/en-us/azure/architecture/framework/cost/",
            "summary": "Cost optimization principles and governance patterns for Azure.",
            "relevance": 0.95,
        },
        {
            "title": "Cost Optimization checklist",
            "url": f"{LEARN_BASE}/en-us/azure/well-architected/cost-optimization/checklist",
            "summary": "Design review checklist covering CO:01-CO:14 activities.",
            "relevance": 0.92,
        },
        {
            "title": "Azure Cost Management best practices",
            "url": f"{LEARN_BASE}/en-us/azure/cost-management-billing/costs/cost-mgmt-best-practices",
            "summary": "Operational guardrails and automation opportunities for managing spend.",
            "relevance": 0.87,
        },
    ],
    "operational_excellence": [
        {
            "title": "Azure Well-Architected Framework - Operational Excellence",
            "url": f"{LEARN_BASE}/en-us/azure/architecture/framework/operational-excellence/",
            "summary": "Operational practices and DevOps culture recommendations for Azure workloads.",
            "relevance": 0.95,
        },
        {
            "title": "Operational Excellence checklist",
            "url": f"{LEARN_BASE}/en-us/azure/well-architected/operational-excellence/checklist",
            "summary": "Design review checklist for OE:01-OE:11 requirements.",
            "relevance": 0.92,
        },
        {
            "title": "Azure DevOps design guidelines",
            "url": f"{LEARN_BASE}/en-us/azure/architecture/framework/devops/devops-design-principles",
            "summary": "Guidance for building automated, observable operational pipelines.",
            "relevance": 0.88,
        },
    ],
    "performance_efficiency": [
        {
            "title": "Azure Well-Architected Framework - Performance Efficiency",
            "url": f"{LEARN_BASE}/en-us/azure/architecture/framework/performance/",
            "summary": "Principles for scaling workloads and meeting performance targets.",
            "relevance": 0.95,
        },
        {
            "title": "Performance Efficiency checklist",
            "url": f"{LEARN_BASE}/en-us/azure/well-architected/performance-efficiency/checklist",
            "summary": "Design review checklist for PE:01-PE:12 steps.",
            "relevance": 0.92,
        },
        {
            "title": "Performance tuning Azure applications",
            "url": f"{LEARN_BASE}/en-us/azure/architecture/framework/performance/performance-best-practices",
            "summary": "Best practices for monitoring, tuning, and scaling Azure workloads.",
            "relevance": 0.87,
        },
    ],
}


class MCPDocumentationClient:
    """Fetch Microsoft Learn reliability references (fallback to static)."""

    def __init__(self, enable_network: bool = True):
        self.enable_network = enable_network and _AF_AVAILABLE
        if self.enable_network:
            logger.info("MCPDocumentationClient initialized with live MCP capability")
        else:
            logger.warning("MCPDocumentationClient running in static fallback mode")

    async def fetch_pillar_references(self, pillar: str, query: str, max_items: int = 6) -> List[Dict[str, Any]]:
        """Return up to max_items Microsoft Learn links for the specified pillar."""
        fallback = _STATIC_FALLBACK_REFS.get(pillar.lower(), _STATIC_FALLBACK_REFS.get("reliability", []))
        if not self.enable_network:
            return fallback[:max_items]

        prompt = (
            "List key Microsoft Learn documentation pages (title - URL) that help improve Azure "
            f"architecture outcomes for the {pillar} pillar. Focus on checklist recommendations for: '{query}'. "
            "Only include Microsoft Learn links."
        )

        try:
            async with AzureCliCredential() as credential, AzureAIAgentClient(async_credential=credential) as chat_client:
                # Observability setup
                try:
                    await chat_client.setup_azure_ai_observability()
                    logger.info("MCP client observability configured successfully")
                except Exception as obs_err:
                    logger.warning(
                        "Failed to configure MCP observability (tracing will not be available): %s. "
                        "Ensure Application Insights is connected to your AI Foundry project.",
                        obs_err
                    )

                reliability_agent = chat_client.create_agent(
                    name=f"{pillar.title()}DocsAgent",
                    instructions=(
                        "You extract authoritative Microsoft Learn documentation references. "
                        "Return a short bullet list; each line must contain a title and a URL."
                    ),
                    tools=HostedMCPTool(
                        name="Microsoft Learn MCP",
                        url="https://learn.microsoft.com/api/mcp",
                        approval_mode="never_require",  # docs lookups are safe
                    ),
                )

                logger.info(
                    "Invoking DocsAgent for pillar '%s' with query: %s",
                    pillar,
                    query[:100]
                )
                
                # Add MCP request event to current span
                if _OTEL_AVAILABLE and trace:
                    current_span = trace.get_current_span()
                    if current_span and current_span.is_recording():
                        current_span.add_event(
                            name="mcp_docs_request",
                            attributes={
                                "mcp.pillar": pillar,
                                "mcp.query": query[:200],
                                "mcp.max_items": max_items,
                                "mcp.prompt_length": len(prompt),
                            }
                        )
                
                result = await reliability_agent.run(prompt)
                text = getattr(result, "text", str(result))
                refs = self._parse_reference_lines(text)
                
                logger.info(
                    "DocsAgent returned %d references from %d chars of output",
                    len(refs),
                    len(text)
                )
                
                # Add MCP response event to span
                if _OTEL_AVAILABLE and trace:
                    current_span = trace.get_current_span()
                    if current_span and current_span.is_recording():
                        event_attrs = {
                            "mcp.response_length": len(text),
                            "mcp.references_found": len(refs),
                        }
                        if refs:
                            event_attrs["mcp.doc.urls"] = "; ".join(r.get("url", "") for r in refs[:3])
                            event_attrs["mcp.doc.titles"] = "; ".join(r.get("title", "")[:60] for r in refs[:3])
                        current_span.add_event(
                            name="mcp_docs_response",
                            attributes=event_attrs
                        )
                
                if refs:
                    for idx, ref in enumerate(refs[:3]):  # Log first 3 URLs
                        logger.info("  [%d] %s - %s", idx + 1, ref.get("title", "")[:60], ref.get("url", ""))
                
                if not refs:
                    logger.info("MCP output parsed empty; returning static fallback")
                    return fallback[:max_items]
                return refs[:max_items]
        except Exception as exc:  # Broad fallback to keep agent resilient
            logger.warning(f"Hosted MCP retrieval failed ({exc}); returning static fallback")
            return fallback[:max_items]

    @staticmethod
    def _parse_reference_lines(text: str) -> List[Dict[str, Any]]:
        """Parse lines containing learn.microsoft.com into refs."""
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        results: List[Dict[str, Any]] = []
        for line in lines:
            if LEARN_BASE not in line:
                continue
            # Heuristic: split on first 'http'
            parts = line.split(LEARN_BASE, 1)
            title = parts[0].strip("- •:\t") or "Azure Documentation"
            url = LEARN_BASE + parts[1].strip()
            results.append({
                "title": title[:160],
                "url": url,
                "summary": "",  # Summary can be populated by a second enrichment step if needed
                "relevance": 0.80,
            })
        return results


# Backwards-compatible facade expected by ReliabilityAgent
class MCPToolManager:
    """Backward-compatible facade for ReliabilityAgent."""

    def __init__(self):
        self._client = MCPDocumentationClient()

    async def get_service_documentation(self, service_name: str, topic: str = "reliability") -> List[Dict[str, Any]]:
        query = f"{service_name} {topic}".strip()
        pillar = (service_name or topic or "reliability").lower().replace(" ", "_")
        refs = await self._client.fetch_pillar_references(pillar, query)
        # Normalize shape (already matches expected keys title/url/summary)
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "summary": r.get("summary", ""),
                "relevance": r.get("relevance", 0.0),
            }
            for r in refs
        ]

    # Additional previous APIs (query_documentation, etc.) intentionally removed for clarity.
    # If needed later, they can wrap MCPDocumentationClient with multi-topic queries.


__all__ = [
    "MCPDocumentationClient",
    "MCPToolManager",
]