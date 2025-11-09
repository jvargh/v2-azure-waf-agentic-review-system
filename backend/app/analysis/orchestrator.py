"""Assessment orchestration and lifecycle management.

Implements the initiator/collector pattern for coordinating pillar agents
and managing assessment progression through lifecycle states.
"""

from __future__ import annotations

import asyncio
import math
import logging
from typing import Dict, List, Optional, Any, Callable, Iterable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AssessmentState(str, Enum):
    """Assessment lifecycle states."""
    NEW = "new"
    REGISTERED = "pending"
    PREPROCESSING = "preprocessing"
    ACTIVE_ANALYSIS = "analyzing"
    CROSS_PILLAR_ALIGNMENT = "aligning"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProgressPhase:
    """Represents a phase in assessment progression."""
    name: str
    start_percent: int
    end_percent: int
    description: str


@dataclass
class UnifiedReviewCorpus:
    """Consolidated analysis substrate for pillar agents."""
    architecture_narrative: str
    visual_augmentation: str
    reactive_case_signals: str
    component_inventory: List[Dict[str, str]]
    pillar_context: Dict[str, List[str]]
    full_corpus: str = field(init=False)
    
    def __post_init__(self):
        """Generate full corpus from components."""
        parts = []
        
        if self.architecture_narrative:
            parts.append("=== ARCHITECTURE NARRATIVE ===\n" + self.architecture_narrative)
        
        if self.visual_augmentation:
            parts.append("\n=== VISUAL TOPOLOGY INSIGHTS ===\n" + self.visual_augmentation)
        
        if self.reactive_case_signals:
            parts.append("\n=== OPERATIONAL REALITY (SUPPORT CASES) ===\n" + self.reactive_case_signals)
        
        if self.component_inventory:
            parts.append("\n=== COMPONENT INVENTORY ===")
            by_category = {}
            for comp in self.component_inventory:
                cat = comp.get("category", "other")
                by_category.setdefault(cat, []).append(comp["service"])
            for cat, services in by_category.items():
                parts.append(f"{cat.title()}: {', '.join(set(services))}")
        
        self.full_corpus = "\n".join(parts)
        # Append aggregated pillar evidence section if pillar_context populated
        if self.pillar_context:
            evidence_section = ["\n=== CONSOLIDATED PILLAR EVIDENCE ==="]
            for pillar, signals in self.pillar_context.items():
                if signals:
                    truncated = signals[:8]
                    evidence_section.append(f"**{pillar.title()}**: " + "; ".join(truncated))
            self.full_corpus += "\n" + "\n".join(evidence_section)


class AssessmentOrchestrator:
    """Orchestrates assessment lifecycle and pillar agent coordination."""
    
    # Non-linear progress distribution across phases
    PHASES = [
        ProgressPhase("Initialization", 0, 5, "Setting up analysis environment"),
        ProgressPhase("Document Processing", 5, 15, "Analyzing uploaded artifacts"),
        ProgressPhase("Corpus Assembly", 15, 20, "Building unified review context"),
        ProgressPhase("Pillar Evaluation", 20, 80, "Running five pillar assessments concurrently"),
        ProgressPhase("Cross-Pillar Alignment", 80, 90, "Identifying dependencies and conflicts"),
        ProgressPhase("Synthesis", 90, 95, "Generating cohesive recommendations"),
        ProgressPhase("Finalization", 95, 100, "Completing assessment"),
    ]
    
    def __init__(self, llm_provider=None):
        """Initialize orchestrator.
        
        Args:
            llm_provider: Optional centralized LLM provider for embeddings
        """
        self.current_state = AssessmentState.NEW
        self.current_phase_index = 0
        self.llm_provider = llm_provider
    
    def get_phase_for_progress(self, progress: int) -> ProgressPhase:
        """Get current phase based on progress percentage."""
        for phase in self.PHASES:
            if phase.start_percent <= progress <= phase.end_percent:
                return phase
        return self.PHASES[-1]
    
    def calculate_phase_progress(self, phase_name: str, sub_progress: float) -> int:
        """Calculate overall progress within a specific phase.
        
        Args:
            phase_name: Name of the current phase
            sub_progress: Progress within phase (0.0 to 1.0)
        
        Returns:
            Overall progress percentage
        """
        phase = next((p for p in self.PHASES if p.name == phase_name), None)
        if not phase:
            return 0
        
        range_size = phase.end_percent - phase.start_percent
        offset = int(range_size * sub_progress)
        return phase.start_percent + offset
    
    async def create_unified_corpus(
        self,
        documents: List[Dict[str, Any]],
        analysis_results: Dict[str, Dict[str, Any]]
    ) -> UnifiedReviewCorpus:
        """Create unified review corpus from analyzed documents with structured report enrichment.
        
        Args:
            documents: List of uploaded documents
            analysis_results: Document analysis results keyed by document ID
        
        Returns:
            UnifiedReviewCorpus ready for pillar agent consumption
        """
        # Collect structured reports for aggregation
        executive_summaries = []
        arch_overviews = []
        # Dynamically accumulate cross-cutting dimensions; start with known defaults but allow new ones (e.g., cost_optimization)
        cross_cutting_aggregated: Dict[str, List[str]] = {"security": [], "scalability": [], "availability": [], "observability": []}
        deployment_summaries = []
        case_concerns = []
        
        # Concatenate architecture narratives with structured sections
        arch_parts = []
        for doc in documents:
            if doc.get("category") == "architecture":
                analysis = analysis_results.get(doc["id"], {})
                arch_parts.append(f"## {doc['filename']}\n{doc.get('raw_text', '')}")
                
                # Inject structured report sections if available
                structured_report = doc.get("structured_report") or analysis.get("structured_report")
                if structured_report:
                    if structured_report.get("executive_summary"):
                        executive_summaries.append(structured_report["executive_summary"])
                        arch_parts.append(f"\n### EXECUTIVE SUMMARY\n{structured_report['executive_summary']}\n")
                    
                    if structured_report.get("architecture_overview"):
                        arch_overviews.append(structured_report["architecture_overview"])
                        arch_parts.append(f"\n### ARCHITECTURE OVERVIEW\n{structured_report['architecture_overview']}\n")
                    
                    if structured_report.get("cross_cutting_concerns"):
                        arch_parts.append("\n### CROSS-CUTTING CONCERNS")
                        for dimension, finding in structured_report["cross_cutting_concerns"].items():
                            arch_parts.append(f"**{dimension.title()}**: {finding}")
                            cross_cutting_aggregated.setdefault(dimension, []).append(finding)
                    
                    if structured_report.get("deployment_summary"):
                        deployment_summaries.append(structured_report["deployment_summary"])
                        arch_parts.append(f"\n### DEPLOYMENT SUMMARY\n{structured_report['deployment_summary']}\n")
                
                if analysis.get("llm_analysis"):
                    arch_parts.append(f"### Analysis Insights\n{analysis['llm_analysis']}\n")
        
        architecture_narrative = "\n\n".join(arch_parts)
        
        # Visual augmentation from diagrams with structured enrichment
        visual_parts = []
        for doc in documents:
            if doc.get("category") == "diagram":
                analysis = analysis_results.get(doc["id"], {})
                
                # Inject structured report sections
                structured_report = doc.get("structured_report") or analysis.get("structured_report")
                if structured_report:
                    if structured_report.get("executive_summary"):
                        executive_summaries.append(structured_report["executive_summary"])
                        visual_parts.append(f"## {doc['filename']} - EXECUTIVE SUMMARY\n{structured_report['executive_summary']}\n")
                    
                    if structured_report.get("architecture_overview"):
                        arch_overviews.append(structured_report["architecture_overview"])
                        visual_parts.append(f"### ARCHITECTURE OVERVIEW (Visual)\n{structured_report['architecture_overview']}\n")
                    
                    if structured_report.get("cross_cutting_concerns"):
                        visual_parts.append("### CROSS-CUTTING CONCERNS (Diagram)")
                        for dimension, finding in structured_report["cross_cutting_concerns"].items():
                            visual_parts.append(f"**{dimension.title()}**: {finding}")
                            cross_cutting_aggregated.setdefault(dimension, []).append(finding)
                    
                    if structured_report.get("deployment_summary"):
                        deployment_summaries.append(structured_report["deployment_summary"])
                        visual_parts.append(f"### DEPLOYMENT (Visual)\n{structured_report['deployment_summary']}\n")
                
                if analysis.get("llm_analysis"):
                    visual_parts.append(f"## {doc['filename']}\n{analysis['llm_analysis']}")
                if analysis.get("topology_insights"):
                    visual_parts.extend(analysis["topology_insights"])
        
        visual_augmentation = "\n\n".join(visual_parts)
        
        # Reactive case signals with concerns injection
        case_parts = []
        for doc in documents:
            if doc.get("category") == "case":
                analysis = analysis_results.get(doc["id"], {})
                
                # Inject structured concerns report
                structured_report = doc.get("structured_report") or analysis.get("structured_report")
                if structured_report:
                    if structured_report.get("executive_summary"):
                        executive_summaries.append(structured_report["executive_summary"])
                        case_parts.append(f"## SUPPORT CASE EXECUTIVE SUMMARY\n{structured_report['executive_summary']}\n")
                    
                    if structured_report.get("support_case_concerns"):
                        case_concerns.append(structured_report["support_case_concerns"])
                        case_parts.append(f"### SUPPORT CASE CONCERNS\n{structured_report['support_case_concerns']}\n")
                    
                    if structured_report.get("cross_cutting_concerns"):
                        case_parts.append("### HISTORICAL INCIDENT CROSS-CUTTING PATTERNS")
                        for dimension, finding in structured_report["cross_cutting_concerns"].items():
                            case_parts.append(f"**{dimension.title()}**: {finding}")
                            cross_cutting_aggregated.setdefault(dimension, []).append(finding)
                    
                    if structured_report.get("deployment_summary"):
                        deployment_summaries.append(structured_report["deployment_summary"])
                        case_parts.append(f"### OPERATIONAL DEPLOYMENT INSIGHTS\n{structured_report['deployment_summary']}\n")
                
                if analysis.get("llm_analysis"):
                    case_parts.append(analysis["llm_analysis"])
                
                # Add thematic patterns
                if analysis.get("thematic_patterns"):
                    case_parts.append("\nThematic Pattern Distribution:")
                    for theme, cases in analysis["thematic_patterns"].items():
                        case_parts.append(f"  • {theme.title()}: {len(cases)} cases")
                
                # Add risk signals
                if analysis.get("risk_signals"):
                    case_parts.append("\nRisk Signals:")
                    for risk in analysis["risk_signals"]:
                        if risk.get("severity") in ["high", "medium"]:
                            case_parts.append(f"  ⚠ {risk['risk_qualifier']}")
        
        reactive_case_signals = "\n\n".join(case_parts)
        
        # Generate aggregated assessment-level summary if multiple docs exist
        aggregated_summary = ""
        if len(executive_summaries) > 1:
            aggregated_summary = "\n=== AGGREGATED ASSESSMENT EXECUTIVE SUMMARY ===\n"
            aggregated_summary += f"This assessment analyzed {len(documents)} artifacts ({sum(1 for d in documents if d.get('category') == 'architecture')} architecture document(s), "
            aggregated_summary += f"{sum(1 for d in documents if d.get('category') == 'diagram')} diagram(s), {sum(1 for d in documents if d.get('category') == 'case')} support case dataset(s)).\n\n"
            
            if arch_overviews:
                aggregated_summary += "**Key Architecture Components**: Multiple documents describe distributed Azure architecture with components across compute, storage, networking, security layers.\n\n"
            
            aggregated_summary += "**Cross-Cutting Concerns Summary**:\n"
            for dimension, findings in cross_cutting_aggregated.items():
                if findings:
                    aggregated_summary += f"- {dimension.title()}: {len(findings)} finding(s) across artifacts; consolidated review required\n"
            
            if deployment_summaries:
                aggregated_summary += f"\n**Deployment Considerations**: {len(deployment_summaries)} artifact(s) provide deployment context; review for consistency.\n"
            
            if case_concerns:
                aggregated_summary += f"**Operational History**: {len(case_concerns)} support case analysis reveals recurring operational challenges.\n"
            
            aggregated_summary += "\n"
        
        # Component inventory
        component_inventory = []
        for doc_id, analysis in analysis_results.items():
            if analysis.get("components_identified"):
                component_inventory.extend(analysis["components_identified"])
        
        # Pillar context signals (aggregate + inferred diagram evidence)
        from .artifact_normalizer import collect_and_infer_pillar_evidence
        pillar_context: Dict[str, List[str]] = {}
        # Collect existing pillar signals from analysis
        for doc_id, analysis in analysis_results.items():
            if analysis.get("pillar_signals"):
                for pillar, signals in analysis["pillar_signals"].items():
                    pillar_context.setdefault(pillar, []).extend(signals)
        # Add structured_report pillar_evidence and inferred diagram evidence excerpts
        consolidated_evidence = collect_and_infer_pillar_evidence(documents, analysis_results, self.llm_provider)
        for pillar, data in consolidated_evidence.items():
            excerpts = data.get("excerpts", [])
            if excerpts:
                pillar_context.setdefault(pillar, []).extend(excerpts)
        # Deduplicate signals per pillar (semantic-lite using lowercase key slice)
        for pillar, sigs in list(pillar_context.items()):
            seen = set()
            deduped = []
            for s in sigs:
                key = s.lower()[:140]
                if key not in seen:
                    seen.add(key)
                    deduped.append(s)
            pillar_context[pillar] = deduped
        
        # Prepend aggregated summary if generated
        if aggregated_summary:
            architecture_narrative = aggregated_summary + "\n" + architecture_narrative
        
        # Build corpus with structured sections
        corpus = UnifiedReviewCorpus(
            architecture_narrative=self._safe_truncate_corpus_section(architecture_narrative, max_tokens=5000),
            visual_augmentation=self._safe_truncate_corpus_section(visual_augmentation, max_tokens=3000),
            reactive_case_signals=self._safe_truncate_corpus_section(reactive_case_signals, max_tokens=4000),
            component_inventory=component_inventory,
            pillar_context=pillar_context
        )
        
        return corpus
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count using simple heuristic (words * 1.3)."""
        if not text:
            return 0
        return int(len(text.split()) * 1.3)
    
    def _safe_truncate_corpus_section(self, section_text: str, max_tokens: int) -> str:
        """Truncate section to stay within token budget, adding truncation marker if needed."""
        if not section_text:
            return section_text
        
        estimated_tokens = self._estimate_tokens(section_text)
        
        if estimated_tokens <= max_tokens:
            return section_text
        
        # Hard truncate to approximate token limit (rough: 1 token ≈ 4 chars)
        max_chars = max_tokens * 4
        if len(section_text) > max_chars:
            truncated = section_text[:max_chars]
            # Try to truncate at sentence boundary
            last_period = truncated.rfind('.')
            if last_period > max_chars * 0.8:  # If period found in last 20%, use it
                truncated = truncated[:last_period + 1]
            return truncated + "\n\n... [Content truncated for token budget - full context preserved in document analysis]"
        
        return section_text
    
    async def detect_cross_pillar_conflicts(
        self,
        pillar_results: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Detect conflicts and dependencies between pillar recommendations.
        
        Args:
            pillar_results: Results from all five pillar assessments
        
        Returns:
            List of detected conflicts with mitigation suggestions
        """
        logger.info("🔍 Starting cross-pillar conflict detection")
        conflicts = []
        
        # Extract recommendations by pillar
        recs_by_pillar = {}
        for result in pillar_results:
            pillar = result.get("pillar", "unknown")
            recs = result.get("recommendations", [])
            recs_by_pillar[pillar] = recs
            logger.debug(f"  Pillar '{pillar}': {len(recs)} recommendations")
        
        # Cost vs Reliability conflicts
        cost_recs = recs_by_pillar.get("Cost Optimization", [])
        reliability_recs = recs_by_pillar.get("Reliability", [])
        
        for cost_rec in cost_recs:
            cost_text = (cost_rec.get("title", "") + " " + cost_rec.get("reasoning", "")).lower()
            if any(k in cost_text for k in ["reduce", "downsize", "lower tier", "scale down"]):
                for rel_rec in reliability_recs:
                    rel_text = (rel_rec.get("title", "") + " " + rel_rec.get("reasoning", "")).lower()
                    if any(k in rel_text for k in ["redundancy", "replica", "multi-region", "failover"]):
                        conflicts.append({
                            "type": "cost_vs_reliability",
                            "pillar_a": "Cost Optimization",
                            "pillar_b": "Reliability",
                            "description": "Cost reduction measures may undermine availability targets",
                            "mitigation": "Prioritize cost optimization in non-critical paths; preserve redundancy for critical flows"
                        })
                        logger.info(f"  ⚠️  Detected conflict: Cost Optimization ↔ Reliability")
                        break
        
        # Security vs Performance conflicts
        security_recs = recs_by_pillar.get("Security", [])
        performance_recs = recs_by_pillar.get("Performance Efficiency", [])
        
        for sec_rec in security_recs:
            sec_text = (sec_rec.get("title", "") + " " + sec_rec.get("reasoning", "")).lower()
            if any(k in sec_text for k in ["encrypt", "authentication", "firewall", "inspection"]):
                for perf_rec in performance_recs:
                    perf_text = (perf_rec.get("title", "") + " " + perf_rec.get("reasoning", "")).lower()
                    if any(k in perf_text for k in ["latency", "faster", "reduce overhead"]):
                        conflicts.append({
                            "type": "security_vs_performance",
                            "pillar_a": "Security",
                            "pillar_b": "Performance Efficiency",
                            "description": "Security hardening may introduce performance overhead",
                            "mitigation": "Use Azure-native security services with performance optimization (e.g., Azure Front Door with WAF)"
                        })
                        logger.info(f"  ⚠️  Detected conflict: Security ↔ Performance Efficiency")
                        break
        
        # Operational complexity dependencies
        operational_recs = recs_by_pillar.get("Operational Excellence", [])
        
        for op_rec in operational_recs:
            op_text = (op_rec.get("title", "") + " " + op_rec.get("reasoning", "")).lower()
            if any(k in op_text for k in ["automation", "ci/cd", "pipeline", "iac"]):
                # This supports multiple pillars
                conflicts.append({
                    "type": "operational_enabler",
                    "pillar_a": "Operational Excellence",
                    "pillar_b": "All Pillars",
                    "description": "Automation and IaC improvements enable better outcomes across all pillars",
                    "mitigation": "Prioritize operational excellence as foundational capability"
                })
                logger.info(f"  💡 Detected enabler: Operational Excellence → All Pillars")
                break
        
        logger.info(f"✅ Cross-pillar analysis complete: {len(conflicts)} conflict(s)/dependency(ies) detected")
        return conflicts
    
    async def generate_cohesive_recommendations(
        self,
        pillar_results: List[Dict[str, Any]],
        conflicts: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Generate cohesive cross-pillar recommendations.
        
        Args:
            pillar_results: Individual pillar assessment results
            conflicts: Detected conflicts and dependencies
        
        Returns:
            Enhanced recommendations with conflict-aware guidance
        """
        logger.info("🔧 Starting cohesive recommendation synthesis")
        
        # Collect all recommendations
        all_recs = []
        for result in pillar_results:
            pillar = result.get("pillar", "unknown")
            for rec in result.get("recommendations", []):
                rec_copy = rec.copy()
                rec_copy["source_pillar"] = pillar
                all_recs.append(rec_copy)
        
        logger.debug(f"  Total recommendations collected: {len(all_recs)}")
        
        # Enrich with conflict awareness
        enriched_count = 0
        for rec in all_recs:
            rec_text = (rec.get("title", "") + " " + rec.get("reasoning", "")).lower()
            
            # Check if this rec is involved in conflicts
            related_conflicts = []
            for conflict in conflicts:
                if conflict.get("type") in ["cost_vs_reliability", "security_vs_performance"]:
                    if rec.get("source_pillar") in [conflict.get("pillar_a"), conflict.get("pillar_b")]:
                        # Check if rec keywords match conflict
                        if any(keyword in rec_text for keyword in ["cost", "reduce", "downsize", "encrypt", "security", "latency"]):
                            related_conflicts.append(conflict)
            
            if related_conflicts:
                # Add cross-pillar consideration
                considerations = []
                for conf in related_conflicts:
                    considerations.append(f"⚠ {conf['description']} - {conf['mitigation']}")
                
                rec["cross_pillar_considerations"] = considerations
                enriched_count += 1
        
        logger.info(f"  Enriched {enriched_count} recommendations with cross-pillar considerations")
        
        # Semantic deduplication across artifact types / pillars
        deduped = self._dedupe_semantic_recommendations(all_recs)
        logger.info(f"✅ Synthesis complete: {len(deduped)} cohesive recommendations (after deduplication)")
        
        return deduped

    # ------------------------------------------------------------------
    # Recommendation semantic deduplication
    # ------------------------------------------------------------------
    def _dedupe_semantic_recommendations(self, recs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not recs:
            return recs
        # Build text corpus
        texts = [ (r.get("title",""), r.get("reasoning","")) for r in recs ]
        combined = [ (t[0] + " \n" + t[1]).strip() for t in texts ]
        # Attempt embedding via llm_provider first, fallback to legacy OpenAI, then bag-of-words
        vectors: List[List[float]] = []
        if self.llm_provider:
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    vectors_result = loop.run_until_complete(self.llm_provider.embed(combined))
                    if vectors_result:
                        vectors = vectors_result
            except Exception:
                pass
        if not vectors:
            # Legacy fallback: direct OpenAI client
            try:
                from openai import OpenAI  # type: ignore
                import os
                api_key = (os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY"))
                if api_key:
                    client = OpenAI()
                    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
                    resp = client.embeddings.create(model=model, input=combined)
                    vectors = [d.embedding for d in resp.data]
            except Exception:
                pass
        if not vectors:
            # Simple bag-of-words normalization
            vocab: Dict[str,int] = {}
            tokenized: List[List[str]] = []
            for c in combined:
                toks = [tok for tok in c.lower().split() if tok.isalpha()]
                tokenized.append(toks)
                for tok in toks:
                    if tok not in vocab:
                        vocab[tok] = len(vocab)
            for toks in tokenized:
                vec = [0.0]*len(vocab)
                for tok in toks:
                    vec[vocab[tok]] += 1.0
                norm = math.sqrt(sum(v*v for v in vec)) or 1.0
                vectors.append([v/norm for v in vec])

        def _cos(a: List[float], b: List[float]) -> float:
            return sum(x*y for x,y in zip(a,b)) / ((math.sqrt(sum(x*x for x in a)) or 1.0)*(math.sqrt(sum(y*y for y in b)) or 1.0))

        kept: List[Dict[str,Any]] = []
        # Maintain mapping of representative vectors
        rep_vectors: List[List[float]] = []
        for idx, rec in enumerate(recs):
            vec = vectors[idx]
            is_duplicate = False
            for rep_vec in rep_vectors:
                if _cos(vec, rep_vec) > 0.90:  # High similarity threshold
                    is_duplicate = True
                    break
            if not is_duplicate:
                kept.append(rec)
                rep_vectors.append(vec)
        return kept
    
    async def run_assessment_lifecycle(
        self,
        assessment_id: str,
        documents: List[Dict[str, Any]],
        analysis_results: Dict[str, Dict[str, Any]],
        pillar_executor: Callable,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Dict[str, Any]:
        """Execute complete assessment lifecycle.
        
        Args:
            assessment_id: Unique assessment identifier
            documents: Uploaded documents
            analysis_results: Document analysis results
            pillar_executor: Async function to execute pillar agents
            progress_callback: Optional callback for progress updates
        
        Returns:
            Complete assessment results
        """
        async def update_progress(percent: int, description: str = ""):
            if progress_callback:
                await progress_callback(percent, description)
        
        # Phase 1: Initialization
        await update_progress(5, "Initializing assessment environment")
        self.current_state = AssessmentState.PREPROCESSING
        
        # Phase 2-3: Corpus Assembly
        await update_progress(10, "Processing uploaded artifacts")
        corpus = await self.create_unified_corpus(documents, analysis_results)
        
        await update_progress(20, "Unified review corpus assembled")
        self.current_state = AssessmentState.ACTIVE_ANALYSIS
        
        # Phase 4: Pillar Evaluation (concurrent)
        await update_progress(25, "Launching five pillar assessments")
        pillar_results = await pillar_executor(corpus)
        
        await update_progress(80, "Pillar assessments complete")
        self.current_state = AssessmentState.CROSS_PILLAR_ALIGNMENT
        
        # Phase 5: Cross-Pillar Alignment (with minimum duration for visibility)
        await update_progress(85, "Analyzing cross-pillar dependencies")
        logger.info("⏳ Phase 5: Cross-Pillar Alignment starting...")
        conflicts_task = asyncio.create_task(self.detect_cross_pillar_conflicts(pillar_results))
        min_duration_task = asyncio.create_task(asyncio.sleep(2.5))  # Minimum 2.5s for visibility
        conflicts, _ = await asyncio.gather(conflicts_task, min_duration_task)
        logger.info(f"✅ Phase 5 complete: {len(conflicts)} conflicts/dependencies identified")
        
        # Phase 6: Synthesis (with minimum duration for visibility)
        await update_progress(90, "Generating cohesive recommendations")
        logger.info("⏳ Phase 6: Synthesis starting...")
        cohesive_task = asyncio.create_task(self.generate_cohesive_recommendations(pillar_results, conflicts))
        min_duration_task = asyncio.create_task(asyncio.sleep(2.5))  # Minimum 2.5s for visibility
        cohesive_recs, _ = await asyncio.gather(cohesive_task, min_duration_task)
        logger.info(f"✅ Phase 6 complete: {len(cohesive_recs)} cohesive recommendations generated")
        
        # Phase 7: Finalization (with minimum duration for visibility)
        await update_progress(95, "Finalizing assessment")
        logger.info("⏳ Phase 7: Finalization starting...")
        await asyncio.sleep(2.0)  # Minimum 2s for visibility
        
        overall_score = 0
        if pillar_results:
            overall_score = sum(r.get("overall_score", 0) for r in pillar_results) / len(pillar_results)
        
        logger.info(f"✅ Phase 7 complete: Overall architecture score = {round(overall_score, 2)}%")
        
        await update_progress(100, "Assessment complete")
        self.current_state = AssessmentState.COMPLETED
        
        return {
            "pillar_results": pillar_results,
            "cross_pillar_conflicts": conflicts,
            "cohesive_recommendations": cohesive_recs,
            "overall_architecture_score": round(overall_score, 2),
            "unified_corpus": corpus.full_corpus
        }
