"""
Generate a fresh assessment to demonstrate enriched business impact functionality.
This will create a new assessment with architecture that has clear reliability issues.
"""
import requests
import time
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:8000/api"

print("=" * 80)
print("FRESH ASSESSMENT GENERATOR - Testing Business Impact Enrichment")
print("=" * 80)

# Architecture with clear reliability gaps to trigger meaningful recommendations
arch_content = """
Azure Production Architecture - E-Commerce Platform

Infrastructure Overview:
- Single region deployment in East US
- No multi-region redundancy
- No availability zones configured
- Basic SKU resources throughout

Key Services:
- Azure Kubernetes Service (AKS): Single node pool, no autoscaling
- Azure SQL Database: Single instance, no failover groups
- Azure Cosmos DB: Single region, no geo-replication
- Azure Cache for Redis: Basic tier, no clustering
- Azure Service Bus: Standard tier, single namespace
- Azure Application Gateway: No WAF configured
- Azure Storage: LRS only, no geo-redundancy

Current Gaps:
- No disaster recovery plan documented
- No backup strategy implemented
- No automated failover mechanisms
- Manual scaling procedures only
- No health monitoring or alerting
- No chaos engineering or resilience testing
- No defined RTO/RPO targets
- No incident response procedures
"""

try:
    # Step 1: Create Assessment
    print("\n[1/5] Creating assessment...")
    resp = requests.post(f"{API_BASE}/assessments", json={
        "name": f"Fresh Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "description": "Testing enriched business impact generation"
    })
    resp.raise_for_status()
    assessment = resp.json()
    aid = assessment["id"]
    print(f"✓ Created assessment: {aid}")

    # Step 2: Upload Architecture Document
    print("\n[2/5] Uploading architecture document...")
    files = {"files": ("production_arch.txt", arch_content, "text/plain")}
    resp = requests.post(f"{API_BASE}/assessments/{aid}/documents", files=files)
    resp.raise_for_status()
    print("✓ Document uploaded")

    # Step 3: Start Analysis
    print("\n[3/5] Starting analysis...")
    resp = requests.post(f"{API_BASE}/assessments/{aid}/analyze")
    resp.raise_for_status()
    print("✓ Analysis started")

    # Step 4: Poll for Completion
    print("\n[4/5] Waiting for analysis to complete...")
    max_wait = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        time.sleep(5)
        resp = requests.get(f"{API_BASE}/assessments/{aid}")
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        progress = data.get("progress", 0)
        phase = data.get("current_phase", "Unknown")
        
        elapsed = int(time.time() - start_time)
        print(f"  [{elapsed}s] {status} - {progress}% - {phase}")
        
        if status == "completed":
            print("\n✓ Analysis complete!")
            
            # Step 5: Display Business Impact Results
            print("\n" + "=" * 80)
            print("[5/5] BUSINESS IMPACT ANALYSIS RESULTS")
            print("=" * 80)
            
            pillar_results = data.get("pillar_results", [])
            if not pillar_results:
                print("⚠ No pillar results found")
            else:
                total_recs = 0
                enriched_count = 0
                
                for pillar in pillar_results:
                    pillar_name = pillar.get("pillar_name", "Unknown")
                    recommendations = pillar.get("recommendations", [])
                    
                    if not recommendations:
                        continue
                    
                    print(f"\n{'─' * 80}")
                    print(f"Pillar: {pillar_name}")
                    print(f"{'─' * 80}")
                    
                    for idx, rec in enumerate(recommendations[:3], 1):  # Show first 3
                        total_recs += 1
                        title = rec.get("title", "N/A")
                        business_impact = rec.get("business_impact")
                        impact = rec.get("impact", "N/A")
                        priority = rec.get("priority", "N/A")
                        
                        # Check if business_impact is enriched (not generic)
                        is_enriched = (
                            business_impact and 
                            len(business_impact) >= 40 and
                            not business_impact.lower().startswith(("high impact", "medium impact", "low impact"))
                        )
                        
                        if is_enriched:
                            enriched_count += 1
                            status_icon = "✓"
                        else:
                            status_icon = "✗"
                        
                        print(f"\n{status_icon} Recommendation #{idx} (Priority: {priority})")
                        print(f"  Title: {title}")
                        print(f"  Business Impact: {business_impact or impact}")
                        if not is_enriched:
                            print(f"    ⚠ Generic/Short - Expected enriched impact")
                
                print(f"\n{'=' * 80}")
                print(f"SUMMARY: {enriched_count}/{total_recs} recommendations have enriched business impact")
                print(f"{'=' * 80}")
                
                if enriched_count > 0:
                    print(f"\n✓ SUCCESS: Business impact enrichment is working!")
                    print(f"  {enriched_count} recommendations have detailed, metric-driven business impact statements")
                else:
                    print(f"\n✗ ISSUE: No enriched business impacts found")
                    print(f"  All {total_recs} recommendations still have generic impacts")
                    print(f"  Check backend logs for [RICH_IMPACT] and [ENRICH_IMPACT] messages")
            
            print(f"\n{'=' * 80}")
            print(f"View full assessment at: http://localhost:5173")
            print(f"Assessment ID: {aid}")
            print(f"{'=' * 80}\n")
            break
            
        elif status == "failed":
            print("\n✗ Analysis failed!")
            error = data.get("error_message", "Unknown error")
            print(f"Error: {error}")
            break
    else:
        print(f"\n⚠ Timeout after {max_wait}s - analysis still running")
        print(f"Check status at: http://localhost:5173")

except requests.exceptions.ConnectionError:
    print("\n✗ ERROR: Could not connect to backend server")
    print("Make sure the backend is running on http://127.0.0.1:8000")
except Exception as e:
    print(f"\n✗ ERROR: {e}")
