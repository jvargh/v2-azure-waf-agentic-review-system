"""
Migration script to apply scoring_breakdown and other new fields to existing assessments.
Calls the bulk rescore API endpoint.
"""
import requests
import sys
import os

# Suppress any module imports that might trigger server startup
os.environ.setdefault('SKIP_STARTUP', '1')

API_BASE = "http://localhost:8000"

def apply_breakdown():
    """Call bulk rescore endpoint to retroactively add new fields."""
    print("Applying scoring_breakdown and transparency fields to existing assessments...")
    print(f"Calling POST {API_BASE}/api/assessments/rescore-all\n")
    
    try:
        response = requests.post(f"{API_BASE}/api/assessments/rescore-all", timeout=300)
        response.raise_for_status()
        
        assessments = response.json()
        print(f"\n✓ Successfully rescored {len(assessments)} assessments")
        
        for assess in assessments:
            print(f"\n  Assessment: {assess.get('name', assess.get('id'))}")
            print(f"    Status: {assess.get('status')}")
            print(f"    Pillars: {len(assess.get('pillar_results', []))}")
            
            # Check if new fields are present
            pillars = assess.get('pillar_results', [])
            if pillars:
                sample = pillars[0]
                new_fields = []
                if sample.get('scoring_breakdown'):
                    new_fields.append('scoring_breakdown')
                if sample.get('simple_explanation'):
                    new_fields.append('simple_explanation')
                if sample.get('scoring_explanation'):
                    new_fields.append('scoring_explanation')
                if sample.get('domain_scores_raw'):
                    new_fields.append('domain_scores_raw')
                
                if new_fields:
                    print(f"    New fields present: {', '.join(new_fields)}")
        
        print(f"\n✓ Migration complete!")
        return 0
        
    except requests.exceptions.ConnectionError:
        print(f"\n✗ ERROR: Could not connect to API at {API_BASE}")
        print("  Make sure the backend server is running:")
        print("  cd backend && python -m uvicorn server:app --host 127.0.0.1 --port 8000")
        return 1
    except requests.exceptions.Timeout:
        print(f"\n✗ ERROR: Request timed out (>300s)")
        print("  Large number of assessments may require longer timeout")
        return 1
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ ERROR: HTTP {e.response.status_code}")
        print(f"  {e.response.text}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(apply_breakdown())
