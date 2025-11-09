"""Test document deletion functionality."""
from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)


def test_delete_document_from_pending_assessment():
    """Verify document can be deleted from pending assessment."""
    # Create assessment
    r = client.post('/api/assessments', json={'name': 'test-delete-doc'})
    assert r.status_code == 200
    aid = r.json()['id']
    
    # Upload document
    files = [('files', ('test.txt', b'Architecture content', 'text/plain'))]
    r2 = client.post(f'/api/assessments/{aid}/documents', files=files)
    assert r2.status_code == 200
    docs = r2.json()
    assert len(docs) == 1
    doc_id = docs[0]['id']
    
    # Delete document
    r3 = client.delete(f'/api/assessments/{aid}/documents/{doc_id}')
    assert r3.status_code == 200
    result = r3.json()
    assert result['status'] == 'deleted'
    assert result['document_id'] == doc_id
    
    # Verify document removed
    r4 = client.get(f'/api/assessments/{aid}')
    assert r4.status_code == 200
    assessment = r4.json()
    assert len(assessment['documents']) == 0


def test_delete_document_blocked_after_analysis_starts():
    """Verify document deletion blocked once analysis begins."""
    # Create assessment
    r = client.post('/api/assessments', json={'name': 'test-delete-blocked'})
    assert r.status_code == 200
    aid = r.json()['id']
    
    # Upload document
    files = [('files', ('test.txt', b'Architecture content', 'text/plain'))]
    r2 = client.post(f'/api/assessments/{aid}/documents', files=files)
    assert r2.status_code == 200
    docs = r2.json()
    doc_id = docs[0]['id']
    
    # Start analysis (sets status to preprocessing/analyzing)
    r3 = client.post(f'/api/assessments/{aid}/analyze')
    assert r3.status_code == 200
    
    # Wait briefly for status transition
    import time
    time.sleep(0.5)
    
    # Attempt to delete document - should fail
    r4 = client.delete(f'/api/assessments/{aid}/documents/{doc_id}')
    assert r4.status_code == 400
    assert 'Cannot delete documents' in r4.json()['detail']


def test_delete_nonexistent_document():
    """Verify 404 returned when deleting non-existent document."""
    # Create assessment
    r = client.post('/api/assessments', json={'name': 'test-404'})
    assert r.status_code == 200
    aid = r.json()['id']
    
    # Try to delete non-existent document
    r2 = client.delete(f'/api/assessments/{aid}/documents/doc_999999')
    assert r2.status_code == 404
    assert 'document not found' in r2.json()['detail'].lower()


def test_delete_multiple_documents_selectively():
    """Verify selective deletion of multiple documents."""
    # Create assessment
    r = client.post('/api/assessments', json={'name': 'test-multi-delete'})
    assert r.status_code == 200
    aid = r.json()['id']
    
    # Upload 3 documents
    files = [
        ('files', ('doc1.txt', b'Content 1', 'text/plain')),
        ('files', ('doc2.txt', b'Content 2', 'text/plain')),
        ('files', ('doc3.txt', b'Content 3', 'text/plain'))
    ]
    r2 = client.post(f'/api/assessments/{aid}/documents', files=files)
    assert r2.status_code == 200
    docs = r2.json()
    assert len(docs) == 3
    
    # Delete middle document
    doc_to_delete = docs[1]['id']
    r3 = client.delete(f'/api/assessments/{aid}/documents/{doc_to_delete}')
    assert r3.status_code == 200
    
    # Verify only 2 documents remain
    r4 = client.get(f'/api/assessments/{aid}')
    assert r4.status_code == 200
    assessment = r4.json()
    assert len(assessment['documents']) == 2
    remaining_ids = [d['id'] for d in assessment['documents']]
    assert doc_to_delete not in remaining_ids
    assert docs[0]['id'] in remaining_ids
    assert docs[2]['id'] in remaining_ids


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
