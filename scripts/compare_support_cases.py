"""
Compare assessments with and without support case integration to determine value-add.
"""
import requests
import json

API_BASE = "http://localhost:8000"

def compare_assessments():
    """Compare two assessments: one with support cases, one without."""
    
    # Get assessment WITH support cases
    with_cases_id = "assess_1762503071"
    without_cases_id = "assess_1762505883"
    
    print("\nFetching assessments...")
    with_cases = requests.get(f"{API_BASE}/api/assessments/{with_cases_id}").json()
    without_cases = requests.get(f"{API_BASE}/api/assessments/{without_cases_id}").json()
    
    print(f"\n{'='*80}")
    print(f"WITH Support Cases: {with_cases['name']}")
    print(f"{'='*80}")
    for p in with_cases['pillar_results']:
        breakdown = p.get('scoring_breakdown', {})
        simple = p.get('simple_explanation', {})
        print(f"\n{p['pillar']}:")
        print(f"  Score: {p['overall_score']}")
        print(f"  Confidence: {p['confidence']}")
        print(f"  Score Source: {p['score_source']}")
        print(f"  Coverage: {breakdown.get('final', {}).get('coverage_pct', 'N/A')}%")
        print(f"  Critical Found: {len(breakdown.get('concepts', {}).get('critical_found', []))}")
        print(f"  Critical Missing: {len(breakdown.get('concepts', {}).get('critical_missing', []))}")
        if simple.get('summary'):
            print(f"  Summary: {simple['summary'][:100]}...")
    
    print(f"\n{'='*80}")
    print(f"WITHOUT Support Cases: {without_cases['name']}")
    print(f"{'='*80}")
    for p in without_cases['pillar_results']:
        breakdown = p.get('scoring_breakdown', {})
        simple = p.get('simple_explanation', {})
        print(f"\n{p['pillar']}:")
        print(f"  Score: {p['overall_score']}")
        print(f"  Confidence: {p['confidence']}")
        print(f"  Score Source: {p['score_source']}")
        print(f"  Coverage: {breakdown.get('final', {}).get('coverage_pct', 'N/A')}%")
        print(f"  Critical Found: {len(breakdown.get('concepts', {}).get('critical_found', []))}")
        print(f"  Critical Missing: {len(breakdown.get('concepts', {}).get('critical_missing', []))}")
        if simple.get('summary'):
            print(f"  Summary: {simple['summary'][:100]}...")
    
    # Calculate differences
    print(f"\n{'='*80}")
    print("SCORE DIFFERENCES (WITH - WITHOUT)")
    print(f"{'='*80}")
    for i, p_with in enumerate(with_cases['pillar_results']):
        p_without = without_cases['pillar_results'][i]
        score_diff = p_with['overall_score'] - p_without['overall_score']
        
        bd_with = p_with.get('scoring_breakdown', {})
        bd_without = p_without.get('scoring_breakdown', {})
        
        cov_with = bd_with.get('final', {}).get('coverage_pct', 0)
        cov_without = bd_without.get('final', {}).get('coverage_pct', 0)
        cov_diff = cov_with - cov_without
        
        crit_with = len(bd_with.get('concepts', {}).get('critical_found', []))
        crit_without = len(bd_without.get('concepts', {}).get('critical_found', []))
        crit_diff = crit_with - crit_without
        
        print(f"\n{p_with['pillar']}:")
        print(f"  Score Δ: {score_diff:+.1f}")
        print(f"  Coverage Δ: {cov_diff:+.1f}%")
        print(f"  Critical Concepts Δ: {crit_diff:+d}")
        
        if score_diff != 0:
            print(f"  → Support cases {'IMPROVED' if score_diff > 0 else 'DECREASED'} score by {abs(score_diff):.1f} points")

if __name__ == "__main__":
    compare_assessments()
