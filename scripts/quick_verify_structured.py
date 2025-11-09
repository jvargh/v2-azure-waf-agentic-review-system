"""Quick verification of structured report functionality by inspecting code logic."""

import sys
sys.path.insert(0, "c:\\_Projects\\MAF\\wara\\azure-well-architected-agents")

from backend.app.analysis.document_analyzer import DocumentAnalyzer

# Check if methods exist
analyzer = DocumentAnalyzer(llm_enabled=False)

# Verify helper methods exist
helpers = [
    "_compose_structured_arch_doc_report",
    "_compose_structured_diagram_report",
    "_compose_structured_case_concerns_report",
    "_extract_root_cause_patterns",
    "_dimensional_concern_summary",
    "_infer_diagram_concern",
    "_case_dimensional_concern"
]

print("=== Verifying DocumentAnalyzer Helper Methods ===\n")
for helper in helpers:
    if hasattr(analyzer, helper):
        print(f"✓ {helper} exists")
    else:
        print(f"✗ {helper} MISSING")

# Test simple arch doc analysis (without LLM)
print("\n=== Testing Architecture Document Analysis ===")
test_doc = """
Azure App Service with SQL Database.
Security: Uses Azure Key Vault.
Scalability: Auto-scaling enabled.
Availability: Multi-region deployment.
"""

try:
    import asyncio
    result = asyncio.run(analyzer.analyze_architecture_document(test_doc, "test.txt"))
    
    print(f"✓ analyze_architecture_document executed")
    
    if "structured_report" in result:
        print(f"✓ structured_report key present")
        report = result["structured_report"]
        
        sections = ["executive_summary", "architecture_overview", "cross_cutting_concerns", "deployment_summary"]
        for section in sections:
            if section in report:
                print(f"  ✓ {section}")
                if section == "cross_cutting_concerns":
                    for dim in ["security", "scalability", "availability", "observability"]:
                        if dim in report[section]:
                            print(f"    ✓ {dim} dimension")
            else:
                print(f"  ✗ {section} MISSING")
    else:
        print(f"✗ structured_report key NOT FOUND")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test CSV analysis
print("\n=== Testing Support Case CSV Analysis ===")
test_csv = """ticketnumber,msdfm_rootcausedescription,msdfm_resolution
1,Config error caused timeout,Updated configuration
2,Network latency issue,Added CDN
3,Auth failure due to MFA,Fixed MFA policy"""

try:
    result2 = asyncio.run(analyzer.analyze_support_cases(test_csv, "cases.csv"))
    
    print(f"✓ analyze_support_cases executed")
    
    if "structured_report" in result2:
        print(f"✓ structured_report key present")
        report2 = result2["structured_report"]
        
        if "support_case_concerns" in report2:
            print(f"  ✓ support_case_concerns section")
        if "cross_cutting_concerns" in report2:
            print(f"  ✓ cross_cutting_concerns (dimensional)")
    else:
        print(f"✗ structured_report key NOT FOUND")
    
    if "root_cause_analysis" in result2:
        print(f"✓ root_cause_analysis key present")
        rca = result2["root_cause_analysis"]
        print(f"  Root causes: {rca.get('root_cause_count', 0)}")
        print(f"  Resolutions: {rca.get('resolution_count', 0)}")
        print(f"  Quality: {rca.get('resolution_quality', 'unknown')}")
    else:
        print(f"✗ root_cause_analysis key NOT FOUND")
        
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Verification Complete ===")
