from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)

def test_subcategory_human_fields_present():
    payload = {
        "name": "human-fields-assessment",
        "architecture_text": "This workload uses Azure Storage, Azure Key Vault, autoscaling policies, monitoring, logging, backup and networking.",
    }
    resp = client.post("/api/quick-assessment", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "pillar_results" in data and data["pillar_results"], "No pillar results returned"
    # Check first pillar's subcategory details
    first = data["pillar_results"][0]
    details = first.get("subcategory_details")
    assert details, "subcategory_details missing"
    for name, detail in details.items():
        assert "human_summary" in detail, f"human_summary missing for {name}"
        assert "expected_concepts" in detail, f"expected_concepts missing for {name}"
        assert "substantiated" in detail, f"substantiated missing for {name}"
        assert isinstance(detail["expected_concepts"], list), "expected_concepts not a list"
        assert isinstance(detail["substantiated"], bool), "substantiated not a bool"
        # human_summary may be None if logic failed, but should be str when present
        if detail["human_summary"] is not None:
            assert isinstance(detail["human_summary"], str)

if __name__ == "__main__":
    test_subcategory_human_fields_present()
    print("✅ human fields test passed")
