from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)

ARCH_DOC = """Redundancy, failover, backup strategy with RTO 30 and RPO 15 documented. Multi-region deployment, health checks, monitoring, SLA 99.9. Chaos testing and fault injection performed quarterly. Active-active quorum design with self-healing runbooks.\n"""

def test_scoring_explanation_alignment():
    # Create assessment and upload doc
    resp = client.post('/api/assessments', json={'name': 'explain-test'})
    aid = resp.json()['id']
    files = [('files', ('arch.txt', ARCH_DOC, 'text/plain'))]
    up = client.post(f'/api/assessments/{aid}/documents', files=files)
    assert up.status_code == 200

    # Trigger analysis (background tasks won't run in TestClient for async jobs here) -> use rescore to force scoring path
    rs = client.post(f'/api/assessments/{aid}/rescore')
    assert rs.status_code == 200, rs.text
    data = rs.json()
    # Reliability result present
    reliability = next((p for p in data['pillar_results'] if p['pillar'] == 'Reliability'), None)
    assert reliability is not None
    expl = reliability.get('scoring_explanation')
    assert expl is not None
    # sums must match final score
    assert sum(reliability['subcategories'].values()) == reliability['overall_score']
    assert expl['subcategories_sum_final'] == reliability['overall_score']
    # uplift should be zero in rescore path
    assert expl['elevation_uplift'] == 0

if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
