"""Document analysis module for pre-processing uploaded artifacts.

Implements comprehensive LLM-powered analysis of:
- Architecture documents (narrative extraction, component identification)
- Diagrams (visual inference, topology extraction)
- Support cases (pattern classification, risk assessment)
"""

from __future__ import annotations

import asyncio
import csv
import io
import re
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING, Any
from dataclasses import dataclass

if TYPE_CHECKING:  # pragma: no cover
    from backend.app.services.llm_provider import LLMProvider


@dataclass
class AnalysisInsight:
    """Structured insight from document analysis."""
    category: str
    insight_type: str  # narrative|topology|pattern|risk
    content: str
    confidence: float
    pillar_alignment: List[str]  # Which pillars this insight relates to


class DocumentAnalyzer:
    """Analyzes uploaded documents to extract structured insights."""
    
    # Azure service patterns for component recognition
    AZURE_SERVICES = {
        "compute": [
            "app service", "azure functions", "container apps", "aks", "kubernetes",
            "virtual machine", "vm", "batch", "service fabric"
        ],
        "storage": [
            "blob storage", "storage account", "file storage", "data lake",
            "cosmos db", "sql database", "mysql", "postgresql", "redis cache"
        ],
        "networking": [
            "virtual network", "vnet", "application gateway", "load balancer",
            "front door", "traffic manager", "cdn", "vpn gateway", "firewall"
        ],
        "security": [
            "key vault", "managed identity", "azure ad", "entra id", "defender",
            "security center", "sentinel", "ddos protection"
        ],
        "monitoring": [
            "application insights", "log analytics", "monitor", "azure monitor",
            "service health", "resource health"
        ],
        "integration": [
            "event grid", "event hub", "service bus", "api management", "logic apps"
        ]
    }
    
    # Pillar-aligned keyword patterns
    PILLAR_PATTERNS = {
        "reliability": [
            "availability", "redundancy", "failover", "disaster recovery", "backup",
            "replication", "multi-region", "zone-redundant", "high availability", "sla",
            "resilience", "fault tolerance", "recovery point", "recovery time"
        ],
        "security": [
            "authentication", "authorization", "encryption", "key management", "secret",
            "certificate", "rbac", "identity", "access control", "compliance",
            "vulnerability", "threat", "security baseline", "zero trust", "mfa"
        ],
        "cost": [
            "cost optimization", "budget", "spending", "reserved instance", "reservation",
            "pricing tier", "sku", "scale down", "right-sizing", "advisor recommendation",
            "cost analysis", "cost management", "autoscale"
        ],
        "operational": [
            "monitoring", "logging", "telemetry", "ci/cd", "deployment", "pipeline",
            "devops", "automation", "infrastructure as code", "iac", "terraform", "bicep",
            "observability", "incident response", "runbook"
        ],
        "performance": [
            "latency", "throughput", "scalability", "performance", "caching", "cdn",
            "load balancing", "optimization", "bottleneck", "capacity planning",
            "response time", "concurrency", "async", "queue"
        ]
    }
    
    def __init__(self, llm_enabled: bool = True, llm_provider: Optional["LLMProvider"] = None):
        """Initialize analyzer.
        
        Args:
            llm_enabled: Whether to use LLM for enhanced analysis (falls back to patterns)
            llm_provider: Optional centralized LLM provider (replaces inline client creation)
        """
        self.llm_enabled = llm_enabled
        self.llm_provider = llm_provider
        self.azure_client = None
        
        # Legacy fallback: create inline client if provider not injected
        if llm_enabled and not llm_provider:
            try:
                from openai import AsyncAzureOpenAI
                import os
                endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                key = os.getenv("AZURE_OPENAI_API_KEY")
                api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
                if endpoint and key:
                    self.azure_client = AsyncAzureOpenAI(
                        azure_endpoint=endpoint,
                        api_key=key,
                        api_version=api_version,
                    )
            except Exception:
                pass  # Fail quietly if client unavailable
    
    async def analyze_architecture_document(
        self,
        content: str,
        filename: str
    ) -> Dict[str, any]:
        """Analyze architecture document and extract structured insights.
        
        Args:
            content: Document text content
            filename: Source filename
        
        Returns:
            Dict containing:
                - llm_analysis: Detailed narrative analysis
                - components_identified: List of Azure services detected
                - pillar_signals: Insights mapped to each pillar
                - architectural_patterns: Detected patterns
        """
        # Extract components
        components = self._identify_azure_services(content)
        
        # Map content to pillars
        pillar_signals = self._extract_pillar_signals(content)
        
        # Detect architectural patterns
        patterns = self._detect_patterns(content)
        
        # Generate comprehensive analysis
        analysis_text = self._generate_document_analysis(
            content, filename, components, pillar_signals, patterns
        )
        
        # Generate structured report
        structured_report = self._compose_structured_arch_doc_report(
            content, filename, components, pillar_signals, patterns
        )
        
        return {
            "llm_analysis": analysis_text,
            "components_identified": components,
            "pillar_signals": pillar_signals,
            "architectural_patterns": patterns,
            "key_insights": self._extract_key_insights(content, pillar_signals),
            "structured_report": structured_report
        }
    
    async def analyze_support_cases(
        self,
        csv_content: str,
        filename: str
    ) -> Dict[str, any]:
        """Analyze support case CSV and classify patterns.
        
        Args:
            csv_content: CSV file content
            filename: Source filename
        
        Returns:
            Dict containing:
                - llm_analysis: Pattern summary
                - thematic_patterns: Classified issue themes
                - risk_signals: Severity-weighted concerns
                - pillar_deviations: Issues mapped to pillars
        """
        cases = self._parse_csv_cases(csv_content)
        
        # Classify into themes
        themes = self._classify_case_themes(cases)
        
        # Extract risk signals
        risks = self._assess_case_risks(cases, themes)
        
        # Map to pillar deviations
        deviations = self._map_pillar_deviations(cases, themes)
        
        # Extract root cause patterns and resolution analysis
        root_cause_analysis = self._extract_root_cause_patterns(cases)
        
        # Generate analysis
        analysis_text = self._generate_case_analysis(filename, cases, themes, risks, root_cause_analysis)
        
        # Generate structured concerns report
        structured_report = self._compose_structured_case_concerns_report(
            filename, cases, themes, risks, root_cause_analysis
        )
        
        return {
            "llm_analysis": analysis_text,
            "thematic_patterns": themes,
            "risk_signals": risks,
            "pillar_deviations": deviations,
            "total_cases": len(cases),
            "high_severity_count": sum(1 for r in risks if r.get("severity") == "high"),
            "root_cause_analysis": root_cause_analysis,
            "structured_report": structured_report,
            "root_cause_samples": structured_report.get("root_cause_samples", []),
            "resolution_samples": structured_report.get("resolution_samples", []),
            "recurring_failure_patterns": structured_report.get("recurring_failure_patterns", [])
        }
    
    async def analyze_diagram(
        self,
        image_data: bytes,
        filename: str,
        content_type: str
    ) -> Dict[str, any]:
        """Extract textual signals from architecture diagram.
        
        Strategies (ordered):
          1. SVG: parse <text> nodes directly.
          2. Heuristic filename/entity tokens.
          3. Optional Azure OpenAI vision summarization (multimodal) if enabled.
        
        Args:
            image_data: Image binary data
            filename: Source filename
            content_type: MIME type
        
        Returns:
            Dict containing:
                - type: "diagram"
                - filename: source filename
                - bytes: file size
                - mime: content type
                - extracted_text: extracted textual content (from SVG nodes, filename heuristics)
                - summary: high-level bullet summary

        # Combined markdown for simpler UI rendering parity with diagram structured view
        combined_parts: List[str] = []
        combined_parts.append(f"# Architecture Document: {filename}\n\n")
        combined_parts.append("## Executive Summary\n\n" + executive_summary.strip() + "\n\n")
        combined_parts.append("## Architecture Overview\n\n" + architecture_overview.strip() + "\n\n")
        combined_parts.append("## Cross-Cutting Concerns\n\n")
        for k in sorted(cross_cutting.keys()):
            combined_parts.append(f"### {k.replace('_',' ').title()}\n\n" + cross_cutting[k].strip() + "\n\n")
        combined_parts.append("## Deployment Summary\n\n" + deployment_summary.strip() + "\n\n")
        combined_parts.append("## Evidence Sources\n\n")
        # Summarize evidence counts
        if evidence_sources.get("services"):
            combined_parts.append("### Services (top 10)\n\n" + "\n".join(
                f"- {svc} (x{data['occurrences']})" for svc, data in list(evidence_sources["services"].items())[:10]
            ) + "\n\n")
        if evidence_sources.get("pillars"):
            combined_parts.append("### Pillars\n\n" + "\n".join(
                f"- {pil} (x{data['count']})" for pil, data in evidence_sources["pillars"].items()
            ) + "\n\n")
        if evidence_sources.get("patterns"):
            combined_parts.append("### Patterns\n\n" + "\n".join(f"- {p}" for p in evidence_sources["patterns"].keys()) + "\n\n")
        combined_markdown = "".join(combined_parts)
                - strategy: comma-separated list of extraction strategies used
                - llm_analysis: summary text for compatibility
        """
        size = len(image_data)
        lower_name = filename.lower()
        strategy_chain: List[str] = []
        extracted_segments: List[str] = []

        # 1. SVG direct text extraction
        if content_type.endswith("svg") or lower_name.endswith(".svg"):
            try:
                import xml.etree.ElementTree as ET
                tree = ET.fromstring(image_data.decode("utf-8", errors="ignore"))
                texts = []
                for node in tree.iter():
                    if node.tag.endswith("text") and node.text and node.text.strip():
                        texts.append(node.text.strip())
                if texts:
                    extracted_segments.extend(texts)
                    strategy_chain.append("svg_text_nodes")
            except Exception as e:  # pragma: no cover - malformed SVG
                strategy_chain.append(f"svg_parse_error:{e.__class__.__name__}")

        # 2. Heuristic filename/entity tokenization (camelCase / separators)
        base_name = lower_name.replace(".svg", "").replace(".png", "").replace(".jpg", "").replace(".jpeg", "")
        tokens = re.split(r"[-_\.]+", base_name)
        camel_tokens: List[str] = []
        for t in tokens:
            parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", t)
            if parts:
                camel_tokens.extend(parts)
        meaningful = [p for p in camel_tokens if len(p) > 2][:25]
        if meaningful:
            extracted_segments.append("Filename tokens: " + ", ".join(sorted(set(meaningful))))
            strategy_chain.append("filename_tokens")

        # 3. Optional Azure vision summarization (attempt once)
        vision_summary = None
        
        # Priority 1: Use llm_provider.vision() if available
        if self.llm_provider:
            print(f"[DIAGRAM] llm_provider available, vision_enabled={self.llm_provider.settings.vision_enabled}, vision_deployment={self.llm_provider.settings.vision_deployment}")
            try:
                import base64
                b64 = base64.b64encode(image_data).decode("utf-8")
                ext = "png"
                if "png" in content_type:
                    ext = "png"
                elif "jpeg" in content_type or "jpg" in content_type:
                    ext = "jpeg"
                elif "svg" in content_type:
                    ext = "svg+xml"
                
                prompt = ("You are an Azure Well-Architected assistant. Extract key Azure service names, "
                          "components, tiers, and any resiliency/security/cost/performance hints from this architecture diagram. "
                          "Return a concise bullet list (max 12 bullets).")
                messages = [
                    {"role": "system", "content": "You convert diagrams into structured architecture bullet points."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/{ext};base64,{b64}"}}
                    ]}
                ]
                print(f"[DIAGRAM] Calling llm_provider.vision() with {len(b64)} base64 chars")
                result = await self.llm_provider.vision(messages)
                print(f"[DIAGRAM] Vision result type: {type(result)}, keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
                if result and not result.get("error") and not result.get("disabled"):
                    # Provider now always returns dict with proper structure
                    vision_summary = (result['choices'][0]['message']['content'] or "").strip()
                    print(f"[DIAGRAM] Vision summary extracted: {len(vision_summary)} chars")
                    if vision_summary:
                        strategy_chain.append("llm_provider_vision")
                elif result.get("error"):
                    error_msg = str(result.get('error'))[:100]
                    print(f"[DIAGRAM] Vision returned error: {error_msg}")
                    strategy_chain.append(f"vision_error:{error_msg[:50]}")
                elif result.get("disabled"):
                    print(f"[DIAGRAM] Vision is disabled in provider settings")
                    strategy_chain.append("vision_disabled")
            except Exception as e:
                print(f"[DIAGRAM] Vision exception: {e.__class__.__name__}: {e}")
                strategy_chain.append(f"vision_error:{e.__class__.__name__}")
        
        # Priority 2: Fallback to legacy azure_client if provider not available
        elif self.azure_client:
            import os
            deployment = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            if deployment:
                try:  # pragma: no cover - external call
                    import base64
                    b64 = base64.b64encode(image_data).decode("utf-8")
                    ext = "png"
                    if "png" in content_type:
                        ext = "png"
                    elif "jpeg" in content_type or "jpg" in content_type:
                        ext = "jpeg"
                    elif "svg" in content_type:
                        ext = "svg+xml"
                    
                    prompt = ("You are an Azure Well-Architected assistant. Extract key Azure service names, "
                              "components, tiers, and any resiliency/security/cost/performance hints from this architecture diagram. "
                              "Return a concise bullet list (max 12 bullets).")
                    response = await self.azure_client.chat.completions.create(
                        model=deployment,
                        messages=[
                            {"role": "system", "content": "You convert diagrams into structured architecture bullet points."},
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/{ext};base64,{b64}"}}
                            ]}
                        ],
                        temperature=0.2,
                        max_tokens=400
                    )
                    vision_summary = (response.choices[0].message.content or "").strip()
                    if vision_summary:
                        strategy_chain.append("azure_vision_summary")
                except Exception as e:
                    strategy_chain.append(f"vision_error:{e.__class__.__name__}")

        extracted_text = "\n".join(extracted_segments).strip()
        # Fallback summary logic
        summary_source = vision_summary or (extracted_text if extracted_text else f"Diagram placeholder (size={size} bytes).")
        print(f"[DIAGRAM] vision_summary={'SET' if vision_summary else 'EMPTY'}, extracted_text={len(extracted_text)} chars, summary_source={len(summary_source)} chars")
        summary = self._basic_summary(summary_source, max_sentences=5)
        
        # Generate structured report (pass vision_summary explicitly so report can distinguish vision vs heuristic content)
        structured_report = self._compose_structured_diagram_report(
            extracted_text, summary, filename, size, vision_summary=vision_summary
        )
        print(f"[DIAGRAM] structured_report executive_summary preview: {structured_report.get('executive_summary', '')[:200]}")

        return {
            "type": "diagram",
            "filename": filename,
            "bytes": size,
            "mime": content_type,
            "extracted_text": extracted_text,
            "summary": summary,
            "strategy": ",".join(strategy_chain) if strategy_chain else "none",
            "llm_analysis": summary,
            "structured_report": structured_report
        }
    
    def _basic_summary(self, text: str, *, max_sentences: int = 5) -> str:
        """Generate a basic summary from text by extracting first N sentences."""
        # Naive sentence boundary split
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        summary = " ".join(parts[:max_sentences])
        if len(parts) > max_sentences:
            summary += " ..."
        return summary[:1200]
    
    def _identify_azure_services(self, content: str) -> List[Dict[str, str]]:
        """Identify Azure services mentioned in content."""
        content_lower = content.lower()
        found = []
        
        for category, services in self.AZURE_SERVICES.items():
            for service in services:
                if service in content_lower:
                    found.append({"service": service, "category": category})
        
        return found
    
    def _extract_pillar_signals(self, content: str) -> Dict[str, List[str]]:
        """Extract signals relevant to each pillar."""
        content_lower = content.lower()
        signals = {}
        
        for pillar, keywords in self.PILLAR_PATTERNS.items():
            matches = []
            for keyword in keywords:
                if keyword in content_lower:
                    # Extract context around keyword
                    pattern = rf"[^.!?]*{re.escape(keyword)}[^.!?]*[.!?]"
                    contexts = re.findall(pattern, content, re.IGNORECASE)
                    if contexts:
                        matches.extend(contexts[:2])  # Limit to 2 contexts per keyword
            
            if matches:
                signals[pillar] = matches[:5]  # Limit to top 5 signals per pillar
        
        return signals
    
    def _detect_patterns(self, content: str) -> List[str]:
        """Detect common architectural patterns."""
        content_lower = content.lower()
        patterns = []
        
        pattern_indicators = {
            "Microservices": ["microservice", "container", "kubernetes", "aks", "service mesh"],
            "Event-Driven": ["event", "message", "queue", "service bus", "event grid"],
            "CQRS": ["cqrs", "command", "query", "event sourcing"],
            "Layered": ["tier", "layer", "presentation", "business logic", "data layer"],
            "Hub-Spoke": ["hub", "spoke", "hub-spoke", "virtual network"],
            "Gateway Pattern": ["api gateway", "application gateway", "reverse proxy"]
        }
        
        for pattern_name, indicators in pattern_indicators.items():
            if any(ind in content_lower for ind in indicators):
                patterns.append(pattern_name)
        
        return patterns
    
    def _generate_document_analysis(
        self,
        content: str,
        filename: str,
        components: List[Dict],
        signals: Dict[str, List[str]],
        patterns: List[str]
    ) -> str:
        """Generate concise document analysis narrative with enriched pillar context."""
        
        lines = ["Architecture Evidence Summary", ""]
        
        # Component summary
        if components:
            lines.append("Identified Azure Services:")
            categories = {}
            for comp in components:
                cat = comp["category"]
                categories.setdefault(cat, []).append(comp["service"])
            for cat, services in categories.items():
                lines.append(f"  • {cat.title()}: {', '.join(set(services))}")
            lines.append("")
        
        # Patterns
        if patterns:
            lines.append(f"Architectural Patterns Detected: {', '.join(patterns)}")
            lines.append("")
        
        # Pillar insights with contextual excerpts
        lines.append("Well-Architected Pillar Signals:")
        for pillar in ["reliability", "security", "cost", "operational", "performance"]:
            pillar_signals = signals.get(pillar, [])
            if pillar_signals:
                count = len(pillar_signals)
                lines.append(f"  • {pillar.title()}: {count} signal(s)")
                # Include up to 3 short excerpts for context
                for i, excerpt in enumerate(pillar_signals[:3]):
                    truncated = excerpt.strip()[:120]
                    if len(excerpt.strip()) > 120:
                        truncated += "..."
                    lines.append(f"    - \"{truncated}\"")
        lines.append("")
        
        # Content summary
        word_count = len(content.split())
        lines.append(f"Document contains {word_count} words of architectural context.")
        
        return "\n".join(lines)
    
    def _parse_csv_cases(self, csv_content: str) -> List[Dict[str, str]]:
        """Parse CSV support cases into a list of dictionaries.

        Robust fallback: if DictReader fails, build dicts manually from header row.
        Returns empty list for insufficient rows.
        """
        key_columns = {"title", "msdfm_rootcausedescription", "msdfm_resolution"}
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            cases = []
            for row in reader:
                if not isinstance(row, dict):
                    continue
                # Normalize presence of required columns; if missing create empty keys for downstream uniformity
                for col in key_columns:
                    if col not in row:
                        row[col] = ""
                cases.append(row)
            if cases:
                return cases
        except Exception:
            pass
        # Fallback simple parsing
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        if len(rows) < 2:
            return []
        header = rows[0]
        normalized_header = [h.strip() or f"col_{i}" for i, h in enumerate(header)]
        parsed: List[Dict[str, str]] = []
        for row in rows[1:]:
            if not any(cell.strip() for cell in row):
                continue
            entry = {normalized_header[i]: row[i] for i in range(min(len(normalized_header), len(row)))}
            # Ensure enrichment keys exist even if absent in CSV header
            for col in key_columns:
                entry.setdefault(col, "")
            parsed.append(entry)
        return parsed

    def _classify_case_themes(self, cases: List[Dict[str, str]]) -> Dict[str, List[Dict]]:
        """Classify cases into thematic buckets (authentication, latency, etc.)."""
        themes: Dict[str, List[Dict]] = {
            "authentication": [],
            "latency": [],
            "availability": [],
            "configuration": [],
            "security": [],
            "cost": [],
            "other": []
        }
        for case in cases:
            case_text = " ".join(str(v) for v in case.values()).lower()
            if any(k in case_text for k in ["auth", "login", "token", "401", "403"]):
                themes["authentication"].append(case)
            elif any(k in case_text for k in ["slow", "latency", "timeout", "performance"]):
                themes["latency"].append(case)
            elif any(k in case_text for k in ["down", "outage", "unavailable", "503", "500"]):
                themes["availability"].append(case)
            elif any(k in case_text for k in ["config", "setting", "parameter", "misconfigur"]):
                themes["configuration"].append(case)
            elif any(k in case_text for k in ["security", "vulnerability", "breach", "unauthorized"]):
                themes["security"].append(case)
            elif any(k in case_text for k in ["cost", "bill", "charge", "expensive"]):
                themes["cost"].append(case)
            else:
                themes["other"].append(case)
        return {k: v for k, v in themes.items() if v}
    
    def _extract_root_cause_patterns(self, cases: List[Dict]) -> Dict[str, any]:
        """Extract and analyze root cause descriptions from support cases."""
        root_causes = []
        resolutions = []
        
        for case in cases:
            root_cause = case.get('msdfm_rootcausedescription', '') or case.get('root_cause', '')
            resolution = case.get('msdfm_resolution', '') or case.get('resolution', '')
            
            if root_cause and isinstance(root_cause, str) and len(root_cause.strip()) > 5:
                root_causes.append(root_cause.strip())
            if resolution and isinstance(resolution, str) and len(resolution.strip()) > 5:
                resolutions.append(resolution.strip())
        
        # Aggregate patterns
        recurring_failures = {}
        for rc in root_causes:
            rc_lower = rc.lower()
            # Simple keyword extraction for recurring themes
            if 'timeout' in rc_lower or 'latency' in rc_lower:
                recurring_failures['performance_timeout'] = recurring_failures.get('performance_timeout', 0) + 1
            elif 'config' in rc_lower or 'misconfigur' in rc_lower:
                recurring_failures['configuration_error'] = recurring_failures.get('configuration_error', 0) + 1
            elif 'auth' in rc_lower or 'permission' in rc_lower:
                recurring_failures['authentication_failure'] = recurring_failures.get('authentication_failure', 0) + 1
            elif 'unavailable' in rc_lower or 'down' in rc_lower:
                recurring_failures['availability_issue'] = recurring_failures.get('availability_issue', 0) + 1
        
        # Resolution quality assessment
        resolution_quality = "unknown"
        if resolutions:
            avg_resolution_length = sum(len(r) for r in resolutions) / len(resolutions)
            if avg_resolution_length > 200:
                resolution_quality = "detailed"
            elif avg_resolution_length > 80:
                resolution_quality = "moderate"
            else:
                resolution_quality = "brief"
        
        return {
            "root_cause_count": len(root_causes),
            "resolution_count": len(resolutions),
            "recurring_failure_patterns": recurring_failures,
            "resolution_quality": resolution_quality,
            "unresolved_gaps": len(cases) - len(resolutions),
            "top_root_causes": sorted(recurring_failures.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _assess_case_risks(
        self,
        cases: List[Dict],
        themes: Dict[str, List[Dict]]
    ) -> List[Dict[str, any]]:
        """Assess risk levels from support cases."""
        risks = []
        
        for theme, theme_cases in themes.items():
            if not theme_cases:
                continue
            
            count = len(theme_cases)
            severity = "low"
            
            if count >= 5:
                severity = "high"
            elif count >= 2:
                severity = "medium"
            
            # Check for recurring patterns
            recurrence_indicator = "concentrated recurrence" if count >= 3 else "isolated incidents"
            
            risks.append({
                "theme": theme,
                "severity": severity,
                "case_count": count,
                "pattern": recurrence_indicator,
                "risk_qualifier": self._risk_qualifier(theme, count)
            })
        
        return risks
    
    def _risk_qualifier(self, theme: str, count: int) -> str:
        """Generate risk qualifier text."""
        qualifiers = {
            "authentication": "User access friction and potential security exposure",
            "latency": "Performance degradation affecting user experience",
            "availability": "Service reliability concerns and potential SLA violations",
            "security": "Systemic vulnerability indicators requiring immediate attention",
            "configuration": "Operational consistency and deployment quality concerns",
            "cost": "Resource optimization opportunities and budget management"
        }
        
        base = qualifiers.get(theme, "Operational pattern requiring review")
        if count >= 5:
            return f"CRITICAL: {base} (high recurrence)"
        elif count >= 2:
            return f"ELEVATED: {base} (moderate recurrence)"
        return base
    
    def _map_pillar_deviations(
        self,
        cases: List[Dict],
        themes: Dict[str, List[Dict]]
    ) -> Dict[str, List[str]]:
        """Map case themes to pillar deviations."""
        deviations = {}
        
        theme_to_pillar = {
            "authentication": ["security", "reliability"],
            "latency": ["performance", "operational"],
            "availability": ["reliability", "operational"],
            "security": ["security"],
            "configuration": ["operational"],
            "cost": ["cost", "operational"]
        }
        
        for theme, theme_cases in themes.items():
            if not theme_cases:
                continue
            
            pillars = theme_to_pillar.get(theme, ["operational"])
            deviation_text = f"{theme.title()} issues ({len(theme_cases)} cases)"
            
            for pillar in pillars:
                deviations.setdefault(pillar, []).append(deviation_text)
        
        return deviations
    
    def _generate_case_analysis(
        self,
        filename: str,
        cases: List[Dict],
        themes: Dict[str, List[Dict]],
        risks: List[Dict],
        root_cause_analysis: Dict[str, any]
    ) -> str:
        """Generate support case analysis narrative."""
        
        lines = [f"Support Case Analysis: {filename}", ""]
        lines.append(f"Total Cases Analyzed: {len(cases)}")
        lines.append("")
        
        if themes:
            lines.append("Thematic Patterns Identified:")
            for theme, theme_cases in sorted(themes.items(), key=lambda x: len(x[1]), reverse=True):
                lines.append(f"  • {theme.title()}: {len(theme_cases)} cases")
            lines.append("")
        
        if risks:
            high_risks = [r for r in risks if r["severity"] == "high"]
            if high_risks:
                lines.append("High-Severity Risk Patterns:")
                for risk in high_risks:
                    lines.append(f"  ⚠ {risk['theme'].title()}: {risk['risk_qualifier']}")
                lines.append("")

        # Recurring failure motifs (from root cause analysis)
        if root_cause_analysis:
            patterns = root_cause_analysis.get("top_root_causes", [])
            if patterns:
                lines.append("Recurring Failure Motifs:")
                for name, count in patterns:
                    pretty = name.replace('_', ' ').title()
                    lines.append(f"  • {pretty} (observed {count} times)")
                lines.append("")

        # Representative root cause samples
        sample_root_causes: List[str] = []
        sample_resolutions: List[str] = []
        if cases:
            seen_rc = set()
            seen_res = set()
            for case in cases:
                rc = case.get('msdfm_rootcausedescription', '') or case.get('root_cause', '')
                res = case.get('msdfm_resolution', '') or case.get('resolution', '')
                if rc and isinstance(rc, str):
                    norm = rc.strip()
                    if len(norm) > 20 and norm[:160] not in seen_rc:
                        seen_rc.add(norm[:160])
                        sample_root_causes.append(norm[:240])
                if res and isinstance(res, str):
                    normr = res.strip()
                    if len(normr) > 20 and normr[:160] not in seen_res:
                        seen_res.add(normr[:160])
                        sample_resolutions.append(normr[:240])
                if len(sample_root_causes) >= 5 and len(sample_resolutions) >= 5:
                    break
        if sample_root_causes:
            lines.append("Representative Root Cause Excerpts:")
            for rc in sample_root_causes:
                lines.append(f"  • {rc}")
            lines.append("")
        if sample_resolutions:
            lines.append("Resolution Approach Samples:")
            for rs in sample_resolutions:
                lines.append(f"  • {rs}")
            lines.append("")
        
        lines.append("Historical support cases provide operational reality context.")
        lines.append("Incident signals will inform reactive recommendations and gap identification.")
        
        return "\n".join(lines)
    
    def _compose_structured_arch_doc_report(
        self,
        content: str,
        filename: str,
        components: List[Dict[str, str]],
        pillar_signals: Dict[str, List[str]],
        patterns: List[str]
    ) -> Dict[str, any]:
        """Compose structured report for architecture document with parity to diagram analysis.

        Sections:
          - executive_summary (multi-paragraph; pattern + workload + infra + resilience/compliance only if evidenced)
          - architecture_overview (numbered subsections + detected patterns + component grouping)
          - cross_cutting_concerns (security, scalability, availability, observability plus conditional cost_optimization, compliance_governance)
          - deployment_summary (component category table + automation/governance notes)
          - evidence_sources (pillar/service excerpts; max 3 each)

        All content is strictly evidence-based: no extrapolation beyond detected keywords, components or pillar signals.
        """
        raw_lower = content.lower()

        # Distinct services
        distinct_services = []
        by_category: Dict[str, List[str]] = {}
        for comp in components:
            svc = comp.get("service", "").strip()
            cat = comp.get("category", "general")
            if svc:
                if svc not in distinct_services:
                    distinct_services.append(svc)
                by_category.setdefault(cat, []).append(svc)

        # Executive Summary construction
        exec_parts: List[str] = []
        exec_parts.append(f"This Azure architecture document ('{filename}') describes ")
        if patterns:
            primary = patterns[0].lower()
            if "micro" in primary:
                exec_parts.append("a microservices-based design emphasizing modularity and independent deployment. ")
            elif "event" in primary:
                exec_parts.append("an event-driven approach favoring asynchronous communication and decoupling. ")
            elif "hub" in primary or "spoke" in primary:
                exec_parts.append("a hub-spoke network topology for centralized connectivity and governance. ")
            elif "layer" in primary or "tier" in primary:
                exec_parts.append("a layered architecture with clear separation of concerns. ")
            else:
                exec_parts.append(f"a {primary} pattern optimized for cloud operations. ")
        else:
            exec_parts.append("a cloud architecture focused on reliability, security, and operational efficiency. ")

        # Workload / user hints (only if present)
        if any(k in raw_lower for k in ["user", "customer", "partner", "client", "consumer"]):
            if "partner" in raw_lower or "b2b" in raw_lower:
                exec_parts.append("It serves partner/B2B integration scenarios. ")
            if "customer" in raw_lower or "consumer" in raw_lower:
                exec_parts.append("It includes externally facing customer workloads. ")
            if "internal" in raw_lower or "operations" in raw_lower:
                exec_parts.append("Internal operational users are also referenced. ")

        # Key infrastructure highlights (top 3 based on categories present)
        infra_highlights: List[str] = []
        if "networking" in by_category:
            if any("front door" in s for s in by_category["networking"]):
                infra_highlights.append("Azure Front Door for global routing and edge security")
            elif any("application gateway" in s for s in by_category["networking"]):
                infra_highlights.append("Application Gateway enabling layer-7 load balancing")
        if "compute" in by_category:
            if any("aks" in s or "kubernetes" in s for s in by_category["compute"]):
                infra_highlights.append("Azure Kubernetes Service for container orchestration")
            elif any("app service" in s for s in by_category["compute"]):
                infra_highlights.append("Azure App Service hosting web application tiers")
            elif any("function" in s for s in by_category["compute"]):
                infra_highlights.append("Azure Functions delivering event-driven serverless logic")
        if "storage" in by_category:
            if any("sql" in s for s in by_category["storage"]):
                if any(k in raw_lower for k in ["geo-replic", "failover group", "replica"]):
                    infra_highlights.append("Azure SQL Database with geo-replication for data resilience")
                else:
                    infra_highlights.append("Azure SQL Database for relational persistence")
            elif any("cosmos" in s for s in by_category["storage"]):
                infra_highlights.append("Azure Cosmos DB for globally distributed data")
        if infra_highlights:
            exec_parts.append("The architecture leverages ")
            exec_parts.append(", ".join(infra_highlights[:3]))
            if len(infra_highlights) > 3:
                exec_parts.append(", and additional supporting Azure services")
            exec_parts.append(". ")

        # Resilience/compliance statements (only if evidenced)
        if any(k in raw_lower for k in ["multi-region", "multi region", "geo-replic", "failover", "zone-redundant", "availability zone"]):
            exec_parts.append("Resilience mechanisms (multi-region, replication or zone redundancy) are referenced. ")
        if any(k in raw_lower for k in ["azure policy", "blueprint", "compliance", "pci", "hipaa", "soc2", "iso", "nist", "governance"]):
            exec_parts.append("Governance and compliance considerations appear in the document. ")

        # Quantitative summary
        exec_parts.append(f"Identified {len(distinct_services)} distinct Azure services")
        if patterns:
            exec_parts.append(f" and {len(patterns)} architectural pattern(s)")
        pillars_with_signals = sum(1 for p in pillar_signals if pillar_signals.get(p))
        exec_parts.append(f"; evidence across {pillars_with_signals} pillar(s).")
        executive_summary = "".join(exec_parts).strip()

        # Architecture Overview subsections
        overview_parts: List[str] = []
        overview_parts.append("### 1. Component Distribution\n\n")
        if by_category:
            for cat in sorted(by_category.keys()):
                services = sorted(set(by_category[cat]))
                overview_parts.append(f"**{cat.title()}**: ")
                overview_parts.append(", ".join(services[:12]) + "\n\n")
        else:
            overview_parts.append("No Azure services explicitly identified.\n\n")

        overview_parts.append("### 2. Networking & Connectivity\n\n")
        net_lines: List[str] = []
        if any(k in raw_lower for k in ["virtual network", "vnet"]):
            net_lines.append("Virtual Network segmentation provides isolation.")
        if "subnet" in raw_lower:
            net_lines.append("Multiple subnets separate functional tiers.")
        if any(k in raw_lower for k in ["private endpoint", "private link"]):
            net_lines.append("Private Endpoints restrict PaaS exposure.")
        if any(k in raw_lower for k in ["nsg", "network security group"]):
            net_lines.append("Network Security Groups govern traffic flows.")
        if "dns" in raw_lower:
            net_lines.append("DNS or private zones manage name resolution.")
        overview_parts.append((" ".join(net_lines) if net_lines else "Networking details not explicitly documented.") + "\n\n")

        overview_parts.append("### 3. Identity & Access\n\n")
        id_lines: List[str] = []
        if any(k in raw_lower for k in ["entra", "azure ad", "active directory"]):
            id_lines.append("Microsoft Entra ID (Azure AD) centralizes identity management.")
        if any(k in raw_lower for k in ["rbac", "role-based"]):
            id_lines.append("Role-Based Access Control enforces least privilege.")
        if "managed identity" in raw_lower or "managed identities" in raw_lower:
            id_lines.append("Managed Identities remove credential embedding.")
        overview_parts.append((" ".join(id_lines) if id_lines else "Identity approach not described.") + "\n\n")

        overview_parts.append("### 4. Data Management & Persistence\n\n")
        data_lines: List[str] = []
        if any("sql" in s for s in by_category.get("storage", [])):
            data_lines.append("Azure SQL Database provides relational persistence.")
            if any(k in raw_lower for k in ["geo-replic", "failover group", "replica"]):
                data_lines.append("Geo-replication or failover groups enhance durability.")
        if any("cosmos" in s for s in by_category.get("storage", [])):
            data_lines.append("Azure Cosmos DB offers globally distributed NoSQL storage.")
        if any(k in raw_lower for k in ["blob", "storage account", "data lake"]):
            data_lines.append("Blob/Data Lake storage covers unstructured data.")
        overview_parts.append((" ".join(data_lines) if data_lines else "Data persistence strategy not explicitly documented.") + "\n\n")

        overview_parts.append("### 5. Detected Architectural Patterns\n\n")
        if patterns:
            overview_parts.append("\n".join(f"• {p}" for p in patterns) + "\n")
        else:
            overview_parts.append("• (No explicit patterns detected)\n")

        architecture_overview = "".join(overview_parts)

        # Cross-Cutting Concerns (enhanced + conditional)
        cross_cutting: Dict[str, str] = {}
        cross_cutting["security"] = self._dimensional_concern_summary("security", pillar_signals.get("security", []), content)
        cross_cutting["scalability"] = self._dimensional_concern_summary("scalability", pillar_signals.get("performance", []), content)
        cross_cutting["availability"] = self._dimensional_concern_summary("availability", pillar_signals.get("reliability", []), content)
        cross_cutting["observability"] = self._dimensional_concern_summary("observability", pillar_signals.get("operational", []), content)

        # --- Conditional Cost Optimization Inclusion (tightened gating) ---
        # Previous logic could surface cost_optimization for sparse single keyword mentions.
        # New gating REQUIRES evidence density across distinct sentences:
        #   Include ONLY IF one of:
        #     A) >= 2 distinct non-generic cost keywords AND >= 2 distinct sentences each containing a non-generic keyword
        #     B) Pillar cost signals (>=2 excerpts) AND >= 2 distinct non-generic cost keywords
        #     C) Strategic combo (strong + governance term) AND >= 2 high-signal sentences (length>40 chars) containing cost keywords
        cost_keywords = ["cost ", "budget", "reserved", "reservation", "pricing", "sku", "rightsizing", "right-sizing", "right sizing", "advisor", "savings plan", "finops", "cost management"]
        strong_terms = {"finops", "savings plan", "reserved", "reservation", "rightsizing", "right-sizing", "right sizing"}
        governance_terms = {"budget", "advisor", "cost management"}
        found_terms = {kw.strip() for kw in cost_keywords if kw in raw_lower}
        distinct_non_generic = {t for t in found_terms if t and not t.startswith("cost")}
        strategic_combo = (strong_terms & found_terms) and (governance_terms & found_terms)
        # Sentence-level evidence extraction
        sentences = re.split(r"(?<=[.!?])\s+", content)
        cost_sentences = []
        high_signal_cost_sentences = []
        for s in sentences:
            ls = s.lower()
            if any(kw for kw in cost_keywords if kw in ls):
                if any(kw for kw in distinct_non_generic if kw in ls):
                    cost_sentences.append(s.strip())
                    if len(s) > 40:
                        high_signal_cost_sentences.append(s.strip())
        # Fallback: treat line-level entries (bullet points) as sentences if punctuation sparse
        if len(cost_sentences) < 2:
            for line in content.splitlines():
                ll = line.lower().strip()
                if any(kw for kw in cost_keywords if kw in ll):
                    if any(kw for kw in distinct_non_generic if kw in ll):
                        if line.strip() not in cost_sentences:
                            cost_sentences.append(line.strip())
                        if len(line) > 40 and line.strip() not in high_signal_cost_sentences:
                            high_signal_cost_sentences.append(line.strip())
        # Distinct sentence count using first 60 chars hash to avoid duplicates
        def _distinct(sent_list: List[str]) -> int:
            seen = set()
            for s in sent_list:
                key = s[:60]
                if key not in seen:
                    seen.add(key)
            return len(seen)
        distinct_cost_sentence_count = _distinct(cost_sentences)
        distinct_high_signal_sentence_count = _distinct(high_signal_cost_sentences)
        pillar_cost_signals = pillar_signals.get("cost", [])
        include_cost = False
        # Tighten: require at least 3 distinct non-generic terms OR (2 terms AND 3 sentences) for generic e-commerce marketing style docs.
        if (len(distinct_non_generic) >= 3 and distinct_cost_sentence_count >= 2) or (len(distinct_non_generic) >=2 and distinct_cost_sentence_count >=3):
            include_cost = True
        elif (len(pillar_cost_signals) >= 2 and len(distinct_non_generic) >= 3 and distinct_cost_sentence_count >=2):
            include_cost = True
        elif strategic_combo and distinct_high_signal_sentence_count >= 3:
            include_cost = True
        if include_cost:
            if pillar_cost_signals:
                cost_excerpt = "; ".join(pillar_cost_signals[:3])
                cross_cutting["cost_optimization"] = f"Cost signals: {cost_excerpt}. Further analysis can refine optimization levers."
            else:
                cross_cutting["cost_optimization"] = "Multiple concrete cost optimization indicators detected (governance + strategic, multi-sentence)."

        # --- Conditional Compliance/Governance Inclusion (tightened gating) ---
        compliance_keywords = ["azure policy", "blueprint", "compliance", "pci", "hipaa", "soc2", "soc 2", "iso", "nist", "governance", "audit", "auditing", "standards", "cis"]
        comp_hits = [k for k in compliance_keywords if k in raw_lower]
        frameworks = [f for f in comp_hits if f in ["pci", "hipaa", "soc2", "soc 2", "iso", "nist", "cis"]]
        has_policy = any("azure policy" in c for c in comp_hits)
        has_blueprint = any("blueprint" in c for c in comp_hits)
        has_governance = "governance" in raw_lower
        has_audit = any(k in raw_lower for k in ["audit", "auditing"])
        # Sentence evidence: require multiple sentences referencing governance/compliance aspects
        compliance_sentences = []
        for s in sentences:
            ls = s.lower()
            if any(k in ls for k in compliance_keywords):
                compliance_sentences.append(s.strip())
        if len(compliance_sentences) < 2:
            for line in content.splitlines():
                ll = line.lower().strip()
                if any(k in ll for k in compliance_keywords):
                    if line.strip() not in compliance_sentences:
                        compliance_sentences.append(line.strip())
        distinct_compliance_sentence_count = _distinct(compliance_sentences)
        include_compliance = False
        # Tighten: frameworks now require >=3 compliance sentences OR >=3 distinct frameworks.
        if ((len(frameworks) >= 2 and distinct_compliance_sentence_count >= 3) or len(frameworks) >=3):
            include_compliance = True
        elif ((has_policy or has_blueprint) and frameworks and (has_governance or has_audit) and distinct_compliance_sentence_count >= 3):
            include_compliance = True
        if include_compliance:
            items = []
            if has_policy:
                items.append("Azure Policy usage indicated")
            if has_blueprint:
                items.append("Blueprint references present")
            if frameworks:
                items.append("Frameworks mentioned: " + ", ".join(sorted(set(frameworks))))
            if has_governance:
                items.append("Governance emphasis noted")
            if has_audit:
                items.append("Audit considerations referenced")
            cross_cutting["compliance_governance"] = "; ".join(items) + "." if items else "Compliance indicators detected; multi-sentence evidence scope limited."

        # Deployment Summary (table + automation notes)
        deploy_parts: List[str] = []
        deploy_parts.append("### Deployment Overview\n\n")
        deploy_parts.append("| Component Category | Azure Services | Purpose |\n")
        deploy_parts.append("|--------------------|----------------|---------|\n")
        if by_category:
            for cat in sorted(by_category.keys()):
                services = ", ".join(sorted(set(by_category[cat]))[:4])
                purpose_map = {
                    "compute": "Application execution",
                    "storage": "Data persistence",
                    "networking": "Connectivity & routing",
                    "security": "Identity & protection",
                    "monitoring": "Telemetry & diagnostics",
                    "integration": "Messaging & workflows"
                }
                purpose = purpose_map.get(cat, "Workload capability")
                deploy_parts.append(f"| {cat.title()} | {services} | {purpose} |\n")
        else:
            deploy_parts.append("| (None) | (No services) | No explicit deployment details |\n")
        deploy_parts.append("\n")
        auto_notes: List[str] = []
        if any(k in raw_lower for k in ["terraform", "bicep", "arm template", "iac", "infrastructure as code"]):
            auto_notes.append("Infrastructure as Code referenced")
        if any(k in raw_lower for k in ["ci/cd", "pipeline", "devops"]):
            auto_notes.append("CI/CD pipeline integration indicated")
        if any(k in raw_lower for k in ["git", "repository", "source control"]):
            auto_notes.append("Source control versioning noted")
        if any(k in raw_lower for k in ["azure policy", "governance"]):
            auto_notes.append("Governance/policy mechanisms referenced")
        if auto_notes:
            deploy_parts.append("; ".join(auto_notes) + ".")
        deployment_summary = "".join(deploy_parts)

        # Evidence Sources
        evidence_sources = self._build_evidence_sources(content, components, pillar_signals, patterns)

        # Pillar evidence for frontend display
        pillar_evidence = {}
        for pillar in ["reliability", "security", "cost", "operational", "performance"]:
            excerpts = pillar_signals.get(pillar, [])
            if excerpts:
                pillar_evidence[pillar] = {
                    "count": len(excerpts),
                    "excerpts": [e.strip() for e in excerpts[:3]]
                }

        return {
            "executive_summary": executive_summary,
            "architecture_overview": architecture_overview,  # rich overview
            "cross_cutting_concerns": cross_cutting,
            "deployment_summary": deployment_summary,
            "evidence_sources": evidence_sources,
            "pillar_evidence": pillar_evidence
        }
    
    def _compose_structured_diagram_report(
        self,
        extracted_text: str,
        summary: str,
        filename: str,
        size: int,
        vision_summary: str | None = None
    ) -> Dict[str, any]:
        """Compose structured report for architecture diagram."""
        combined = (extracted_text + "\n" + summary).lower()
        patterns = self._detect_diagram_patterns(extracted_text + "\n" + summary)
        
        # Comprehensive Executive Summary - prioritize vision analysis when available
        exec_summary_parts = []
        
        if vision_summary and len(vision_summary) > 50:
            # Use vision API analysis as primary source
            exec_summary_parts.append(f"Architecture diagram analysis ('{filename}'): {vision_summary[:1200]}")
            if len(vision_summary) > 1200:
                exec_summary_parts.append("...")
            exec_summary = "".join(exec_summary_parts)
        else:
            # Fallback to heuristic analysis
            exec_summary_parts.append(f"This Azure architecture diagram ('{filename}') depicts a ")
            
            # Identify primary pattern
            if any('multi-region' in p.lower() for p in patterns):
                exec_summary_parts.append("highly available, multi-region deployment pattern designed for reliability, scalability, and security. ")
            elif any('high availability' in p.lower() for p in patterns):
                exec_summary_parts.append("highly available deployment pattern focused on resilience and uptime. ")
            else:
                exec_summary_parts.append("cloud architecture designed for scalability and operational efficiency. ")
            
            # User/workload context
            if 'front door' in combined or 'gateway' in combined:
                exec_summary_parts.append("It serves distributed users through a globally distributed setup with edge routing and security. ")
            
            # Key infrastructure highlights
            key_services = []
            if 'front door' in combined and 'waf' in combined:
                key_services.append("Azure Front Door with WAF provides global load balancing, routing, and edge security")
            if 'region' in combined and combined.count('region') > 1:
                key_services.append("multiple Azure regions host redundant environments ensuring business continuity")
            if 'sql' in combined and ('replica' in combined or 'geo' in combined):
                key_services.append("geo-replicated SQL Database maintains data consistency across regions")
            if 'redis' in combined or 'cache' in combined:
                key_services.append("distributed caching layer optimizes performance and reduces latency")
            
            if key_services:
                exec_summary_parts.append(". ".join(key_services[:3]) + ". ")
            
            # Resilience statement
            if 'region' in combined and combined.count('region') > 1:
                exec_summary_parts.append("Each region hosts a complete instance of the application stack to maintain redundancy and resilience, ensuring minimal downtime during regional failures.")
            
            exec_summary = "".join(exec_summary_parts)
        
        # Detailed Architecture Overview with Regional Breakdown
        arch_overview_parts = []
        
        # Section 1: Regional Distribution
        if 'region' in combined:
            arch_overview_parts.append("### 1. Regional Distribution\n\n")
            region_count = 2 if combined.count('region') > 1 else 1
            if region_count > 1:
                arch_overview_parts.append(f"Two Azure regions host mirrored environments. Both contain:\n\n")
            else:
                arch_overview_parts.append("Architecture deployed in a single Azure region with the following components:\n\n")
            
            # Extract components
            components = []
            if 'app service' in combined or 'web app' in combined:
                components.append("• **Web Apps (Front End and API)**: Implemented using Azure App Service, separated by subnets for frontend and API layers.")
            if 'storage' in combined:
                components.append("• **Azure Storage**: Handles application assets and persistent data.")
            if 'sql' in combined:
                geo_note = " with geo-replication between regions for disaster recovery" if 'geo' in combined or 'replica' in combined else ""
                components.append(f"• **Azure SQL Database**: Acts as the primary data store{geo_note}.")
            if 'redis' in combined or 'cache' in combined:
                components.append("• **Azure Cache for Redis**: Provides high-performance caching for frequently accessed data.")
            if 'insight' in combined or 'monitor' in combined:
                components.append("• **Application Insights**: Enables performance monitoring and telemetry.")
            if 'key vault' in combined or 'app configuration' in combined:
                components.append("• **App Configuration & Key Vault**: Centralize configuration management and secrets handling.")
            
            arch_overview_parts.append("\n".join(components))
            arch_overview_parts.append("\n\n")
        
        # Section 2: Networking
        arch_overview_parts.append("### 2. Networking\n\n")
        if 'virtual network' in combined or 'vnet' in combined:
            arch_overview_parts.append("Each region deploys:\n\n")
            arch_overview_parts.append("• A Virtual Network (VNet) segmented into:\n")
            if 'subnet' in combined:
                arch_overview_parts.append("  - Front-End App Service Subnet\n")
                arch_overview_parts.append("  - API App Service Subnet\n")
            if 'private endpoint' in combined:
                arch_overview_parts.append("  - Private Endpoint Subnet\n")
                arch_overview_parts.append("\n• Private Endpoints ensure secure communication between Azure services without exposure to the public internet.\n")
            if 'dns' in combined:
                arch_overview_parts.append("• DNS Zones maintain internal name resolution consistency across services.\n")
        else:
            arch_overview_parts.append("Network topology details not explicitly documented in diagram.\n")
        arch_overview_parts.append("\n")
        
        # Section 3: Global Connectivity
        if 'front door' in combined or 'gateway' in combined:
            arch_overview_parts.append("### 3. Global Connectivity\n\n")
            arch_overview_parts.append("Azure Front Door acts as the global entry point, offering:\n\n")
            arch_overview_parts.append("• Intelligent traffic routing between regions\n")
            arch_overview_parts.append("• SSL offloading and caching\n")
            if 'waf' in combined:
                arch_overview_parts.append("• WAF protection against OWASP vulnerabilities\n")
            arch_overview_parts.append("\n")
        
        if 'entra' in combined or 'azure ad' in combined or 'identity' in combined:
            arch_overview_parts.append("Microsoft Entra ID (Azure AD) handles user authentication and identity management.\n\n")
        
        # Section 4: Data and Replication
        if 'sql' in combined and ('replica' in combined or 'geo' in combined):
            arch_overview_parts.append("### 4. Data and Replication\n\n")
            arch_overview_parts.append("The SQL Database in each region replicates asynchronously to the counterpart, maintaining data consistency and failover capability. ")
            arch_overview_parts.append("The design ensures that even in regional failure scenarios, data remains accessible and consistent.\n\n")
        
        # Append detected patterns
        arch_overview_parts.append("### Detected Architecture Patterns\n\n")
        if patterns:
            arch_overview_parts.append("\n".join(f"• {p}" for p in patterns))
        else:
            arch_overview_parts.append("• (No explicit patterns detected from diagram metadata)")
        
        arch_overview = "".join(arch_overview_parts)
        
        # Enhanced Cross-Cutting Concerns (already handled by _infer_diagram_concern)
        cross_cutting = {
            "security": self._infer_diagram_concern("security", extracted_text, summary),
            "scalability": self._infer_diagram_concern("scalability", extracted_text, summary),
            "availability": self._infer_diagram_concern("availability", extracted_text, summary),
            "observability": self._infer_diagram_concern("observability", extracted_text, summary)
        }
        
        # Comprehensive Deployment Summary with Component Table
        deployment_parts = []
        deployment_parts.append("### Deployment Overview\n\n")
        
        # Build component table
        deployment_parts.append("| Component | Service | Purpose |\n")
        deployment_parts.append("|-----------|---------|---------|\n")
        
        if 'front door' in combined:
            waf_note = " + WAF" if 'waf' in combined else ""
            deployment_parts.append(f"| Global Entry | Azure Front Door{waf_note} | Global routing, security, SSL termination |\n")
        if 'entra' in combined or 'azure ad' in combined:
            deployment_parts.append("| Identity | Microsoft Entra ID | Centralized authentication and access control |\n")
        if 'app service' in combined or 'web app' in combined:
            deployment_parts.append("| Application Layer | Azure App Service (Web + API) | Web frontend and backend APIs |\n")
        if 'sql' in combined:
            geo_note = " with geo-replication" if 'geo' in combined or 'replica' in combined else ""
            deployment_parts.append(f"| Data Layer | Azure SQL Database | Persistent data store{geo_note} |\n")
        if 'redis' in combined or 'cache' in combined:
            deployment_parts.append("| Caching | Azure Cache for Redis | High-speed data caching and session storage |\n")
        if 'key vault' in combined or 'app configuration' in combined:
            deployment_parts.append("| Configuration | App Configuration & Key Vault | Central config management and secret storage |\n")
        if 'insight' in combined or 'monitor' in combined:
            deployment_parts.append("| Monitoring | Application Insights | Telemetry, diagnostics, and performance monitoring |\n")
        if 'virtual network' in combined or 'vnet' in combined or 'private endpoint' in combined:
            deployment_parts.append("| Networking | VNet, Subnets, DNS, Private Endpoints | Secure, isolated network topology |\n")
        
        deployment_parts.append("\n")
        
        # Deployment automation note
        if 'bicep' in combined or 'terraform' in combined or 'arm' in combined or 'iac' in combined:
            deployment_parts.append("Deployment is automated via Infrastructure as Code (IaC) templates, enabling consistent provisioning across regions. ")
        else:
            deployment_parts.append("Deployment is typically automated via Azure Resource Manager (ARM) templates or Bicep, enabling consistent provisioning. ")
        
        if 'pipeline' in combined or 'devops' in combined or 'cicd' in combined:
            deployment_parts.append("The environment supports continuous integration and continuous deployment (CI/CD) pipelines integrated with source control, ensuring consistent versioning and configuration across deployments.")
        else:
            deployment_parts.append("CI/CD integration recommended for consistent versioning and automated deployment workflows.")
        
        deployment_summary = "".join(deployment_parts)
        
        # Pillar evidence synthesis (diagram-specific heuristics)
        # We derive lightweight excerpts signaling pillar relevance based on detected services, patterns, and cross-cutting text.
        pillar_evidence: Dict[str, Dict[str, Any]] = {}
        def _add(pillar: str, text: str):
            entry = pillar_evidence.setdefault(pillar, {"excerpts": []})
            if text not in entry["excerpts"] and len(entry["excerpts"]) < 5:
                entry["excerpts"].append(text)

        # Reliability indicators
        if 'multi-region' in combined or combined.count('region') > 1:
            _add("reliability", "Multi-region redundancy depicted")
        if 'replica' in combined or 'geo' in combined:
            _add("reliability", "Geo-replication for data resilience")
        if 'failover' in combined or 'front door' in combined:
            _add("reliability", "Global entry + routing suggests failover strategy")

        # Security indicators
        if 'waf' in combined:
            _add("security", "Web Application Firewall protection visible")
        if 'key vault' in combined:
            _add("security", "Key Vault integration for secrets management")
        if 'entra' in combined or 'azure ad' in combined:
            _add("security", "Centralized identity via Microsoft Entra ID")

        # Operational indicators
        if 'insight' in combined or 'monitor' in combined:
            _add("operational", "Telemetry via Application Insights / monitoring components")
        if 'pipeline' in combined or 'devops' in combined or 'cicd' in combined:
            _add("operational", "CI/CD workflow references support operational excellence")
        if 'bicep' in combined or 'terraform' in combined or 'iac' in combined or 'arm' in combined:
            _add("operational", "Infrastructure as Code automation noted")

        # Performance indicators
        if 'redis' in combined or 'cache' in combined:
            _add("performance", "Caching layer for low-latency performance")
        if 'front door' in combined:
            _add("performance", "Global edge routing optimizes request latency")

        # Cost indicators (sparser – infer from absence/presence of redundancy optimizations)
        if 'redis' in combined and 'cache' in combined:
            _add("cost", "Caching can reduce backend compute cost")
        if 'automation' in combined or 'iac' in combined:
            _add("cost", "Automation enables consistent, optimized provisioning")

        # Finalize counts
        for pillar, data in pillar_evidence.items():
            data["count"] = len(data["excerpts"])
            data["inferred"] = True  # Mark as inferred from diagram heuristics

        return {
            "executive_summary": exec_summary,
            "architecture_overview": arch_overview,
            "cross_cutting_concerns": cross_cutting,
            "deployment_summary": deployment_summary,
            "pillar_evidence": pillar_evidence
        }
    
    def _compose_structured_case_concerns_report(
        self,
        filename: str,
        cases: List[Dict],
        themes: Dict[str, List[Dict]],
        risks: List[Dict],
        root_cause_analysis: Dict[str, any]
    ) -> Dict[str, any]:
        """Compose concerns report for support cases with root cause/resolution analysis."""
        # Executive Summary (qualitative – no numeric emphasis)
        exec_summary = (
            f"Support case review of '{filename}' surfaces recurring reliability, configuration, and observability friction. "
            "Patterns suggest systemic issues requiring stabilization and proactive mitigation rather than isolated one-off fixes. "
        )
        if any(r.get('severity') == 'high' for r in risks):
            exec_summary += "Multiple high-severity motifs appear across distinct incidents, indicating compound failure modes that merit root cause consolidation. "
        exec_summary += "Focus should shift toward disciplined change management, clearer ownership, and earlier detection through telemetry."

        # Qualitative Support Case Concerns (remove counts / numeric framing)
        concerns_parts: List[str] = []
        concerns_parts.append("Qualitative Case Themes:\n")
        recurring = root_cause_analysis.get("recurring_failure_patterns")
        if recurring and root_cause_analysis.get("top_root_causes"):
            # Extract only pattern names (omit counts)
            pattern_names = [p.replace('_', ' ').title() for p, _ in root_cause_analysis["top_root_causes"][:5]]
            concerns_parts.append(
                "Recurring failure motifs: " + ", ".join(pattern_names) + 
                " (indicative of systemic design or operational gaps).\n"
            )
        else:
            concerns_parts.append("No dominant recurring pattern emerged; failures appear more context-specific.\n")

        # Resolution quality (qualitative only)
        rq = root_cause_analysis.get('resolution_quality', '')
        if isinstance(rq, str) and rq:
            concerns_parts.append(
                f"Resolution posture: {rq.title()} – improve structured post-incident reviews to capture lessons learned and preventive actions.\n"
            )
        if root_cause_analysis.get('unresolved_gaps', 0) > 0:
            concerns_parts.append("Some gaps remain unresolved and require coordinated follow-up and ownership assignment.\n")

        concerns_parts.append(
            "Emphasis: shift from reactive triage toward preemptive detection (health probes, synthetic monitoring) and guardrails on configuration/change flows.\n"
        )
        concerns = "".join(concerns_parts)

        # Cross-Cutting Concerns (risk-based; unchanged logic)
        cross_cutting = {
            "security": self._case_dimensional_concern("security", themes, risks),
            "scalability": self._case_dimensional_concern("scalability", themes, risks),
            "availability": self._case_dimensional_concern("availability", themes, risks),
            "observability": self._case_dimensional_concern("observability", themes, risks)
        }
        
        # Deployment Summary (qualitative; remove numeric references)
        deployment_summary = (
            "Operational history reflects environment friction during configuration changes and incident response. "
            "Prioritize consistent change automation, clearer rollback strategies, and enriched telemetry over ad-hoc manual remediation."
        )

        # Pillar evidence extraction (case-specific): map themes + root causes to pillars for contextual excerpts
        pillar_map = {
            "reliability": ["availability_issue"],
            "security": ["authentication_failure", "security"],
            "performance": ["performance_timeout", "latency"],
            "operational": ["configuration_error", "configuration"],
            "cost": ["cost"]
        }
        # Collect sentences/excerpts from root causes and resolutions
        rc_texts = []
        for case in cases:
            rc = case.get('msdfm_rootcausedescription', '') or case.get('root_cause', '')
            res = case.get('msdfm_resolution', '') or case.get('resolution', '')
            if rc and isinstance(rc, str):
                rc_texts.append(rc.strip())
            if res and isinstance(res, str):
                rc_texts.append(res.strip())
        # Simple sentence segmentation
        import re as _re
        sentences: List[str] = []
        for block in rc_texts:
            parts = _re.split(r"(?<=[.!?])\s+", block.strip())
            for p in parts:
                if p.strip():
                    sentences.append(p.strip())
        pillar_evidence: Dict[str, Dict[str, any]] = {}
        for pillar, keys in pillar_map.items():
            # Keys correspond to pattern names or theme names; gather sentences referencing keywords
            kws = [k.replace('_', ' ') for k in keys]
            matched: List[str] = []
            seen = set()
            for sent in sentences:
                low = sent.lower()
                if any(k in low for k in kws):
                    norm = low[:140]
                    if norm not in seen:
                        seen.add(norm)
                        matched.append(sent[:240])
                if len(matched) >= 3:
                    break
            if matched:
                pillar_evidence[pillar] = {"count": len(matched), "excerpts": matched}

        # Build sample arrays (distinct, truncated) for upstream UI usage
        root_cause_samples: List[str] = []
        resolution_samples: List[str] = []
        seen_rc = set()
        seen_res = set()
        for case in cases:
            rc = case.get('msdfm_rootcausedescription', '') or case.get('root_cause', '')
            res = case.get('msdfm_resolution', '') or case.get('resolution', '')
            if rc and isinstance(rc, str):
                norm = rc.strip()[:240]
                sig = norm[:160]
                if len(norm) > 20 and sig not in seen_rc:
                    seen_rc.add(sig)
                    root_cause_samples.append(norm)
            if res and isinstance(res, str):
                normr = res.strip()[:240]
                sigr = normr[:160]
                if len(normr) > 20 and sigr not in seen_res:
                    seen_res.add(sigr)
                    resolution_samples.append(normr)
            if len(root_cause_samples) >= 8 and len(resolution_samples) >= 8:
                break

        recurring_failure_patterns = list(root_cause_analysis.get("recurring_failure_patterns", {}).items())
        
        return {
            "executive_summary": exec_summary,
            "support_case_concerns": concerns,  # Specialized section for CSV
            "cross_cutting_concerns": cross_cutting,
            "deployment_summary": deployment_summary,
            "pillar_evidence": pillar_evidence,
            "root_cause_samples": root_cause_samples,
            "resolution_samples": resolution_samples,
            "recurring_failure_patterns": recurring_failure_patterns
        }
    
    def _dimensional_concern_summary(self, dimension: str, signals: List[str], content: str) -> str:
        """Generate dimensional concern summary for architecture docs."""
        if not signals:
            return f"{dimension.title()}: Not explicitly addressed in documentation; requires validation."
        signal_summary = "; ".join(signals[:3])
        return f"{dimension.title()}: {signal_summary}. Further assessment recommended."

    def _build_evidence_sources(
        self,
        content: str,
        components: List[Dict[str, str]],
        pillar_signals: Dict[str, List[str]],
        patterns: List[str],
        max_excerpts: int = 3
    ) -> Dict[str, any]:
        """Build evidence sources map for pillars and services.

        Extracts up to `max_excerpts` sentence-boundary excerpts for each pillar and service.
        Ensures strictly source-based evidence; dedupes identical excerpts.
        """
        text = content
        lower = text.lower()

        def _sentences(src: str) -> List[str]:
            # Simple sentence split; keep periods/exclamations/questions.
            parts = re.split(r"(?<=[.!?])\s+", src.strip())
            # Trim excessively long parts
            return [p.strip() for p in parts if p.strip()]

        sentences = _sentences(text)
        # Index sentences for lookup
        indexed: List[Tuple[int, str]] = list(enumerate(sentences))

        # Helper to collect excerpts containing a keyword (case-insensitive)
        def collect_excerpts(keywords: List[str]) -> List[str]:
            found: List[str] = []
            seen = set()
            for _, sent in indexed:
                low_sent = sent.lower()
                if any(k in low_sent for k in keywords):
                    norm = low_sent[:140]
                    if norm not in seen:
                        seen.add(norm)
                        found.append(sent[:240])  # Cap length
                if len(found) >= max_excerpts:
                    break
            return found

        # Pillar evidence
        pillar_evidence: Dict[str, Dict[str, any]] = {}
        for pillar, signals in pillar_signals.items():
            if not signals:
                continue
            # Use signals themselves as keywords for excerpt matching
            kws = [s.lower()[:60] for s in signals[:max_excerpts]]
            excerpts = collect_excerpts(kws)
            pillar_evidence[pillar] = {
                "count": len(signals),
                "excerpts": excerpts
            }

        # Service evidence
        service_evidence: Dict[str, Dict[str, any]] = {}
        # Collate distinct services by longest token first to avoid substring overlap
        distinct: List[Tuple[str, str]] = []  # (service, category)
        seen_services = set()
        for comp in components:
            svc = comp.get("service", "").strip()
            cat = comp.get("category", "general")
            if svc and svc not in seen_services:
                seen_services.add(svc)
                distinct.append((svc, cat))
        # Sort by length desc to prefer longer matches
        distinct.sort(key=lambda x: len(x[0]), reverse=True)

        for svc, cat in distinct:
            svc_lower = svc.lower()
            occurrences = lower.count(svc_lower)
            if occurrences == 0:
                continue
            excerpts = collect_excerpts([svc_lower])
            service_evidence[svc] = {
                "category": cat,
                "occurrences": occurrences,
                "excerpts": excerpts
            }

        # Pattern excerpts (optional)
        pattern_evidence: Dict[str, List[str]] = {}
        for pattern in patterns:
            p_low = pattern.lower()
            ex = collect_excerpts([p_low])
            if ex:
                pattern_evidence[pattern] = ex

        return {
            "pillars": pillar_evidence,
            "services": service_evidence,
            "patterns": pattern_evidence
        }
    
    def _infer_diagram_concern(self, dimension: str, extracted_text: str, summary: str) -> str:
        """Infer dimensional concern from diagram text/summary with descriptive findings."""
        combined = (extracted_text + " " + summary).lower()
        
        findings = []
        
        if dimension == "security":
            if "waf" in combined or "firewall" in combined:
                findings.append("WAF/firewall layer detected for ingress protection")
            if "vault" in combined or "key vault" in combined:
                findings.append("Key Vault for secret management")
            if "entra" in combined or "azure ad" in combined or "identity" in combined:
                findings.append("Entra ID (Azure AD) for identity & access management")
            if "private endpoint" in combined or "private link" in combined:
                findings.append("Private endpoints for secure PaaS access")
            if not findings:
                return "No explicit security controls identified in diagram; validate defense-in-depth implementation."
            return "; ".join(findings) + ". Validate configuration and audit logs."
        
        elif dimension == "scalability":
            if "scale" in combined or "auto" in combined:
                findings.append("Auto-scaling configuration implied")
            if "load" in combined and "balanc" in combined:
                findings.append("Load balancing detected")
            if "redis" in combined or "cache" in combined:
                findings.append("Caching layer (Redis) for performance")
            if "cdn" in combined or "front door" in combined:
                findings.append("Global distribution via CDN/Front Door")
            if not findings:
                return "No explicit scalability mechanisms visible; assess elastic scale policies and capacity planning."
            return "; ".join(findings) + ". Validate scale limits and performance baselines."
        
        elif dimension == "availability":
            if "region" in combined and (combined.count("region") > 1 or "multi" in combined):
                findings.append("Multi-region deployment for geo-redundancy")
            if "replica" in combined or "replicat" in combined:
                findings.append("Data replication detected (SQL geo-replication)")
            if "zone" in combined:
                findings.append("Zone redundancy implied")
            if "failover" in combined:
                findings.append("Failover configuration present")
            if not findings:
                return "No explicit high-availability topology visible; assess SLA targets and failover strategy."
            return "; ".join(findings) + ". Validate RTO/RPO objectives and test DR procedures."
        
        elif dimension == "observability":
            if "insight" in combined or "application insights" in combined:
                findings.append("Application Insights for telemetry")
            if "monitor" in combined:
                findings.append("Azure Monitor integration")
            if "log" in combined:
                findings.append("Logging infrastructure detected")
            if "alert" in combined:
                findings.append("Alerting configured")
            if not findings:
                return "No explicit monitoring/observability tools visible; assess telemetry coverage and alert strategy."
            return "; ".join(findings) + ". Validate metrics collection and incident response runbooks."
        
        return "Assessment required; diagram does not provide sufficient detail for this dimension."
    
    def _case_dimensional_concern(self, dimension: str, themes: Dict, risks: List[Dict]) -> str:
        """Generate dimensional concern from support case themes/risks."""
        dimension_themes = {
            "security": ["authentication", "security"],
            "scalability": ["latency", "performance"],
            "availability": ["availability"],
            "observability": ["configuration"]
        }
        related = [t for t in dimension_themes.get(dimension, []) if t in themes]
        if related:
            issue_count = sum(len(themes[t]) for t in related)
            severity_match = next((r for r in risks if r["theme"] in related and r["severity"] == "high"), None)
            qualifier = "HIGH PRIORITY" if severity_match else "requires attention"
            return f"{dimension.title()}: {issue_count} historical incidents ({qualifier})."
        return f"{dimension.title()}: No significant incident patterns detected."

    def _detect_diagram_patterns(self, combined_text: str) -> List[str]:
        """Infer high-level architecture patterns from diagram textual signals."""
        text = combined_text.lower()
        patterns = []
        if 'front door' in text and ('waf' in text or 'firewall' in text):
            patterns.append('Global ingress with WAF (Azure Front Door)')
        if text.count('region') >= 2 or 'multi-region' in text or 'geo-replicat' in text:
            patterns.append('Multi-region high availability pattern')
        if 'redis' in text and ('cache' in text or 'performance' in text):
            patterns.append('Performance optimization via distributed caching (Redis)')
        if 'key vault' in text and ('secret' in text or 'identity' in text or 'entra' in text):
            patterns.append('Centralized secret & identity protection (Key Vault + Entra)')
        if 'virtual network' in text and 'private endpoint' in text:
            patterns.append('Private network isolation with secure service endpoints')
        if 'sql' in text and ('geo-replicat' in text or 'replica' in text):
            patterns.append('Data resiliency via geo-replicated SQL')
        if 'application insights' in text or 'monitor' in text or 'telemetry' in text:
            patterns.append('Integrated observability & telemetry (App Insights)')
        if 'app configuration' in text:
            patterns.append('Externalized configuration management')
        return patterns[:8]
    
    def _extract_key_insights(
        self,
        content: str,
        signals: Dict[str, List[str]]
    ) -> List[str]:
        """Extract top key insights from content."""
        insights = []
        
        for pillar, pillar_signals in signals.items():
            if pillar_signals:
                insights.append(f"{pillar.title()}: {len(pillar_signals)} relevant patterns detected")
        
        return insights[:5]
