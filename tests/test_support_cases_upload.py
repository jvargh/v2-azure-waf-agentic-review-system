"""Test uploading support case CSV via API and enrichment fields population.

Validates that the /api/assessments/{aid}/documents endpoint correctly
extracts thematic patterns, risk signals, total case count, and builds
support_cases_summary plus structured_report metadata for case artifacts.
"""

from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)

SAMPLE_CSV = """id,title,severity,description
1,High CPU on App Service,high,Intermittent high CPU spikes under load
2,Slow SQL Query,medium,Long-running query causes latency
3,Storage Throttling,high,Requests exceeding provisioned IOPS
4,Missing Backups,high,No backup policy configured for critical DB
5,Unencrypted Traffic,medium,Legacy component still uses HTTP
"""


def test_support_case_upload_enrichment():
    # Create assessment
    r = client.post('/api/assessments', json={'name': 'cases-enrichment'})
    assert r.status_code == 200, r.text
    aid = r.json()['id']

    # Upload support cases CSV
    files = [('files', ('support_cases.csv', SAMPLE_CSV, 'text/csv'))]
    r2 = client.post(f'/api/assessments/{aid}/documents', files=files)
    assert r2.status_code == 200, r2.text
    docs = r2.json()
    assert len(docs) == 1
    doc = docs[0]
    assert doc['category'] == 'case'

    # Enrichment fields
    assert 'support_cases_summary' in doc, 'support_cases_summary missing'
    assert doc.get('support_cases_summary'), 'support_cases_summary empty'
    assert 'total_cases' in doc, 'total_cases missing'
    assert isinstance(doc.get('total_cases'), int), 'total_cases not int'
    # risk_signals and thematic_patterns may vary but should exist (non-failing if empty)
    assert 'risk_signals' in doc, 'risk_signals field missing'
    assert 'thematic_patterns' in doc, 'thematic_patterns field missing'

    # Metadata should contain structured_report and total_cases provenance
    meta = doc.get('analysis_metadata') or {}
    assert 'structured_report' in meta, 'structured_report missing in analysis_metadata'
    structured = meta.get('structured_report') or {}
    # New sample arrays
    assert 'root_cause_samples' in structured, 'root_cause_samples missing in structured_report'
    assert 'resolution_samples' in structured, 'resolution_samples missing in structured_report'
    # Arrays may be empty if CSV lacks those columns, but should exist
    assert isinstance(structured.get('root_cause_samples'), list), 'root_cause_samples not a list'
    assert isinstance(structured.get('resolution_samples'), list), 'resolution_samples not a list'
    # Summary should include Total cases line
    assert 'Total cases:' in doc.get('support_cases_summary', ''), 'Total cases line missing from summary'

if __name__ == '__main__':  # pragma: no cover
    test_support_case_upload_enrichment()
    print('✅ Support case upload enrichment test passed')
