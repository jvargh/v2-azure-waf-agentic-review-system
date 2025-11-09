import React, { useState } from 'react';
import ConnectionStatus from './ConnectionStatus';
import { useAssessments } from '../context/AssessmentsContext';
import UploadDocumentsTab from './UploadDocumentsTab';
import ArtifactFindingsTab from './ArtifactFindingsTab';
import AnalysisProgressTab from './AnalysisProgressTab';
import ResultsScorecardTab from './ResultsScorecardTab';
import VisualizationTab from '../visualization/VisualizationTab';

interface Props { onBack: () => void; }

const AssessmentDetail: React.FC<Props> = ({ onBack }: Props) => {
  const { selected } = useAssessments();
  const [tab, setTab] = useState<'upload' | 'artifacts' | 'progress' | 'results' | 'visualization'>('upload');

  React.useEffect(() => {
    if (['preprocessing', 'analyzing', 'aligning'].includes(selected?.status || '')) setTab('progress');
    if (selected?.status === 'completed') setTab('results');
  }, [selected?.status]);

  if (!selected) return <div><button onClick={onBack}>Back</button>Not found</div>;

  const getBadgeClass = () => {
    if (selected.status === 'pending') return 'badge-pending';
    if (['preprocessing', 'analyzing', 'aligning'].includes(selected.status)) return 'badge-analyzing';
    if (selected.status === 'completed') return 'badge-completed';
    return 'badge-pending'; // failed or unknown
  };

  const getBadgeText = () => {
    if (selected.status === 'pending') return 'Pending';
    if (selected.status === 'preprocessing') return 'Preprocessing';
    if (selected.status === 'analyzing') return 'Analyzing';
    if (selected.status === 'aligning') return 'Aligning';
    if (selected.status === 'completed') return 'Completed';
    if (selected.status === 'failed') return 'Failed';
    return selected.status;
  };

  return (
    <div>
      {/* Header with back button and status */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '1.5rem',
        paddingBottom: '1rem',
        borderBottom: '1px solid #e1e4e8',
        position: 'relative',
        paddingRight: '110px' /* reserve space for connection badge */
      }}>
        <ConnectionStatus variant="floating" />
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button 
            className="icon-btn" 
            onClick={onBack}
            style={{
              background: 'transparent',
              border: '1px solid #d1d5da',
              borderRadius: '4px',
              padding: '0.5rem 0.75rem',
              cursor: 'pointer',
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              transition: 'all 0.2s',
              color: '#24292e'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = '#f6f8fa';
              e.currentTarget.style.borderColor = '#0078d4';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.borderColor = '#d1d5da';
            }}
          >
            <span style={{ fontSize: '1rem' }}>◄</span> Back to Dashboard
          </button>
          <h2 style={{ 
            margin: 0, 
            fontSize: '1.5rem', 
            fontWeight: 600,
            color: '#24292e'
          }}>{selected.name}</h2>
        </div>
        <span 
          className={`badge ${getBadgeClass()}`}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '12px',
            fontSize: '0.8rem',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}
        >{getBadgeText()}</span>
      </div>

      {/* Navigation Tabs */}
      <div className="tabs" style={{
        display: 'flex',
        gap: '0.5rem',
        borderBottom: '2px solid #e1e4e8',
        marginBottom: '1.5rem'
      }}>
        <button 
          className={`tab-btn ${tab === 'upload' ? 'active' : ''}`} 
          onClick={() => setTab('upload')}
          style={{
            background: 'transparent',
            border: 'none',
            borderBottom: tab === 'upload' ? '2px solid #0078d4' : '2px solid transparent',
            padding: '0.75rem 1rem',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: tab === 'upload' ? 600 : 400,
            color: tab === 'upload' ? '#0078d4' : '#586069',
            transition: 'all 0.2s',
            marginBottom: '-2px'
          }}
          onMouseOver={(e) => !tab.includes('upload') && (e.currentTarget.style.color = '#24292e')}
          onMouseOut={(e) => !tab.includes('upload') && (e.currentTarget.style.color = '#586069')}
        >📄 UPLOAD DOCUMENTS</button>
        <button 
          className={`tab-btn ${tab === 'artifacts' ? 'active' : ''}`} 
          onClick={() => setTab('artifacts')}
          style={{
            background: 'transparent',
            border: 'none',
            borderBottom: tab === 'artifacts' ? '2px solid #0078d4' : '2px solid transparent',
            padding: '0.75rem 1rem',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: tab === 'artifacts' ? 600 : 400,
            color: tab === 'artifacts' ? '#0078d4' : '#586069',
            transition: 'all 0.2s',
            marginBottom: '-2px'
          }}
          onMouseOver={(e) => !tab.includes('artifacts') && (e.currentTarget.style.color = '#24292e')}
          onMouseOut={(e) => !tab.includes('artifacts') && (e.currentTarget.style.color = '#586069')}
        >🔍 UPLOADED ARTIFACT FINDINGS</button>
        <button 
          className={`tab-btn ${tab === 'progress' ? 'active' : ''}`} 
          onClick={() => setTab('progress')}
          style={{
            background: 'transparent',
            border: 'none',
            borderBottom: tab === 'progress' ? '2px solid #0078d4' : '2px solid transparent',
            padding: '0.75rem 1rem',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: tab === 'progress' ? 600 : 400,
            color: tab === 'progress' ? '#0078d4' : '#586069',
            transition: 'all 0.2s',
            marginBottom: '-2px'
          }}
          onMouseOver={(e) => !tab.includes('progress') && (e.currentTarget.style.color = '#24292e')}
          onMouseOut={(e) => !tab.includes('progress') && (e.currentTarget.style.color = '#586069')}
        >⚡ ANALYSIS PROGRESS</button>
        <button 
          className={`tab-btn ${tab === 'results' ? 'active' : ''}`} 
          onClick={() => setTab('results')}
          style={{
            background: 'transparent',
            border: 'none',
            borderBottom: tab === 'results' ? '2px solid #0078d4' : '2px solid transparent',
            padding: '0.75rem 1rem',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: tab === 'results' ? 600 : 400,
            color: tab === 'results' ? '#0078d4' : '#586069',
            transition: 'all 0.2s',
            marginBottom: '-2px'
          }}
          onMouseOver={(e) => !tab.includes('results') && (e.currentTarget.style.color = '#24292e')}
          onMouseOut={(e) => !tab.includes('results') && (e.currentTarget.style.color = '#586069')}
        >📊 RESULTS & SCORECARD</button>
        <button 
          className={`tab-btn ${tab === 'visualization' ? 'active' : ''}`} 
          onClick={() => setTab('visualization')}
          style={{
            background: 'transparent',
            border: 'none',
            borderBottom: tab === 'visualization' ? '2px solid #0078d4' : '2px solid transparent',
            padding: '0.75rem 1rem',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: tab === 'visualization' ? 600 : 400,
            color: tab === 'visualization' ? '#0078d4' : '#586069',
            transition: 'all 0.2s',
            marginBottom: '-2px'
          }}
          onMouseOver={(e) => !tab.includes('visualization') && (e.currentTarget.style.color = '#24292e')}
          onMouseOut={(e) => !tab.includes('visualization') && (e.currentTarget.style.color = '#586069')}
        >📈 VISUALIZATION</button>
      </div>

      <div style={{ marginTop: '1.5rem' }}>
        {tab === 'upload' && <UploadDocumentsTab assessmentId={selected.id} onStartAnalysis={() => setTab('progress')} />}
        {tab === 'artifacts' && <ArtifactFindingsTab />}
        {tab === 'progress' && <AnalysisProgressTab />}
        {tab === 'results' && <ResultsScorecardTab />}
        {tab === 'visualization' && <VisualizationTab />}
      </div>
    </div>
  );
};

export default AssessmentDetail;
