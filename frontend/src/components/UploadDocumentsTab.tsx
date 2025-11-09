import React, { useCallback, useState } from 'react';
import { useAssessments } from '../context/AssessmentsContext';

interface Props { assessmentId: string; onStartAnalysis: () => void; }

const UploadDocumentsTab: React.FC<Props> = ({ assessmentId, onStartAnalysis }: Props) => {
  const { selected, addDocuments, removeDocument, beginAnalysis } = useAssessments();
  const [drag, setDrag] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  const onFiles = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    await addDocuments(assessmentId, Array.from(files));
    setUploading(false);
  }, [assessmentId, addDocuments]);

  const start = async () => {
    await beginAnalysis(assessmentId);
    onStartAnalysis();
  };

  const handleDelete = async (docId: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    setDeleting(docId);
    try {
      await removeDocument(assessmentId, docId);
    } catch (err: any) {
      console.error('Delete failed for', docId, 'in assessment', assessmentId, 'documents:', selected?.documents.map(d=>d.id));
      alert(err.message || 'Failed to delete document');
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div>
      <h3>Upload Architecture Documents, Images & CSV Files</h3>
      <p style={{ fontSize:'.8rem', color:'#555', marginTop:'.35rem' }}>Upload your architecture diagrams, documentation, and CSV support case files. Our AI agents will analyze these against the 5 pillars.</p>
      <div
        className={`upload-area ${drag ? 'drag' : ''}`}
        onDragOver={(e: React.DragEvent) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e: React.DragEvent) => { e.preventDefault(); setDrag(false); onFiles(e.dataTransfer.files); }}
        onClick={() => document.getElementById('fileInput')?.click()}
      >
        <div style={{ fontSize:'2.5rem', opacity:.35 }}>📁</div>
        <p style={{ fontSize:'.8rem', margin:'0.5rem 0 0', fontWeight:600 }}>Drop files here or click to upload</p>
        <p style={{ fontSize:'.65rem', margin:'.35rem 0 0', color:'#666' }}>Documents: PDF, DOC, TXT | Images: PNG, JPG, SVG | CSV: Support Case Data</p>
        <input id="fileInput" type="file" multiple style={{ display:'none' }} onChange={(e: React.ChangeEvent<HTMLInputElement>) => onFiles(e.target.files)} accept=".pdf,.doc,.docx,.txt,.md,.png,.jpg,.jpeg,.svg,.csv" />
      </div>
      <div className="file-list">
        {selected?.documents.length ? <h4 style={{ margin:'1.5rem 0 .75rem' }}>Uploaded Documents ({selected.documents.length})</h4> : null}
        {selected?.documents.map(d => (
          <div className="doc-row" key={d.id}>
            <div style={{ display:'flex', flexDirection:'column' }}>
              <strong style={{ fontSize:'.8rem' }}>{d.filename}</strong>
              <span style={{ fontSize:'.6rem', color:'#555' }}>{d.contentType}</span>
            </div>
            <div style={{ display:'flex', alignItems:'center', gap:'0.5rem' }}>
              <span className={`badge-type ${d.category === 'architecture' ? 'badge-arch' : d.category === 'case' ? 'badge-case' : 'badge-diagram'}`}>{d.category === 'architecture' ? 'Architecture Doc' : d.category === 'case' ? 'Case Analysis Data' : 'Architecture Diagram'}</span>
              {selected?.status === 'pending' && (
                <button
                  className="btn-delete"
                  onClick={() => handleDelete(d.id)}
                  disabled={deleting === d.id}
                  title="Delete document"
                  style={{ padding:'0.25rem 0.5rem', fontSize:'0.75rem', cursor: deleting === d.id ? 'not-allowed' : 'pointer', opacity: deleting === d.id ? 0.5 : 1 }}
                >
                  {deleting === d.id ? '...' : '🗑️'}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
      {uploading && <p style={{ fontSize:'.7rem', color:'#555' }}>Uploading...</p>}
      {selected?.status === 'pending' && selected.documents.length > 0 && (
        <div style={{ display:'flex', justifyContent:'flex-end', marginTop:'1.25rem' }}>
          <button className="btn btn-primary" onClick={start}>🚀 Start Enhanced Well-Architected Analysis</button>
        </div>
      )}
    </div>
  );
};

export default UploadDocumentsTab;
