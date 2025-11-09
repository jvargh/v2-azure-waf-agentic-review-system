"""Test script for validating structured report enhancements.

Tests three artifact types:
1. Architecture document - should produce executive_summary, architecture_overview, 
   cross_cutting_concerns (dimensional), deployment_summary
2. Architecture diagram - same structure
3. Support case CSV - includes support_case_concerns with root cause analysis
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def create_test_assessment():
    """Create a new test assessment."""
    response = requests.post(f"{BASE_URL}/api/assessments", json={
        "name": "Structured Report Test",
        "description": "Testing enhanced structured analysis reports"
    })
    response.raise_for_status()
    assessment = response.json()
    print(f"✓ Created assessment: {assessment['id']}")
    return assessment["id"]

def upload_test_documents(assessment_id):
    """Upload test artifacts."""
    # Architecture document
    arch_doc_content = """
    Azure Architecture Document
    
    This workload uses the following Azure services:
    - Azure App Service for hosting web frontend
    - Azure SQL Database for transactional data
    - Azure Storage Account for blob storage
    - Azure Key Vault for secrets management
    - Azure Application Gateway with WAF
    - Azure Monitor for observability
    
    The architecture follows a multi-tier pattern with:
    - Frontend tier: React SPA hosted on App Service
    - API tier: .NET Core APIs on App Service
    - Data tier: Azure SQL with geo-replication
    
    Security considerations:
    - All traffic encrypted with TLS 1.2+
    - Managed identities for service-to-service auth
    - WAF rules enabled for OWASP Top 10
    
    Scalability approach:
    - App Service configured for auto-scaling (2-10 instances)
    - SQL Database uses Premium tier with read replicas
    
    Availability:
    - Multi-region deployment with Traffic Manager
    - 99.95% SLA target
    
    Deployment:
    - Infrastructure as Code using Bicep templates
    - CI/CD pipeline via Azure DevOps
    - Blue-green deployment strategy
    """
    
    # Support cases CSV
    csv_content = """ticketnumber,title,createdon,msdfm_productname,msdfm_rootcausedescription,msdfm_customerstatement,msdfm_resolution,msdfm_fullpath
123,Auth timeout,2024-01-15,Azure AD,Token timeout due to network latency,Users cannot login,Increased token lifetime to 60s,Security>Identity
124,SQL slowness,2024-01-16,SQL Database,Missing index on Orders table,Query times over 5s,Added clustered index,Performance>Database
125,Storage unavailable,2024-01-17,Storage Account,Region outage,Cannot access blobs,Failed over to secondary region,Reliability>Storage
126,App crash,2024-01-18,App Service,Memory leak in worker process,Site returns 503,Restarted workers and added monitoring,Operational>Compute
127,High costs,2024-01-19,Cost Management,Over-provisioned VMs,Bill doubled,Rightsized VM SKUs,Cost>Compute
128,Login failure,2024-01-20,Azure AD,MFA configuration error,MFA prompts fail,Reconfigured MFA policy,Security>Identity
129,Slow API,2024-01-21,App Service,Cold start latency,First request takes 10s,Enabled Always On,Performance>Compute
130,DB connection timeout,2024-01-22,SQL Database,Connection pool exhausted,Intermittent timeouts,Increased max connections,Reliability>Database"""
    
    files = [
        ("files", ("architecture.txt", arch_doc_content, "text/plain")),
        ("files", ("support_cases.csv", csv_content, "text/csv"))
    ]
    
    response = requests.post(f"{BASE_URL}/api/assessments/{assessment_id}/documents", files=files)
    response.raise_for_status()
    documents = response.json()
    print(f"✓ Uploaded {len(documents)} documents")
    return documents

def validate_structured_report(doc, expected_type):
    """Validate structured report sections."""
    print(f"\n--- Validating {doc['filename']} (category: {doc['category']}) ---")
    
    if "structured_report" not in doc:
        print(f"✗ FAIL: No structured_report field found")
        return False
    
    report = doc["structured_report"]
    if not report:
        print(f"✗ FAIL: structured_report is None")
        return False
    
    print(f"✓ structured_report field present")
    
    # Check executive summary
    if "executive_summary" in report:
        exec_summary = report["executive_summary"]
        print(f"✓ Executive Summary: {exec_summary[:100]}...")
    else:
        print(f"✗ MISSING: executive_summary")
    
    # Check architecture overview (or support_case_concerns for CSV)
    if expected_type == "case":
        if "support_case_concerns" in report:
            concerns = report["support_case_concerns"]
            print(f"✓ Support Case Concerns: {len(concerns)} chars")
            if "root_cause" in concerns.lower() or "resolution" in concerns.lower():
                print(f"  ✓ Contains root cause/resolution analysis")
        else:
            print(f"✗ MISSING: support_case_concerns")
    else:
        if "architecture_overview" in report:
            overview = report["architecture_overview"]
            print(f"✓ Architecture Overview: {len(overview)} chars")
        else:
            print(f"✗ MISSING: architecture_overview")
    
    # Check cross-cutting concerns (dimensional)
    if "cross_cutting_concerns" in report:
        concerns = report["cross_cutting_concerns"]
        print(f"✓ Cross-Cutting Concerns (dimensional):")
        for dimension in ["security", "scalability", "availability", "observability"]:
            if dimension in concerns:
                print(f"  ✓ {dimension}: {concerns[dimension][:60]}...")
            else:
                print(f"  ✗ MISSING dimension: {dimension}")
    else:
        print(f"✗ MISSING: cross_cutting_concerns")
    
    # Check deployment summary
    if "deployment_summary" in report:
        deployment = report["deployment_summary"]
        print(f"✓ Deployment Summary: {deployment[:100]}...")
    else:
        print(f"✗ MISSING: deployment_summary")
    
    # Check for root cause analysis in CSV
    if expected_type == "case" and "analysis_metadata" in doc:
        metadata = doc.get("analysis_metadata", {})
        if "root_cause_analysis" in metadata:
            rca = metadata["root_cause_analysis"]
            print(f"✓ Root Cause Analysis in metadata:")
            print(f"  - Root causes found: {rca.get('root_cause_count', 0)}")
            print(f"  - Resolutions found: {rca.get('resolution_count', 0)}")
            print(f"  - Resolution quality: {rca.get('resolution_quality', 'unknown')}")
            print(f"  - Unresolved gaps: {rca.get('unresolved_gaps', 0)}")
            if rca.get("top_root_causes"):
                print(f"  - Top recurring patterns: {rca['top_root_causes'][:3]}")
        else:
            print(f"✗ MISSING: root_cause_analysis in analysis_metadata")
    
    return True

def test_orchestrator_corpus(assessment_id):
    """Start analysis and check unified corpus generation."""
    print("\n--- Starting Analysis to Test Orchestrator ---")
    response = requests.post(f"{BASE_URL}/api/assessments/{assessment_id}/analyze")
    response.raise_for_status()
    print(f"✓ Analysis started")
    
    # Poll until completed
    for i in range(60):
        time.sleep(2)
        response = requests.get(f"{BASE_URL}/api/assessments/{assessment_id}")
        assessment = response.json()
        status = assessment["status"]
        progress = assessment.get("progress", 0)
        print(f"  Status: {status}, Progress: {progress}%")
        
        if status == "completed":
            print(f"✓ Analysis completed")
            
            # Check unified corpus
            if "unified_corpus" in assessment and assessment["unified_corpus"]:
                corpus = assessment["unified_corpus"]
                print(f"\n--- Unified Corpus Analysis ---")
                print(f"Total corpus length: {len(corpus)} chars")
                
                # Estimate tokens (words * 1.3)
                estimated_tokens = int(len(corpus.split()) * 1.3)
                print(f"Estimated tokens: {estimated_tokens}")
                
                if estimated_tokens > 15000:
                    print(f"⚠ WARNING: Corpus exceeds 15K tokens (target ~12K)")
                else:
                    print(f"✓ Corpus within reasonable token budget")
                
                # Check for structured sections
                sections = [
                    "EXECUTIVE SUMMARY",
                    "ARCHITECTURE OVERVIEW",
                    "CROSS-CUTTING CONCERNS",
                    "DEPLOYMENT SUMMARY",
                    "SUPPORT CASE CONCERNS"
                ]
                
                for section in sections:
                    if section in corpus:
                        print(f"✓ Found section: {section}")
                    else:
                        print(f"✗ MISSING section: {section}")
                
                # Check for aggregated summary
                if "AGGREGATED ASSESSMENT EXECUTIVE SUMMARY" in corpus:
                    print(f"✓ Found aggregated assessment-level summary")
                else:
                    print(f"ℹ No aggregated summary (may be single document)")
                
                # Check dimensional cross-cutting concerns
                dimensions = ["Security", "Scalability", "Availability", "Observability"]
                for dim in dimensions:
                    if dim in corpus:
                        print(f"✓ Found dimensional concern: {dim}")
            else:
                print(f"✗ No unified_corpus found in assessment")
            
            return True
        
        if status == "failed":
            print(f"✗ FAIL: Analysis failed")
            return False
    
    print(f"✗ TIMEOUT: Analysis did not complete in 120s")
    return False

def main():
    """Run structured report validation tests."""
    print("=== Structured Report Validation Test ===\n")
    
    try:
        # Create assessment
        assessment_id = create_test_assessment()
        
        # Upload documents
        documents = upload_test_documents(assessment_id)
        
        # Validate each document's structured report
        print("\n=== Document-Level Structured Reports ===")
        for doc in documents:
            expected_type = doc["category"]
            validate_structured_report(doc, expected_type)
        
        # Test orchestrator corpus generation
        test_orchestrator_corpus(assessment_id)
        
        print("\n=== Test Complete ===")
        print(f"Assessment ID: {assessment_id}")
        print(f"View in UI: http://localhost:3000 (or your frontend port)")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
