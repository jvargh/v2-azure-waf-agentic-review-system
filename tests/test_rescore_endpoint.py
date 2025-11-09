from fastapi.testclient import TestClient
import datetime as dt

from backend.server import app, ASSESSMENTS

client = TestClient(app)

ARCH_DOC = """Highly available multi-region architecture.
We implement redundancy, failover, backup, disaster recovery with defined RTO 30 minutes and RPO 15 minutes.
Security layers: encryption at rest and in transit, authentication via Azure AD, authorization with RBAC, key vault secrets rotated.
Cost governance includes budget monitoring, optimization, reserved instance planning, rightsizing and anomaly detection with FinOps processes.
Operational excellence: monitoring, logging, automation runbook, CI/CD pipeline, alerting, documentation, testing and blue-green canary deployments.
Performance tuning: latency targets p95 < 220ms, throughput 1500 rps, scalability via autoscaling, cache, cdn, load balancing and query optimization with indexing.
"""

def test_rescore_endpoint_basic():
    # Create assessment
    resp = client.post("/api/assessments", json={"name": "rescore-test"})
    assert resp.status_code == 200
    aid = resp.json()["id"]

    # Upload architecture document
    files = [("files", ("arch.txt", ARCH_DOC, "text/plain"))]
    up_resp = client.post(f"/api/assessments/{aid}/documents", files=files)
    assert up_resp.status_code == 200
    assert len(up_resp.json()) == 1

    # Perform rescore (without full analysis lifecycle)
    rs_resp = client.post(f"/api/assessments/{aid}/rescore")
    assert rs_resp.status_code == 200, rs_resp.text
    data = rs_resp.json()

    # Basic assertions
    assert data["overall_architecture_score"] is not None
    assert data["overall_architecture_score"] > 0
    assert len(data["pillar_results"]) == 5
    # score history should contain one snapshot (pre-rescore state)
    assert len(data.get("score_history", [])) == 1
    # Each pillar should have confidence field
    for pr in data["pillar_results"]:
        assert "confidence" in pr
        assert pr["overall_score"] >= 0

    # Ensure persistence updated in in-memory store
    stored = ASSESSMENTS.get(aid)
    assert stored is not None
    assert "score_history" in stored
    assert len(stored["score_history"]) == 1
