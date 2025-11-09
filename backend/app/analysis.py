"""Minimal analysis layer stub to unblock FastAPI server imports.

Provides DocumentAnalyzer and AssessmentOrchestrator classes expected by `backend.server`.
Real implementation would perform semantic chunking, normalization, cross-pillar alignment, etc.
This stub focuses on:
  * Parsing uploaded documents into a unified corpus
  * Returning lightweight metadata structures consumed by pillar executor
  * Orchestrating lifecycle phases via callbacks supplied by the server

Safe to replace later with full implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Awaitable
import asyncio
import re


@dataclass
class _CorpusContainer:
    """Simple container used by server to access `full_corpus` attribute."""
    full_corpus: str


class DocumentAnalyzer:
    """Analyzer with lightweight extraction/summarization capabilities.

    For architecture diagrams we attempt structured text extraction to enrich the
    unified corpus. The strategy is heuristic-first (fast) with optional Azure
    OpenAI vision summarization if credentials are present. This keeps runtime
    dependencies minimal while enabling future extensibility.
    """
    def __init__(self, llm_enabled: bool = False) -> None:
        self.llm_enabled = llm_enabled
        # Lazy initialization flags for optional Azure OpenAI client
        self._azure_client = None
        if llm_enabled:
            try:  # pragma: no cover - network client creation
                from openai import AsyncAzureOpenAI  # type: ignore
                import os
                endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                key = os.getenv("AZURE_OPENAI_API_KEY")
                api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
                if endpoint and key:
                    self._azure_client = AsyncAzureOpenAI(
                        azure_endpoint=endpoint,
                        api_key=key,
                        api_version=api_version,
                    )
            except Exception as e:  # pragma: no cover - fail quietly if lib missing
                print(f"[diagram-analyzer] [WARN] Azure client init failed: {e}")

    async def analyze_architecture_document(self, text: str, filename: str) -> Dict[str, Any]:
        return {
            "type": "architecture",
            "filename": filename,
            "length": len(text),
            "llm_analysis": self._basic_summary(text, max_sentences=6),
        }

    async def analyze_support_cases(self, csv_text: str, filename: str) -> Dict[str, Any]:
        # Extract rows containing keywords for quick signal enrichment
        lines = [l for l in csv_text.splitlines() if l.strip()]
        keywords = ("error", "fail", "latency", "timeout", "security")
        matches = [l[:240] for l in lines if any(k in l.lower() for k in keywords)][:25]
        return {
            "type": "case_csv",
            "filename": filename,
            "rows": len(lines),
            "matches": matches,
            "llm_analysis": "\n".join(matches) if matches else "No notable case patterns detected.",
        }

    async def analyze_diagram(self, raw_bytes: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Extract textual signals from a diagram.

        Strategies (ordered):
          1. SVG: parse <text> nodes directly.
          2. Heuristic filename/entity tokens.
          3. Optional Azure OpenAI vision summarization (multimodal) if enabled.

        Returns dict with keys:
          type, filename, bytes, mime, extracted_text, summary, strategy, llm_analysis
        """
        size = len(raw_bytes)
        lower_name = filename.lower()
        strategy_chain: List[str] = []
        extracted_segments: List[str] = []

        # 1. SVG direct text extraction
        if content_type.endswith("svg") or lower_name.endswith(".svg"):
            try:
                import xml.etree.ElementTree as ET
                tree = ET.fromstring(raw_bytes.decode("utf-8", errors="ignore"))
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
        base_name = lower_name.replace(".svg", "")
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
        deployment = None
        if self._azure_client:
            import os
            deployment = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            if deployment:
                try:  # pragma: no cover - external call
                    # NOTE: Using chat completions; if future multimodal requires different API adjust here.
                    b64 = _to_base64_safe(raw_bytes)
                    prompt = ("You are an Azure Well-Architected assistant. Extract key Azure service names, "
                              "components, tiers, and any resiliency/security/cost/performance hints from this architecture diagram. "
                              "Return a concise bullet list (max 12 bullets).")
                    response = await self._azure_client.chat.completions.create(
                        model=deployment,
                        messages=[
                            {"role": "system", "content": "You convert diagrams into structured architecture bullet points."},
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/{_infer_image_ext(content_type)};base64,{b64}"}}
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
        summary = self._basic_summary(summary_source, max_sentences=5)

        print(f"[analyze_diagram] Extracted {len(extracted_segments)} segments: {extracted_segments[:3]}")
        print(f"[analyze_diagram] extracted_text length: {len(extracted_text)}, summary length: {len(summary)}")

        return {
            "type": "diagram",
            "filename": filename,
            "bytes": size,
            "mime": content_type,
            "extracted_text": extracted_text,
            "summary": summary,
            "strategy": ",".join(strategy_chain) if strategy_chain else "none",
            "llm_analysis": summary,
        }

    def _basic_summary(self, text: str, *, max_sentences: int = 5) -> str:
        # Naive sentence boundary split
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        summary = " ".join(parts[:max_sentences])
        if len(parts) > max_sentences:
            summary += " ..."
        return summary[:1200]


def _to_base64_safe(raw: bytes) -> str:
    import base64
    return base64.b64encode(raw).decode("utf-8")


def _infer_image_ext(content_type: str) -> str:
    if "png" in content_type:
        return "png"
    if "jpeg" in content_type or "jpg" in content_type:
        return "jpeg"
    if "svg" in content_type:
        return "svg+xml"
    return "png"


class AssessmentOrchestrator:
    """Stub orchestration engine coordinating assessment lifecycle.

    The real implementation would perform multiple phases (preprocessing, evidence alignment,
    conflict detection, pillar execution with advanced prompt composition, etc.). This stub:
      1. Concatenates document raw_text fields into unified corpus
      2. Invokes provided `pillar_executor(corpus_container)` coroutine to evaluate pillars
      3. Returns dict matching expected shape consumed by server
    """
    async def run_assessment_lifecycle(
        self,
        *,
        assessment_id: str,
        documents: List[Dict[str, Any]],
        analysis_results: Dict[str, Any],
        pillar_executor: Callable[[Any], Awaitable[List[Dict[str, Any]]]],
        progress_callback: Callable[[int, str], Awaitable[None]],
    ) -> Dict[str, Any]:
        # Phase: aggregation
        await progress_callback(10, "Aggregating Documents")
        raw_parts: List[str] = []
        for d in documents:
            if d.get("raw_text"):
                raw_parts.append(str(d.get("raw_text")))
            if d.get("llm_analysis"):
                raw_parts.append(str(d.get("llm_analysis")))
        unified_corpus = "\n\n" + "\n\n".join(raw_parts)
        corpus_container = _CorpusContainer(full_corpus=unified_corpus)

        # Phase: simple enrichment (placeholder)
        await progress_callback(15, "Normalizing Evidence")
        await asyncio.sleep(0)  # yield control

        # Phase: pillar execution
        await progress_callback(20, "Executing Pillars")
        pillar_results = await pillar_executor(corpus_container)

        # Phase: cross-pillar conflict detection (stub - none)
        await progress_callback(85, "Analyzing Cross-Pillar Conflicts")
        cross_pillar_conflicts: List[Dict[str, str]] = []

        # Compute overall architecture score as average of pillar scores (if any)
        overall_score = 0.0
        if pillar_results:
            overall_score = round(
                sum(r.get("overall_score", 0) for r in pillar_results) / len(pillar_results), 2
            )

        await progress_callback(95, "Finalizing")
        await asyncio.sleep(0)

        return {
            "pillar_results": pillar_results,
            "cross_pillar_conflicts": cross_pillar_conflicts,
            "overall_architecture_score": overall_score,
            "unified_corpus": unified_corpus,
        }

__all__ = ["DocumentAnalyzer", "AssessmentOrchestrator"]
