import React, { useState } from 'react';
import { useAssessments } from '../context/AssessmentsContext';

interface Props { onClose: () => void; onCreated: (id: string) => void; }

const CreateAssessmentModal: React.FC<Props> = ({ onClose, onCreated }: Props) => {
  const { create } = useAssessments();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      const a = await create(name.trim(), description.trim() || undefined);
      setSaving(false);
      onCreated(a.id);
    } catch (err: any) {
      setSaving(false);
      setError(err.message || 'Failed to create assessment. Check backend connection.');
    }
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal">
        <h2>Create New Assessment</h2>
        <form onSubmit={submit}>
          <div className="form-group">
            <label>Assessment Name *</label>
            <input value={name} onChange={e => setName(e.target.value)} required placeholder="e.g. Frontier Inc. - LLM Mode" />
          </div>
          <div className="form-group">
            <label>Description (Optional)</label>
            <textarea rows={3} value={description} onChange={e => setDescription(e.target.value)} placeholder="Brief context..." />
          </div>
          {error && (
            <div style={{ padding: '0.75rem', backgroundColor: '#fee', border: '1px solid #fcc', borderRadius: '0.375rem', marginBottom: '1rem', color: '#c00' }}>
              <strong>Error:</strong> {error}
            </div>
          )}
          <div className="info-box">
            After creating the assessment, you'll be able to upload architecture documents, diagrams, and CSV support case files. Our AI agents will analyze your architecture against all 5 pillars of the Well-Architected Framework.
          </div>
          <div style={{ display:'flex', justifyContent:'flex-end', gap:'.75rem' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Creating...' : 'Create Assessment'}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAssessmentModal;
