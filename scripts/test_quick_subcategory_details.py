"""In-process validation of /api/quick-assessment returning subcategory_details.

Run:  python scripts/test_quick_subcategory_details.py
Prints summary confirming concept coverage fields populated.
"""

from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.getcwd())  # ensure local package import
from backend.server import app
import json

payload = {
    "name": "Demo Assessment",
    "architecture_text": (
        "Our Azure architecture uses AKS with multi-zone nodes, Key Vault for secrets, "
        "Front Door for global routing, Cosmos DB for data, and Azure Monitor with alerts. "
        "Backups implemented weekly but disaster recovery runbooks incomplete. Identity via Entra ID with Conditional Access partially configured. "
        "CI/CD pipelines deploy infrastructure as code. Autoscale policies set but performance tests are ad-hoc."
    ),
    "support_cases_csv": ""
}

client = TestClient(app)

resp = client.post("/api/quick-assessment", json=payload)
print("HTTP", resp.status_code)
data = resp.json()
print("Keys:", list(data.keys()))
pillars = data.get("pillar_results", [])
print("Pillars returned:", len(pillars))
for p in pillars:
    name = p.get("pillar")
    sub_details = p.get("subcategory_details")
    if sub_details:
        any_detail = next(iter(sub_details.values())) if isinstance(sub_details, dict) else None
        found_total = sum(len(d.get("found_concepts", []) or d.get("evidence_found", [])) for d in sub_details.values())
        missing_total = sum(len(d.get("missing_concepts", [])) for d in sub_details.values())
        print(f" - {name}: subcategories={len(sub_details)} found_total={found_total} missing_total={missing_total}")
        if any_detail:
            print("   Sample justification:", (any_detail.get("justification_text") or "<none>")[:140])
    else:
        print(f" - {name}: NO subcategory_details present")

# Write full JSON for manual inspection if needed
with open("quick_assessment_output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("Saved full response to quick_assessment_output.json")
