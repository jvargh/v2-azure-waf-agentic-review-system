from fastapi.testclient import TestClient
from backend.server import app, NO_EVIDENCE_SUBCATEGORY_FLOOR

client = TestClient(app)

def test_curated_expected_concepts_and_floor_applied():
    arch_text = (
        "This system implements failover and backup with multi-region deployment and monitoring. "
        "It includes autoscale and health probes but lacks chaos engineering and formal DR drills."
    )
    payload = {"name": "curated-concepts-test", "architecture_text": arch_text}
    resp = client.post("/api/quick-assessment", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    pillar_results = data.get("pillar_results") or []
    reliability = next((p for p in pillar_results if p["pillar"].lower() == "reliability"), None)
    assert reliability, "Reliability pillar missing"
    details = reliability.get("subcategory_details") or {}
    assert details, "No subcategory details present"
    # All reliability subcategories should have non-empty curated expected concepts
    for d in details.values():
        expected = d.get("expected_concepts") or []
        assert expected, f"Curated expected concepts missing for {d['name']}"
        found = set(d.get("evidence_found") or [])
        missing = set(d.get("missing_concepts") or [])
        # Found and missing concepts must be subsets of expected_concepts
        assert found.issubset(set(expected)), f"Found concepts not subset of curated expected for {d['name']}"
        assert missing.issubset(set(expected)), f"Missing concepts not subset of curated expected for {d['name']}"
    # Ensure at least one zero-evidence subcategory to exercise floor & recommendation generation
    zero_evidence = [d for d in details.values() if not d.get("evidence_found")]
    assert zero_evidence, "Expected at least one zero-evidence subcategory for test"
    for d in zero_evidence:
        assert d.get("final_score") <= NO_EVIDENCE_SUBCATEGORY_FLOOR, f"Evidence floor not applied for {d['name']}"
        recs = reliability.get("recommendations") or []
        assert any(r.get("source") == d['name'] for r in recs), f"Missing targeted recommendation for zero-evidence subcategory {d['name']}"

if __name__ == "__main__":
    test_curated_expected_concepts_and_floor_applied()
    print("✅ Curated expected concepts & floor test passed")
