"""(Relocated) Strict scoring separation validation script."""
import os, sys
sys.path.append(os.getcwd())
from backend.server import _calculate_conservative_score

SAMPLES = [
    ("excellent_architecture.txt", "Excellent"),
    ("low_rating_architecture_document.txt", "LowRated")
]
PILLARS = [
    ("reliability", "Reliability"),
    ("security", "Security"),
    ("cost", "Cost Optimization"),
    ("operational", "Operational Excellence"),
    ("performance", "Performance Efficiency"),
]
base = os.path.join(os.getcwd(), "sample_data")

results = {}
for fname, label in SAMPLES:
    path = os.path.join(base, fname)
    if not os.path.isfile(path):
        print(f"[MISS] {path} not found")
        continue
    corpus = open(path, 'r', encoding='utf-8').read()
    pillar_scores = []
    for code, pname in PILLARS:
        score, confidence, subcats, source, coverage, gaps, breakdown = _calculate_conservative_score(corpus, code, pname)
        pillar_scores.append({
            'pillar': pname,
            'score': score,
            'confidence': confidence,
            'source': source,
            'coverage': coverage,
            'gaps': gaps,
            'critical_found': len(breakdown.get('concepts', {}).get('critical', {}).get('found', [])),
            'critical_missing': len(breakdown.get('concepts', {}).get('critical', {}).get('missing', []))
        })
    results[label] = pillar_scores

for label, rows in results.items():
    print(f"\n=== {label} Architecture ===")
    for r in rows:
        print(f"{r['pillar']:<24} score={r['score']:>3} src={r['source']:<8} cov={r['coverage']:>5.1f}% gaps={r['gaps']:<2} conf={r['confidence']}")

if all(k in results for k in ['Excellent','LowRated']):
    print("\n=== Separation Delta (Excellent - LowRated) ===")
    for i, (code, pname) in enumerate(PILLARS):
        ex = results['Excellent'][i]['score']
        lo = results['LowRated'][i]['score']
        print(f"{pname:<24} delta={ex-lo:+4}")
