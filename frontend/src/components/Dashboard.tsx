import React, { useState } from 'react';
import ConnectionStatus from './ConnectionStatus';
import { useAssessments } from '../context/AssessmentsContext';
import CreateAssessmentModal from './CreateAssessmentModal';
import { Assessment } from '../types';

interface Props { onOpenAssessment: (id: string) => void; }

const Dashboard: React.FC<Props> = ({ onOpenAssessment }: Props) => {
  const { assessments, remove } = useAssessments();
  const [showModal, setShowModal] = useState(false);

  const total = assessments.length;
  const completed = assessments.filter(a => a.status === 'completed').length;
  const analyzing = assessments.filter(a => a.status === 'analyzing').length;
  const avgScore = completed === 0 ? 0 : Math.round(
    assessments
      .filter((a: Assessment) => a.pillarScores)
      .reduce((sum: number, a: Assessment) => sum + ((a?.pillarScores?.reduce((s: number, p) => s + (p.score || p.overallScore || 0), 0) || 0) / 5), 0) / completed
  );

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString();
  }

  return (
    <div>
      {/* Professional Header with Microsoft Branding */}
      <div style={{
        background: '#0078d4',
        padding: '1.25rem 1.5rem',
        marginBottom: '1.5rem',
        borderRadius: '6px',
        boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
        position: 'relative',
        paddingRight: '110px'
      }}>
        <ConnectionStatus variant="floating" />
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
          {/* Microsoft Logo - 4 colored squares */}
          <svg width="23" height="23" viewBox="0 0 23 23" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0 }}>
            <rect width="11" height="11" fill="#f25022"/>
            <rect x="12" width="11" height="11" fill="#7fba00"/>
            <rect y="12" width="11" height="11" fill="#00a4ef"/>
            <rect x="12" y="12" width="11" height="11" fill="#ffb900"/>
          </svg>
          <h1 style={{
            color: 'white',
            fontSize: '1.5rem',
            fontWeight: 400,
            margin: '0',
            letterSpacing: '0'
          }}>Azure Well-Architected Agentic Review System</h1>
        </div>
        <p style={{
          color: 'rgba(255,255,255,0.9)',
          fontSize: '0.875rem',
          margin: '0',
          fontWeight: 300
        }}>
          Analyze your Azure architecture against the 5 pillars of excellence.
        </p>
      </div>

      {/* Action Button */}
      <div style={{ marginBottom: '1.25rem', display: 'flex', justifyContent: 'flex-end' }}>
        <button 
          className="btn btn-primary" 
          onClick={() => setShowModal(true)}
          style={{
            background: '#0078d4',
            color: 'white',
            border: 'none',
            padding: '0.55rem 1rem',
            fontSize: '0.875rem',
            fontWeight: 600,
            borderRadius: '2px',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.background = '#106ebe'}
          onMouseOut={(e) => e.currentTarget.style.background = '#0078d4'}
        >
          + New Well-Architected Assessment
        </button>
      </div>

      {/* Stats Overview */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ 
          fontSize: '1.1rem', 
          fontWeight: 600, 
          margin: '0 0 0.75rem',
          color: '#1a1a1a'
        }}>Overview</h2>
        <div className="stats-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: '0.75rem'
        }}>
          <div className="card" style={{
            padding: '0.75rem',
            borderRadius: '6px',
            border: '1px solid #e1e4e8',
            background: '#fff'
          }}>
            <h4 style={{ 
              fontSize: '0.65rem', 
              fontWeight: 600, 
              textTransform: 'uppercase', 
              color: '#586069',
              letterSpacing: '0.5px',
              margin: '0 0 0.4rem'
            }}>TOTAL REVIEWS</h4>
            <div className="metric" style={{
              fontSize: '1.75rem',
              fontWeight: 600,
              color: '#0078d4'
            }}>{total}</div>
          </div>
          <div className="card" style={{
            padding: '0.75rem',
            borderRadius: '6px',
            border: '1px solid #e1e4e8',
            background: '#fff'
          }}>
            <h4 style={{ 
              fontSize: '0.65rem', 
              fontWeight: 600, 
              textTransform: 'uppercase', 
              color: '#586069',
              letterSpacing: '0.5px',
              margin: '0 0 0.4rem'
            }}>COMPLETED</h4>
            <div className="metric" style={{
              fontSize: '1.75rem',
              fontWeight: 600,
              color: '#28a745'
            }}>{completed}</div>
          </div>
          <div className="card" style={{
            padding: '0.75rem',
            borderRadius: '6px',
            border: '1px solid #e1e4e8',
            background: '#fff'
          }}>
            <h4 style={{ 
              fontSize: '0.65rem', 
              fontWeight: 600, 
              textTransform: 'uppercase', 
              color: '#586069',
              letterSpacing: '0.5px',
              margin: '0 0 0.4rem'
            }}>IN PROGRESS</h4>
            <div className="metric" style={{
              fontSize: '1.75rem',
              fontWeight: 600,
              color: '#ffc107'
            }}>{analyzing}</div>
          </div>
          <div className="card" style={{
            padding: '0.75rem',
            borderRadius: '6px',
            border: '1px solid #e1e4e8',
            background: '#fff'
          }}>
            <h4 style={{ 
              fontSize: '0.65rem', 
              fontWeight: 600, 
              textTransform: 'uppercase', 
              color: '#586069',
              letterSpacing: '0.5px',
              margin: '0 0 0.4rem'
            }}>AVG SCORE</h4>
            <div className="metric" style={{
              fontSize: '1.75rem',
              fontWeight: 600,
              color: '#0078d4'
            }}>{completed === 0 ? 'N/A' : `${avgScore}%`}</div>
          </div>
        </div>
      </div>

      {/* Recent Assessments Section */}
      <h2 style={{ 
        fontSize: '1.1rem', 
        fontWeight: 600, 
        margin: '0 0 0.75rem',
        color: '#1a1a1a'
      }}>Recent Assessments</h2>
      {assessments.length === 0 && (
        <div className="card" style={{ 
          textAlign: 'center', 
          padding: '4rem 2rem',
          background: '#f6f8fa',
          border: '2px dashed #d1d5da',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '4rem', opacity: 0.3, marginBottom: '1rem' }}>�</div>
          <p style={{ 
            margin: '0 0 0.5rem', 
            fontWeight: 600, 
            fontSize: '1.1rem',
            color: '#24292e'
          }}>No architecture reviews yet</p>
          <p style={{ 
            margin: 0, 
            fontSize: '0.9rem', 
            color: '#586069',
            maxWidth: '500px',
            marginLeft: 'auto',
            marginRight: 'auto',
            lineHeight: '1.5'
          }}>
            Get started by creating your first assessment to analyze your Azure architecture 
            against Microsoft's Well-Architected Framework best practices.
          </p>
        </div>
      )}
      <div className="recent-list" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {assessments.map((a: Assessment) => (
          <div 
            key={a.id} 
            className="assessment-item"
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '0.875rem 1rem',
              background: '#fff',
              border: '1px solid #e1e4e8',
              borderRadius: '6px',
              transition: 'all 0.2s',
              cursor: 'pointer'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
              e.currentTarget.style.borderColor = '#0078d4';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.boxShadow = 'none';
              e.currentTarget.style.borderColor = '#e1e4e8';
            }}
          >
            <div style={{ flex: 1 }} onClick={() => onOpenAssessment(a.id)}>
              <div className="assessment-title" style={{
                fontSize: '0.95rem',
                fontWeight: 600,
                color: '#24292e',
                marginBottom: '0.35rem'
              }}>{a.name}</div>
              <div className="subtext" style={{
                display: 'flex',
                gap: '0.75rem',
                fontSize: '0.75rem',
                color: '#586069'
              }}>
                <span>📄 {a.documents.length} document{a.documents.length !== 1 ? 's' : ''}</span>
                <span>📅 {formatDate(a.createdAt)}</span>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span 
                className={`badge ${a.status === 'pending' ? 'badge-pending' : ['preprocessing', 'analyzing', 'aligning'].includes(a.status) ? 'badge-analyzing' : a.status === 'completed' ? 'badge-completed' : 'badge-pending'}`}
                style={{
                  padding: '0.35rem 0.75rem',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}
              >
                {a.status === 'pending' ? 'Pending' : a.status === 'preprocessing' ? 'Preprocessing' : a.status === 'analyzing' ? 'Analyzing' : a.status === 'aligning' ? 'Aligning' : a.status === 'completed' ? 'Completed' : a.status === 'failed' ? 'Failed' : a.status}
              </span>
              <button 
                className="icon-btn" 
                aria-label="Delete" 
                onClick={() => remove(a.id)}
                style={{
                  background: 'transparent',
                  border: '1px solid #d1d5da',
                  borderRadius: '4px',
                  padding: '0.5rem',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  transition: 'all 0.2s'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = '#ffeef0';
                  e.currentTarget.style.borderColor = '#dc3545';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.borderColor = '#d1d5da';
                }}
              >🗑️</button>
              <button 
                className="icon-btn" 
                aria-label="Open" 
                onClick={() => onOpenAssessment(a.id)}
                style={{
                  background: '#0078d4',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '0.5rem 0.75rem',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  transition: 'all 0.2s',
                  color: 'white'
                }}
                onMouseOver={(e) => e.currentTarget.style.background = '#106ebe'}
                onMouseOut={(e) => e.currentTarget.style.background = '#0078d4'}
              >➡️</button>
            </div>
          </div>
        ))}
      </div>
      {showModal && <CreateAssessmentModal onClose={() => setShowModal(false)} onCreated={(id) => { setShowModal(false); onOpenAssessment(id); }} />}
    </div>
  );
};

export default Dashboard;
