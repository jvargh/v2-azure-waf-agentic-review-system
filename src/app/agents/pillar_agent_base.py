"""Shared abstractions for Azure Well-Architected pillar agents.

This module provides a light-weight base class that encapsulates the common
pattern implemented by the Reliability agent so that the remaining pillar agents
(Security, Cost Optimization, Operational Excellence, Performance Efficiency)
can remain concise while still offering consistent behaviour.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import warnings
import csv
from contextlib import suppress
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from src.app.tools.mcp_tools import MCPToolManager
from src.utils.env_utils import EnvironmentConfig, load_env_vars, validate_env_vars
from src.utils.scoring.scoring import compute_pillar_scores, summarize_scores

# Suppress aiohttp unclosed session warnings from Azure SDK
warnings.filterwarnings("ignore", message=".*Unclosed.*", category=ResourceWarning)

# Centralized logging initialization (delegated to logging_config)
try:
    from src.app.utils.logging_config import init_logging
    init_logging()
except Exception:
    # Fallback minimal configuration if centralized module unavailable
    _root = logging.getLogger()
    if not _root.handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

logger = logging.getLogger(__name__)
logger.debug("BasePillarAgent module loaded")

try:
    from agent_framework.azure import AzureOpenAIResponsesClient, AzureAIAgentClient
    from azure.identity import AzureCliCredential
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False

# OpenTelemetry imports for span enrichment
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None


@dataclass
class PillarAssessment:
    """Normalized assessment payload returned by pillar agents."""

    overall_score: int
    domain_scores: Dict[str, Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    mcp_references: List[Dict[str, str]]
    maturity: Dict[str, Any]
    architecture_text: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BasePillarAgent:
    """Reusable Azure Well-Architected pillar agent.

    Sub-classes only need to provide pillar metadata (code, prefix, domain titles)
    and the path to an instructions file that specifies the JSON contract expected
    from the LLM. All shared functionality—environment validation, MCP lookups,
    scoring pipeline integration, and markdown export—is handled here.
    """

    def __init__(
        self,
        *,
        pillar_code: str,
        pillar_prefix: str,
        domain_titles: Dict[str, str],
        instructions_filename: str,
        agent_name: str,
        pillar_display_name: Optional[str] = None,
        mcp_topic: Optional[str] = None,
        enable_mcp: bool = True,
    ) -> None:
        if not AGENT_FRAMEWORK_AVAILABLE:
            raise SystemExit(
                "Microsoft Agent Framework is required. Install the 'agent-framework' package "
                "to run Well-Architected pillar agents."
            )

        self.pillar_code = pillar_code
        self.pillar_prefix = pillar_prefix
        self.domain_titles = dict(domain_titles)
        self.instructions_filename = instructions_filename
        self.agent_name = agent_name
        self.pillar_display_name = pillar_display_name or pillar_code.replace("_", " ").title()
        self.mcp_topic = mcp_topic or pillar_code
        self.enable_mcp = enable_mcp

        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.prompts_dir = self.project_root / "app" / "prompts"

        self.agent = None
        self._client = None  # Store client for cleanup
        self._async_credential = None  # Store async credential for cleanup
        self._instructions_cache: Optional[str] = None
        self.mcp_manager = MCPToolManager() if enable_mcp else None

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------
    async def _get_or_create_agent(self, instructions: str, name: str, model: str = None) -> Any:
        """Get existing agent by name or create new one if it doesn't exist."""
        try:
            # Try to list agents and find existing one by name
            agents = self._client.list_agents()
            for agent in agents:
                if agent.name == name:
                    logger.info("Found existing agent '%s' with ID: %s", name, agent.id)
                    return self._client.get_agent(agent.id)
        except Exception as e:
            logger.debug("Could not list agents (may not be supported): %s", e)
        
        # If no existing agent found or listing not supported, create new one
        logger.info("Creating new agent '%s'", name)
        if model:
            return self._client.create_agent(instructions=instructions, name=name, model=model)
        else:
            return self._client.create_agent(instructions=instructions, name=name)

    async def _initialize_agent(self) -> None:
        """Initialize the hosted agent via Microsoft Agent Framework."""
        env_config, validation = self._load_and_validate_config()
        config_type = validation.get("configuration_type")
        instructions = await self._load_instructions()

        credential = AzureCliCredential()
        if config_type == "azure_ai_foundry":
            from azure.identity.aio import AzureCliCredential as AsyncAzureCliCredential

            self._async_credential = AsyncAzureCliCredential()
            self._client = AzureAIAgentClient(
                async_credential=self._async_credential,
                project_endpoint=env_config.azure_ai_project_endpoint,
            )
            try:
                await self._client.setup_azure_ai_observability()
                logger.info("Azure AI Foundry observability configured successfully")
            except Exception as obs_err:  # pragma: no cover - defensive
                logger.warning(
                    "Failed to configure Azure AI observability (tracing will not be available): %s. "
                    "Ensure Application Insights is connected to your AI Foundry project.",
                    obs_err
                )
            self.agent = await self._get_or_create_agent(
                instructions=instructions,
                name=self.agent_name,
                model=env_config.azure_ai_model_deployment_name,
            )
        elif config_type == "azure_openai":
            if getattr(env_config, "azure_openai_api_key", None):
                self._client = AzureOpenAIResponsesClient(
                    endpoint=env_config.azure_openai_endpoint,
                    deployment_name=env_config.azure_openai_deployment_name,
                    api_version=env_config.azure_openai_api_version,
                    api_key=env_config.azure_openai_api_key,
                )
            else:
                self._client = AzureOpenAIResponsesClient(
                    endpoint=env_config.azure_openai_endpoint,
                    deployment_name=env_config.azure_openai_deployment_name,
                    api_version=env_config.azure_openai_api_version,
                    credential=credential,
                )
            self.agent = await self._get_or_create_agent(
                instructions=instructions,
                name=self.agent_name,
            )
        else:
            raise ValueError(f"Unknown configuration type: {config_type}")

        logger.info("%s initialized (config: %s)", self.agent_name, config_type)

    def _load_and_validate_config(self) -> Tuple[EnvironmentConfig, Dict[str, Any]]:
        env_config = load_env_vars()
        validation = validate_env_vars(env_config, agent_type=self.pillar_code)
        if not validation.get("is_valid"):
            errors = "\n - ".join(validation.get("errors", []))
            raise ValueError(f"Invalid configuration for pillar '{self.pillar_code}':\n - {errors}")
        for warning in validation.get("warnings", []):
            logger.warning("%s", warning)
        return env_config, validation

    async def _load_instructions(self) -> str:
        if self._instructions_cache:
            return self._instructions_cache
        file_path = self.prompts_dir / self.instructions_filename
        if not file_path.exists():
            raise FileNotFoundError(f"Instructions file not found: {file_path}")
        content = file_path.read_text(encoding="utf-8").strip()
        self._instructions_cache = content
        return content

    # ------------------------------------------------------------------
    # Assessment pipeline
    # ------------------------------------------------------------------
    async def assess_architecture(self, architecture_content: str) -> PillarAssessment:
        if not self.agent:
            logger.debug("Agent instance missing; initializing %s", self.agent_name)
            await self._initialize_agent()

        logger.info(
            "Starting assessment run | pillar=%s | chars=%d",
            self.pillar_code,
            len(architecture_content or ""),
        )

        references: List[Dict[str, str]] = []
        if self.mcp_manager and self.enable_mcp:
            try:
                docs = await self.mcp_manager.get_service_documentation(self.pillar_code, self.mcp_topic)
                references = [{"title": d.get("title", ""), "url": d.get("url", "")} for d in docs[:3]]
                logger.info("Retrieved %d MCP documentation references", len(references))
                for idx, ref in enumerate(references):
                    logger.info("  Doc [%d]: %s - %s", idx + 1, ref.get("title", "")[:60], ref.get("url", ""))
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("MCP lookup failed for %s: %s", self.pillar_code, exc)

        prompt = self._render_prompt(architecture_content)
        logger.info(
            "Sending assessment prompt to agent | pillar=%s | prompt_length=%d | architecture_length=%d | references=%d",
            self.pillar_code,
            len(prompt),
            len(architecture_content),
            len(references)
        )
        logger.debug("Prompt preview (first 300 chars): %s", prompt[:300])
        
        # Log MCP reference URLs for tracing
        if references:
            logger.info("MCP documentation references being used:")
            for idx, ref in enumerate(references):
                logger.info("  [%d] %s", idx + 1, ref.get("url", ""))
        
        # Add custom span events with rich metadata
        if OTEL_AVAILABLE and trace:
            current_span = trace.get_current_span()
            if current_span and current_span.is_recording():
                # Add event with all context details
                event_attributes = {
                    "pillar.code": self.pillar_code,
                    "pillar.display_name": self.pillar_display_name,
                    "architecture.length": len(architecture_content),
                    "prompt.length": len(prompt),
                    "mcp.references.count": len(references),
                }
                if references:
                    event_attributes["mcp.reference.urls"] = "; ".join(r.get("url", "") for r in references)
                    event_attributes["mcp.reference.titles"] = "; ".join(r.get("title", "")[:50] for r in references)
                
                current_span.add_event(
                    name="assessment_context",
                    attributes=event_attributes
                )
        
        result = await self.agent.run(prompt)
        logger.debug("Raw agent response type=%s", type(result))
        text = getattr(result, "text", str(result))
        logger.info("Agent response received | output_length=%d", len(text))
        
        # Add response event to span
        if OTEL_AVAILABLE and trace:
            current_span = trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.add_event(
                    name="llm_response_received",
                    attributes={"response.length": len(text)}
                )
        
        with suppress(Exception):
            logger.debug("Response first 250 chars: %s", text[:250])
        assessment = self._parse_response(text, references, architecture_content)
        logger.info(
            "Assessment completed | pillar=%s | overall_score=%d | recommendations=%d",
            self.pillar_code,
            assessment.overall_score,
            len(assessment.recommendations),
        )
        
        # Add final assessment metrics as span event
        if OTEL_AVAILABLE and trace:
            current_span = trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.add_event(
                    name="assessment_completed",
                    attributes={
                        "overall_score": assessment.overall_score,
                        "recommendations.count": len(assessment.recommendations),
                        "maturity.percent": float(assessment.maturity.get("overall_maturity_percent", 0)),
                    }
                )
        
        return assessment

    # NEW: Optional pathway including Azure Support Cases CSV context
    async def assess_architecture_with_cases(self, architecture_content: str, support_cases_path: Optional[Path] = None) -> PillarAssessment:
        """Assess architecture augmented with Azure support cases context.

        Args:
            architecture_content: Primary architecture/workload description text.
            support_cases_path: Path to a CSV file containing Azure support cases with
                columns: title, msdfm_productname, msdfm_customerstatement, msdfm_resolution.
        Returns:
            PillarAssessment including recommendations factoring in case learnings.
        """
        combined = architecture_content
        if support_cases_path:
            summary = self._summarize_support_cases(support_cases_path)
            if summary:
                combined += "\n\n### Historical Azure Support Cases (Context)\n" + summary
                logger.info(
                    "Support cases merged into architecture content | file=%s | chars_added=%d",
                    support_cases_path,
                    len(summary),
                )
            else:
                logger.warning("Support cases summary empty or failed to parse; continuing without it")
        return await self.assess_architecture(combined)

    def _render_prompt(self, architecture_content: str) -> str:
        return (
            "Evaluate the following Azure workload strictly against the Azure Well-Architected "
            f"{self.pillar_display_name} pillar. Respond with the JSON specified in your system instructions.\n\n"
            "Architecture input:\n"
            f"{architecture_content}"
        )

    # ------------------------------------------------------------------
    # Support cases parsing
    # ------------------------------------------------------------------
    def _summarize_support_cases(self, csv_path: Path, *, max_cases: int = 25) -> str:
        """Create a textual summary of Azure support cases for prompt enrichment.

        Each case becomes a bullet point with product, condensed customer statement and
        resolution outcome. Long fields are truncated for prompt efficiency.

        Args:
            csv_path: Path to CSV containing required columns.
            max_cases: Maximum number of cases to include to avoid prompt bloat.
        Returns:
            Markdown formatted bullet list or empty string if parsing fails.
        """
        if not csv_path.exists():
            logger.warning("Support cases file not found: %s", csv_path)
            return ""
        try:
            lines: List[str] = []
            with csv_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                required = {"title", "msdfm_productname", "msdfm_customerstatement", "msdfm_resolution"}
                if not required.issubset(set(reader.fieldnames or [])):
                    logger.warning(
                        "Support cases CSV missing required columns. Found=%s Required=%s",
                        reader.fieldnames,
                        sorted(list(required)),
                    )
                    return ""
                for i, row in enumerate(reader):
                    if i >= max_cases:
                        break
                    title = (row.get("title") or "").strip()
                    product = (row.get("msdfm_productname") or "").strip()
                    statement = (row.get("msdfm_customerstatement") or "").strip()
                    resolution = (row.get("msdfm_resolution") or "").strip()
                    # Truncate overly long fields for prompt efficiency
                    def _truncate(text: str, limit: int = 220) -> str:
                        return (text[: limit - 3] + "...") if len(text) > limit else text
                    statement = _truncate(statement)
                    resolution = _truncate(resolution)
                    bullet = (
                        f"- Case: {title or 'N/A'} | Product: {product or 'N/A'}\n"
                        f"  Customer: {statement or '—'}\n"
                        f"  Resolution: {resolution or '—'}"
                    )
                    lines.append(bullet)
            return "\n".join(lines)
        except Exception as exc:  # pragma: no cover - robust parsing
            logger.warning("Failed to parse support cases CSV %s: %s", csv_path, exc)
            return ""

    # ------------------------------------------------------------------
    # Response parsing & normalization
    # ------------------------------------------------------------------
    def _parse_response(
        self,
        response_text: str,
        mcp_references: List[Dict[str, str]],
        architecture_content: str,
    ) -> PillarAssessment:
        # Optionally remove legacy raw sections if disabled
        architecture_filtered = self._filter_legacy_sections(architecture_content)
        payload = self._extract_json(response_text)
        logger.debug("Parsed JSON keys: %s", list(payload.keys())[:10])
        domain_scores = self._normalize_domain_scores(payload.get("domain_scores", {}))
        recommendations = self._normalize_recommendations(payload.get("recommendations", []))
        overall_score = int(payload.get("overall_score", 0))

        # Multi-section equal weighting maturity computation
        sections = self._extract_weighted_sections(architecture_filtered)
        maturity_summary = self._compute_multi_section_maturity(sections) if sections else summarize_scores(
            compute_pillar_scores(architecture_filtered, pillar=self.pillar_code)
        )

        return PillarAssessment(
            overall_score=overall_score,
            domain_scores=domain_scores,
            recommendations=recommendations,
            mcp_references=mcp_references,
            maturity=maturity_summary,
            architecture_text=architecture_filtered,
        )

    def _extract_json(self, text: str) -> Dict[str, Any]:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end <= start:
            raise ValueError("Agent response did not include a JSON object")
        return json.loads(text[start:end])

    def _normalize_domain_scores(self, raw_scores: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        normalized: Dict[str, Dict[str, Any]] = {}
        for code, title in self.domain_titles.items():
            raw = raw_scores.get(code)
            score_value: int
            entry_title = title
            if isinstance(raw, dict):
                score_value = self._safe_int(raw.get("score", 0))
                entry_title = raw.get("title", title)
            else:
                score_value = self._safe_int(raw)
            normalized[code] = {"score": score_value, "title": entry_title}
        return normalized

    def _normalize_recommendations(self, recs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for rec in recs or []:
            if not isinstance(rec, dict):
                continue
            severity = self._derive_severity(rec)
            rec_copy = dict(rec)
            rec_copy.setdefault("severity", severity)
            normalized.append(rec_copy)
        return normalized

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _derive_severity(rec: Dict[str, Any]) -> int:
        for key in ("severity", "priority", "execution_priority"):
            val = rec.get(key)
            try:
                if val is not None:
                    return int(val)
            except (TypeError, ValueError):
                continue
        impact = rec.get("impact_score")
        try:
            impact_int = int(impact) if impact is not None else None
        except (TypeError, ValueError):
            impact_int = None
        if impact_int is None:
            return 5
        if impact_int >= 9:
            return 1
        if impact_int >= 7:
            return 2
        if impact_int >= 5:
            return 3
        if impact_int >= 3:
            return 4
        return 5

    # ------------------------------------------------------------------
    # Markdown helpers
    # ------------------------------------------------------------------
    def build_results_markdown(self, assessment: PillarAssessment) -> str:
        maturity = assessment.maturity
        domain_lines = [
            "| Code | Title | Score |",
            "|------|-------|-------|",
        ]
        for code, entry in assessment.domain_scores.items():
            domain_lines.append(f"| {code} | {entry.get('title', '')} | {entry.get('score', 0)} |")

        recommendation_lines = [
            "| Title | Severity | Priority | Impact | Codes |",
            "|-------|----------|----------|--------|-------|",
        ]
        for rec in assessment.recommendations:
            recommendation_lines.append(
                "| {title} | {sev} | {priority} | {impact} | {codes} |".format(
                    title=rec.get("title", ""),
                    sev=rec.get("severity", ""),
                    priority=rec.get("priority", ""),
                    impact=rec.get("impact_score", ""),
                    codes=", ".join(rec.get("pillar_codes") or rec.get("re_codes") or [])
                    if isinstance(rec.get("pillar_codes") or rec.get("re_codes"), list)
                    else rec.get("pillar_codes")
                    or rec.get("re_codes")
                    or "-",
                )
            )

        references_lines = [
            "| Title | URL |",
            "|-------|-----|",
        ]
        for ref in assessment.mcp_references:
            references_lines.append(f"| {ref.get('title', '')} | {ref.get('url', '')} |")

        practice_lines = [
            "| Code | Score (0-5) | Weight | Coverage | Matched Signals |",
            "|------|---------------|--------|----------|------------------|",
        ]
        for practice in maturity.get("practice_scores", []):
            practice_lines.append(
                "| {code} | {score} | {weight} | {coverage} | {signals} |".format(
                    code=practice.get("code"),
                    score=practice.get("score"),
                    weight=practice.get("weight"),
                    coverage=practice.get("coverage"),
                    signals=", ".join(practice.get("matched_signals", [])) or "-",
                )
            )

        lines = [
            f"# {self.pillar_display_name} Assessment Results",
            "",
            f"Generated: {assessment.timestamp}",
            "",
            f"Overall LLM Score: **{assessment.overall_score}** / 100",
            f"Deterministic Maturity: **{maturity.get('overall_maturity_percent')}%**",
            "",
            "## Domain Scores",
            *domain_lines,
            "",
            "## Recommendations",
            *recommendation_lines,
            "",
            "## MCP References",
            *references_lines,
            "",
            "## Deterministic Practice Scores",
            *practice_lines,
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Equal weighting helpers & legacy filtering
    # ------------------------------------------------------------------
    def _filter_legacy_sections(self, text: str) -> str:
        """Remove legacy raw analysis blocks when global toggle is off.
        Controlled by env var ENABLE_LEGACY_SECTIONS (default: off).
        """
        if os.getenv("ENABLE_LEGACY_SECTIONS", "false").lower() in ("1", "true", "yes"):
            return text
        filtered_lines: List[str] = []
        skip = False
        for line in text.splitlines():
            # Detect start of legacy block heuristically
            if "Raw LLM Analysis" in line or "RAW LLM ANALYSIS" in line:
                skip = True
            if skip:
                # End legacy block if blank line encountered after start
                if not line.strip():
                    skip = False
                continue
            filtered_lines.append(line)
        return "\n".join(filtered_lines)

    def _extract_weighted_sections(self, corpus_text: str) -> List[str]:
        """Extract known corpus sections for equal-weight scoring."""
        markers = [
            "=== ARCHITECTURE NARRATIVE ===",
            "=== VISUAL TOPOLOGY INSIGHTS ===",
            "=== OPERATIONAL REALITY (SUPPORT CASES) ===",
            "=== CONSOLIDATED PILLAR EVIDENCE ===",
        ]
        sections: List[str] = []
        current = []
        active = None
        for line in corpus_text.splitlines():
            if any(line.startswith(m) for m in markers):
                if active and current:
                    sections.append("\n".join(current).strip())
                active = line
                current = []
            else:
                if active is not None:
                    current.append(line)
        if active and current:
            sections.append("\n".join(current).strip())
        # Fallback: if no markers found treat whole text as one section
        return [s for s in sections if s] or [corpus_text]

    def _compute_multi_section_maturity(self, sections: List[str]) -> Dict[str, Any]:
        """Compute aggregated maturity with equal weight across sections."""
        from collections import defaultdict
        practice_acc: Dict[str, Dict[str, Any]] = {}
        overall_percents: List[float] = []
        gap_matched: List[Dict[str, Any]] = []
        gap_unmatched: List[Dict[str, Any]] = []
        all_recommendations: List[Dict[str, Any]] = []
        for section in sections:
            scores = compute_pillar_scores(section, pillar=self.pillar_code)
            summary = summarize_scores(scores)
            overall_percents.append(summary.get("overall_maturity_percent", 0.0))
            # Aggregate practices
            for p in summary.get("practice_scores", []):
                code = p.get("code")
                if not code:
                    continue
                entry = practice_acc.setdefault(code, {
                    "code": code,
                    "scores": [],
                    "weight": p.get("weight", 1.0),
                    "matched_signals": set(),
                    "coverage_values": [],
                    "mode": p.get("mode"),
                })
                entry["scores"].append(p.get("score", 0))
                entry["matched_signals"].update(p.get("matched_signals", []))
                entry["coverage_values"].append(p.get("coverage", 0.0))
            # Aggregate gaps
            for g in summary.get("gaps", []):
                if g.get("matched"):
                    gap_matched.append(g)
                else:
                    gap_unmatched.append(g)
            # Recommendations (not deterministic but keep for potential weighting diagnostics)
            all_recommendations.extend(summary.get("recommendations", []))
        # Build merged practice list
        merged_practices = []
        for code, data in practice_acc.items():
            avg_score = round(sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0, 2)
            avg_coverage = round(sum(data["coverage_values"]) / len(data["coverage_values"]) if data["coverage_values"] else 0, 3)
            merged_practices.append({
                "code": code,
                "score": avg_score,
                "weight": data["weight"],
                "matched_signals": sorted(list(data["matched_signals"]))[:20],
                "coverage": avg_coverage,
                "mode": data["mode"],
            })
        overall_maturity_percent = round(sum(overall_percents) / len(overall_percents), 2) if overall_percents else 0.0
        return {
            "pillar": self.pillar_display_name,
            "overall_maturity_percent": overall_maturity_percent,
            "practice_scores": merged_practices,
            "recommendations": all_recommendations,  # preserved raw; may be deduped later
            "gaps": gap_matched + gap_unmatched,
            "matched_gap_count": len(gap_matched),
            "unmatched_gap_count": len(gap_unmatched),
            "framework": self.pillar_display_name,
        }

    def write_results_markdown(self, assessment: PillarAssessment, *, filename: Optional[str] = None) -> Path:
        output_dir = self.project_root / "results"
        output_dir.mkdir(parents=True, exist_ok=True)
        file_name = filename or f"RESULTS_{self.pillar_code.upper()}.md"
        target = output_dir / file_name
        md = self.build_results_markdown(assessment)
        target.write_text(md, encoding="utf-8")
        logger.info(
            "Markdown written | pillar=%s | path=%s | bytes=%d",
            self.pillar_code,
            target,
            len(md),
        )
        return target

    def write_assessment_artifacts(
        self,
        assessment: PillarAssessment,
        *,
        output_dir: str = "results",
        markdown_filename: Optional[str] = None,
        json_filename: Optional[str] = None,
    ) -> Dict[str, Path]:
        """Write both markdown and JSON assessment artifacts.

        Args:
            assessment: PillarAssessment object
            output_dir: Output directory path
            markdown_filename: Optional markdown filename override
            json_filename: Optional JSON filename override

        Returns:
            Dict with 'markdown' and 'json' Path objects
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Markdown report
        md_name = markdown_filename or f"{self.pillar_code}_assessment.md"
        md_file = output_path / md_name
        markdown_content = self.build_results_markdown(assessment)
        md_file.write_text(markdown_content, encoding="utf-8")
        logger.info("Markdown artifact written | path=%s | bytes=%d", md_file, len(markdown_content))

        # JSON data
        js_name = json_filename or f"{self.pillar_code}_assessment.json"
        js_file = output_path / js_name
        json_data = {
            "overall_score": assessment.overall_score,
            "domain_scores": assessment.domain_scores,
            "recommendations": assessment.recommendations,
            "maturity": assessment.maturity,
            "mcp_references": assessment.mcp_references,
            "timestamp": assessment.timestamp,
        }
        js_file.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        logger.info("JSON artifact written | path=%s | bytes=%d", js_file, len(json.dumps(json_data)))

        return {"markdown": md_file, "json": js_file}

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    async def cleanup(self) -> None:
        """Clean up async resources to prevent unclosed session warnings."""
        # Give pending tasks a moment to complete
        await asyncio.sleep(0.05)
        logger.debug("Cleanup starting for %s", self.agent_name)
        
        if self._client is not None:
            try:
                await self._client.close()
                logger.debug("Client closed for %s", self.agent_name)
            except Exception:
                pass  # Ignore cleanup errors
        if self._async_credential is not None:
            try:
                await self._async_credential.close()
                logger.debug("Async credential closed for %s", self.agent_name)
            except Exception:
                pass  # Ignore cleanup errors

    # ------------------------------------------------------------------
    # Convenience utilities
    # ------------------------------------------------------------------
    async def run_sample(self, architecture_text: str) -> PillarAssessment:
        assessment = await self.assess_architecture(architecture_text)
        self.write_results_markdown(assessment)
        return assessment


async def run_agent_cli(agent: BasePillarAgent, architecture_path: Optional[Path], quiet: bool = False) -> None:
    if architecture_path and architecture_path.exists():
        architecture = architecture_path.read_text(encoding="utf-8")
    else:
        architecture = ""

    try:
        assessment = await agent.assess_architecture(architecture)
        print(
            f"LLM Score: {assessment.overall_score}/100 | "
            f"Recommendations: {len(assessment.recommendations)} | "
            f"Maturity %: {assessment.maturity.get('overall_maturity_percent')}"
        )
        if not quiet:
            print(json.dumps(asdict(assessment), indent=2, default=str))

        output_path = agent.write_results_markdown(assessment)
        if not quiet:
            print(f"Markdown report written to {output_path}")
    finally:
        # Always cleanup async resources
        await agent.cleanup()


__all__ = [
    "BasePillarAgent",
    "PillarAssessment",
    "run_agent_cli",
]
