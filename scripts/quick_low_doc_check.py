"""Quick gating verification for low-rating architecture document.
Prints which cross-cutting sections appear (should omit cost/compliance if no evidence).

Adds repository root to sys.path for direct execution.
"""
import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.analysis.document_analyzer import DocumentAnalyzer

async def main():
    p = Path("sample_data/low_rating_architecture_document.txt")
    if not p.exists():
        print("Missing sample file:", p)
        return
    text = p.read_text(encoding="utf-8")
    analyzer = DocumentAnalyzer(llm_enabled=False)
    result = await analyzer.analyze_architecture_document(text, p.name)
    sr = result.get("structured_report", {})
    keys = list(sr.get("cross_cutting_concerns", {}).keys())
    print("CROSS_CUTTING_KEYS:", keys)
    print("HAS_COST_OPTIMIZATION:", "cost_optimization" in keys)
    print("HAS_COMPLIANCE_GOVERNANCE:", "compliance_governance" in keys)
    print("EXEC_SUMMARY_FIRST_160:", sr.get("executive_summary", "")[:160])

if __name__ == "__main__":
    asyncio.run(main())
