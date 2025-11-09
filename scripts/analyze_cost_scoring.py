"""
Deep dive into Cost Optimization scoring differences with support cases.
"""
import requests
import json

API_BASE = "http://localhost:8000"

def analyze_cost_optimization():
    # Get both assessments
    with_cases = requests.get(f"{API_BASE}/api/assessments/assess_1762503071").json()
    without_cases = requests.get(f"{API_BASE}/api/assessments/assess_1762505883").json()
    
    cost_with = [p for p in with_cases['pillar_results'] if p['pillar'] == 'Cost Optimization'][0]
    cost_without = [p for p in without_cases['pillar_results'] if p['pillar'] == 'Cost Optimization'][0]
    
    print("="*80)
    print("COST OPTIMIZATION DEEP DIVE")
    print("="*80)
    
    print(f"\nWITH Support Cases: {cost_with['overall_score']}")
    print(f"WITHOUT Support Cases: {cost_without['overall_score']}")
    print(f"DIFFERENCE: {cost_with['overall_score'] - cost_without['overall_score']}")
    
    # Breakdown comparison
    bd_with = cost_with.get('scoring_breakdown', {})
    bd_without = cost_without.get('scoring_breakdown', {})
    
    print("\n" + "="*80)
    print("SCORING STEPS COMPARISON")
    print("="*80)
    
    print("\nWITH Support Cases:")
    for step in bd_with.get('steps', []):
        print(f"  {step['step']}: {step.get('before', 'N/A')} → {step['after']}")
        if 'reason' in step:
            print(f"    Reason: {step['reason']}")
        if 'negative_mentions' in step:
            print(f"    Negative mentions: {step['negative_mentions']}")
        if 'missing_critical' in step:
            print(f"    Missing critical: {step['missing_critical']}")
    
    print("\nWITHOUT Support Cases:")
    for step in bd_without.get('steps', []):
        print(f"  {step['step']}: {step.get('before', 'N/A')} → {step['after']}")
        if 'reason' in step:
            print(f"    Reason: {step['reason']}")
        if 'negative_mentions' in step:
            print(f"    Negative mentions: {step['negative_mentions']}")
        if 'missing_critical' in step:
            print(f"    Missing critical: {step['missing_critical']}")
    
    # Check for negative mentions in simple explanation
    simple_with = cost_with.get('simple_explanation', {})
    simple_without = cost_without.get('simple_explanation', {})
    
    print("\n" + "="*80)
    print("GAPS ASSESSMENT")
    print("="*80)
    
    print("\nWITH Support Cases:")
    print(f"  {simple_with.get('gaps_assessment', 'N/A')}")
    
    print("\nWITHOUT Support Cases:")
    print(f"  {simple_without.get('gaps_assessment', 'N/A')}")
    
    # Recommendations comparison
    print("\n" + "="*80)
    print("TOP RECOMMENDATIONS")
    print("="*80)
    
    print("\nWITH Support Cases:")
    for i, rec in enumerate(cost_with['recommendations'][:3], 1):
        print(f"  {i}. {rec['title']}")
        print(f"     Priority: {rec['priority']}")
    
    print("\nWITHOUT Support Cases:")
    for i, rec in enumerate(cost_without['recommendations'][:3], 1):
        print(f"  {i}. {rec['title']}")
        print(f"     Priority: {rec['priority']}")
    
    # Check raw components
    print("\n" + "="*80)
    print("RAW COMPONENTS")
    print("="*80)
    
    print("\nWITH Support Cases:")
    raw_with = bd_with.get('raw_components', {})
    print(f"  Critical score: {raw_with.get('critical_score', 'N/A')}")
    print(f"  Important score: {raw_with.get('important_score', 'N/A')}")
    print(f"  Nice-to-have score: {raw_with.get('nice_score', 'N/A')}")
    
    print("\nWITHOUT Support Cases:")
    raw_without = bd_without.get('raw_components', {})
    print(f"  Critical score: {raw_without.get('critical_score', 'N/A')}")
    print(f"  Important score: {raw_without.get('important_score', 'N/A')}")
    print(f"  Nice-to-have score: {raw_without.get('nice_score', 'N/A')}")

if __name__ == "__main__":
    analyze_cost_optimization()
