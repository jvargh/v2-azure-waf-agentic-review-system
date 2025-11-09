"""Quick test for enhanced architecture document structured report output.

Ensures the repository root is on sys.path so that the sibling `backend` package
can be imported when executing this script directly (python scripts/foo.py).
"""
import asyncio
from pathlib import Path
import sys

# Add repo root (parent of this file's directory) to sys.path for direct execution
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.analysis.document_analyzer import DocumentAnalyzer

def format_section(title: str):
    print("=" * 80)
    print(title)
    print("=" * 80)

async def main():
    doc_path = Path("sample_data/excellent_architecture.txt")
    if not doc_path.exists():
        print("Sample architecture document missing:", doc_path)
        return
    content = doc_path.read_text(encoding="utf-8")
    analyzer = DocumentAnalyzer()
    result = await analyzer.analyze_architecture_document(content, doc_path.name)
    sr = result.get("structured_report", {})

    format_section("EXECUTIVE SUMMARY")
    print(sr.get("executive_summary", "<missing>")[:1200])

    format_section("ARCHITECTURE OVERVIEW (first 800 chars)")
    print(sr.get("architecture_overview", "<missing>")[:800])

    format_section("CROSS-CUTTING CONCERNS KEYS")
    print(list(sr.get("cross_cutting_concerns", {}).keys()))
    for k,v in sr.get("cross_cutting_concerns", {}).items():
        print(f"\n[{k}]\n{v[:300]}{'...' if len(v)>300 else ''}")

    format_section("DEPLOYMENT SUMMARY (first 600 chars)")
    print(sr.get("deployment_summary", "<missing>")[:600])

    evidence = sr.get("evidence_sources", {})
    format_section("EVIDENCE - SERVICES (sample)")
    svc_ev = evidence.get("services", {})
    print("Total services with evidence:", len(svc_ev))
    for svc,data in list(svc_ev.items())[:3]:
        print(f"- {svc} (occurrences={data['occurrences']})")
        for ex in data.get("excerpts", []):
            print("  excerpt:", ex[:140])

    format_section("EVIDENCE - PILLARS (sample)")
    pil_ev = evidence.get("pillars", {})
    for pil,data in pil_ev.items():
        print(f"- {pil} (count={data['count']})")
        for ex in data.get("excerpts", [])[:2]:
            print("  excerpt:", ex[:140])

    format_section("EVIDENCE - PATTERNS")
    pat_ev = evidence.get("patterns", {})
    print(list(pat_ev.keys()))

    print("\nLegacy overview present:", 'architecture_overview_legacy' in sr)

if __name__ == "__main__":
    asyncio.run(main())
