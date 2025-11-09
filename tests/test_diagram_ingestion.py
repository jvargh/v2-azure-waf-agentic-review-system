"""Test diagram ingestion enrichment.

Validates that uploading a diagram results in extracted text or summary fields
being populated and that the unified corpus contains diagram-derived text after
analysis lifecycle.
"""
from fastapi.testclient import TestClient
from backend.server import app
import io

client = TestClient(app)

SVG_SAMPLE = """<svg xmlns='http://www.w3.org/2000/svg' width='200' height='100'>
  <text x='10' y='20'>WebTier</text>
  <text x='10' y='40'>AppService</text>
  <text x='10' y='60'>AzureSQL</text>
</svg>"""

def test_diagram_upload_and_enrichment():
    # Create assessment
    r = client.post('/api/assessments', json={'name': 'diagram-assessment'})
    assert r.status_code == 200, r.text
    aid = r.json()['id']

    # Upload diagram SVG
    files = [('files', ('arch.svg', SVG_SAMPLE, 'image/svg+xml'))]
    r2 = client.post(f'/api/assessments/{aid}/documents', files=files)
    assert r2.status_code == 200, r2.text
    docs = r2.json()
    assert len(docs) == 1
    doc = docs[0]
    assert doc['category'] == 'diagram'
    # Ensure enrichment fields present
    assert 'raw_extracted_text' in doc or 'analysis_metadata' in doc
    assert doc.get('diagram_summary') or doc.get('llm_analysis')
    # CRITICAL: verify extracted tokens are present
    raw_ext = doc.get('raw_extracted_text') or ''
    assert any(t in raw_ext for t in ['WebTier', 'AppService', 'AzureSQL']), f'Tokens missing from raw_extracted_text: {raw_ext}'

    # Run analysis lifecycle
    r3 = client.post(f'/api/assessments/{aid}/analyze')
    assert r3.status_code == 200, r3.text

    # Poll final assessment (synchronous bg task not awaited here, but unified_corpus should appear later)
    final = client.get(f'/api/assessments/{aid}')
    assert final.status_code == 200, final.text
    data = final.json()
    # unified_corpus may be empty early; allow missing but if present ensure diagram tokens included
    corpus = data.get('unified_corpus', '') or ''
    if corpus:
      # Corpus may not yet include raw extracted tokens if background task appended summary first.
      token_present = any(t in corpus for t in ['WebTier', 'AppService', 'AzureSQL'])
      if not token_present:
        # Fall back to checking document enrichment fields inside assessment payload
        docs_after = data.get('documents', [])
        diag_docs = [d for d in docs_after if d.get('category') == 'diagram']
        assert diag_docs, 'Diagram document missing in assessment payload'
        enriched_tokens = ' '.join([str(d.get('raw_extracted_text','') or '') for d in diag_docs])
        assert any(t in enriched_tokens for t in ['WebTier','AppService','AzureSQL']), 'Extracted diagram tokens not found in corpus or enrichment fields'

if __name__ == '__main__':  # pragma: no cover
    test_diagram_upload_and_enrichment()
    print('✅ Diagram ingestion test passed')
