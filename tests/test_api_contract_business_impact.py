import json
import re
import os
import http.client
import pytest

API_HOST = os.getenv('API_HOST', '127.0.0.1')
API_PORT = int(os.getenv('API_PORT', '8000'))
GENERIC_PATTERN = re.compile(r'^(high|medium|low) impact on ', re.IGNORECASE)


def _get(path: str):
    """Return (status, data) or (None, b'') if server unreachable."""
    try:
        conn = http.client.HTTPConnection(API_HOST, API_PORT, timeout=3)
        conn.request('GET', path)
        resp = conn.getresponse()
        data = resp.read()
        conn.close()
        return resp.status, data
    except OSError:
        return None, b''


def test_recommendations_have_enriched_business_impact():
    status, data = _get('/api/assessments')
    if status is None:
        pytest.skip('API server not running; skipping business impact contract test')
    assert status == 200, f'Expected 200 from list assessments, got {status}'
    assessments = json.loads(data.decode('utf-8'))
    if not assessments:
        # Skip if no assessments created yet
        return
    # Just check first completed one
    target = None
    for a in assessments:
        if a.get('status') == 'completed' and a.get('pillar_results'):
            target = a
            break
    if not target:
        # No completed assessment yet
        return
    rec_count = 0
    failures = []
    for pillar in target.get('pillar_results', []):
        for rec in pillar.get('recommendations', []):
            rec_count += 1
            bi = rec.get('business_impact') or rec.get('impact') or ''
            # Validate enriched length threshold
            if len(bi) < 40:
                failures.append(f"Too short: '{bi}'")
            if GENERIC_PATTERN.match(bi.lower()):
                failures.append(f"Generic phrasing: '{bi}'")
    # Only assert if we actually had recommendations
    if rec_count > 0 and failures:
        assert False, 'Business impact enrichment failures:\n' + '\n'.join(failures)
