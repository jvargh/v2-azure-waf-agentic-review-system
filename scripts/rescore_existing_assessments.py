"""
Script to rescore existing assessments with new transparent bottom-up scoring logic.

This script calls the /api/assessments/{aid}/rescore endpoint to update existing
assessments without requiring re-upload of architecture documents.

Usage:
    python scripts/rescore_existing_assessments.py <assessment_id>
    python scripts/rescore_existing_assessments.py --all  # Rescore all assessments
"""

import sys
import requests
import json
from typing import Optional


def rescore_assessment(assessment_id: str, base_url: str = "http://localhost:8000") -> bool:
    """Rescore a single assessment with new transparent scoring logic.
    
    Args:
        assessment_id: The ID of the assessment to rescore
        base_url: Base URL of the API server
        
    Returns:
        True if successful, False otherwise
    """
    url = f"{base_url}/api/assessments/{assessment_id}/rescore"
    
    try:
        print(f"Rescoring assessment: {assessment_id}")
        response = requests.post(url, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Successfully rescored: {assessment_id}")
            print(f"  Overall Score: {data.get('overall_architecture_score', 'N/A')}")
            
            # Show pillar scores with normalization info
            for pillar in data.get('pillar_results', []):
                pillar_name = pillar.get('pillar', 'Unknown')
                score = pillar.get('overall_score', 0)
                normalized = pillar.get('normalization_applied', False)
                raw_sum = pillar.get('raw_subcategory_sum', score)
                
                if normalized:
                    print(f"  {pillar_name}: {score}/100 (normalized from {raw_sum})")
                else:
                    print(f"  {pillar_name}: {score}/100")
            
            return True
        elif response.status_code == 404:
            print(f"✗ Assessment not found: {assessment_id}")
            return False
        elif response.status_code == 400:
            print(f"✗ Cannot rescore: {response.json().get('detail', 'Unknown error')}")
            return False
        else:
            print(f"✗ Error rescoring: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to API server at {base_url}")
        print("  Make sure the backend server is running")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ Timeout rescoring assessment {assessment_id}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def rescore_all_assessments(base_url: str = "http://localhost:8000") -> None:
    """Rescore all existing assessments.
    
    Args:
        base_url: Base URL of the API server
    """
    url = f"{base_url}/api/assessments/rescore-all"
    
    try:
        print("Rescoring all assessments...")
        response = requests.post(url, timeout=300)
        
        if response.status_code == 200:
            assessments = response.json()
            print(f"✓ Successfully rescored {len(assessments)} assessment(s)")
            
            for assessment in assessments:
                aid = assessment.get('id', 'Unknown')
                score = assessment.get('overall_architecture_score', 'N/A')
                print(f"  {aid}: {score}")
                
        else:
            print(f"✗ Error rescoring all: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to API server at {base_url}")
        print("  Make sure the backend server is running")
    except requests.exceptions.Timeout:
        print(f"✗ Timeout rescoring all assessments")
    except Exception as e:
        print(f"✗ Error: {e}")


def list_assessments(base_url: str = "http://localhost:8000") -> None:
    """List all available assessments.
    
    Args:
        base_url: Base URL of the API server
    """
    url = f"{base_url}/api/assessments"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            assessments = response.json()
            
            if not assessments:
                print("No assessments found")
                return
                
            print(f"Found {len(assessments)} assessment(s):")
            for assessment in assessments:
                aid = assessment.get('id', 'Unknown')
                status = assessment.get('status', 'Unknown')
                score = assessment.get('overall_architecture_score', 'N/A')
                created = assessment.get('created_at', 'Unknown')
                
                print(f"  {aid}")
                print(f"    Status: {status}")
                print(f"    Score: {score}")
                print(f"    Created: {created}")
                print()
        else:
            print(f"✗ Error listing assessments: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/rescore_existing_assessments.py <assessment_id>")
        print("  python scripts/rescore_existing_assessments.py --all")
        print("  python scripts/rescore_existing_assessments.py --list")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "--list":
        list_assessments()
    elif command == "--all":
        rescore_all_assessments()
    else:
        # Assume it's an assessment ID
        success = rescore_assessment(command)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
