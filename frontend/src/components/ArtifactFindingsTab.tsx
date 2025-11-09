import React, { useState } from 'react';
import { useAssessments } from '../context/AssessmentsContext';
import { DocumentItem } from '../types';
import { theme } from '../theme';

const ArtifactFindingsTab: React.FC = () => {
  const { selected } = useAssessments();
  const docs = selected?.documents || [];
  const archDocs = docs.filter((d: DocumentItem) => d.category === 'architecture');
  const caseDocs = docs.filter((d: DocumentItem) => d.category === 'case');
  const diagrams = docs.filter((d: DocumentItem) => d.category === 'diagram');

  return (
    <div>
      <h3>Uploaded Artifact Findings</h3>
      <div style={{ display:'grid', gap:'1rem', gridTemplateColumns:'repeat(auto-fit,minmax(160px,1fr))', marginTop:'1rem' }}>
        <div className="card"><strong style={{ fontSize:'1.2rem' }}>{docs.length}</strong><div className="small" style={{ marginTop:'.35rem' }}>Total Documents</div></div>
        <div className="card"><strong style={{ fontSize:'1.2rem' }}>{archDocs.length}</strong><div className="small" style={{ marginTop:'.35rem' }}>Architecture Docs</div></div>
        <div className="card"><strong style={{ fontSize:'1.2rem' }}>{diagrams.length}</strong><div className="small" style={{ marginTop:'.35rem' }}>Architecture Diagrams</div></div>
        <div className="card"><strong style={{ fontSize:'1.2rem' }}>{caseDocs.length}</strong><div className="small" style={{ marginTop:'.35rem' }}>Case Analysis CSVs</div></div>
      </div>
      <div className="info-box" style={{ marginTop:'1rem' }}>
        <strong>AI Analysis Context:</strong> These uploaded artifacts provide comprehensive context for the AI-powered Well-Architected review. Architecture documents inform textual analysis, diagrams enable visual component recognition, and CSV files provide historical case patterns for reactive analysis recommendations.
      </div>
      {archDocs.length > 0 && (
        <details style={{ marginTop:'1.5rem' }}>
          <summary style={{ cursor:'pointer', fontWeight:600 }}>Architecture Documents ({archDocs.length})</summary>
          <div style={{ marginTop:'.75rem' }}>
            {archDocs.map(d => (
              <div key={d.id} className="rec-card" style={{ borderColor:'#d0c9f5' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'.4rem', fontSize:'.75rem', fontWeight:600 }}>
                  <span style={{ background: theme.badge.architectureDoc.bg, color: theme.badge.architectureDoc.fg, padding:'2px 6px', borderRadius:'4px', fontSize:'.55rem', fontWeight:700 }}>ARCHITECTURE DOC</span>
                  {d.filename} • {d.contentType}
                </div>
                <div className="details-box" style={{ marginTop:'.5rem' }}>
                  {d.structured_report?.combined_markdown ? (
                    <>
                      <strong style={{ fontSize:'.65rem' }}>Structured Architecture Analysis:</strong>
                      <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.35rem 0 0', maxHeight:'22rem', overflow:'auto', background:'#fafafa', border:'1px solid #ddd', padding:'.35rem' }}>
{d.structured_report.combined_markdown.slice(0, 4500)}{d.structured_report.combined_markdown.length > 4500 ? '\n... (truncated)' : ''}
                      </pre>
                      {d.structured_report?.pillar_evidence && (
                        <div style={{ marginTop:'.6rem' }}>
                          <strong style={{ fontSize:'.65rem' }}>Pillar Evidence:</strong>
                          <div style={{ marginTop:'.3rem', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0', maxHeight:'14rem', overflow:'auto' }}>
                            {Object.entries(d.structured_report.pillar_evidence).map(([pillar, info]) => (
                              <div key={pillar} style={{ marginBottom:'.5rem' }}>
                                <strong style={{ fontSize:'.55rem', color:'#2c3e50' }}>{pillar.toUpperCase()} • {info.count}</strong>
                                <ul style={{ margin:'.2rem 0 0', paddingLeft:'1rem' }}>
                                  {info.excerpts.slice(0,6).map((ex, i) => (
                                    <li key={i} style={{ fontSize:'.5rem', lineHeight:1.15 }}>{ex}</li>
                                  ))}
                                  {info.excerpts.length > 6 && <li style={{ fontSize:'.5rem', opacity:.7 }}>… {info.excerpts.length - 6} more</li>}
                                </ul>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : d.structured_report?.executive_summary || d.structured_report?.architecture_overview || d.structured_report?.cross_cutting_concerns ? (
                    <>
                      {d.structured_report?.executive_summary && (
                        <div style={{ marginTop:'.4rem' }}>
                          <strong style={{ fontSize:'.65rem' }}>Executive Summary:</strong>
                          <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.25rem 0 0', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0' }}>{d.structured_report.executive_summary}</pre>
                        </div>
                      )}
                      {d.structured_report?.architecture_overview && (
                        <div style={{ marginTop:'.5rem' }}>
                          <strong style={{ fontSize:'.65rem' }}>Detailed Architecture Overview:</strong>
                          <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.25rem 0 0', maxHeight:'18rem', overflow:'auto', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0' }}>{d.structured_report.architecture_overview}</pre>
                        </div>
                      )}
                      {d.structured_report?.cross_cutting_concerns && Object.keys(d.structured_report.cross_cutting_concerns).length > 0 && (
                        <div style={{ marginTop:'.5rem' }}>
                          <strong style={{ fontSize:'.65rem' }}>Cross-Cutting Concerns:</strong>
                          <div style={{ marginTop:'.25rem', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0', maxHeight:'14rem', overflow:'auto' }}>
                            {Object.entries(d.structured_report.cross_cutting_concerns).map(([key, value]) => (
                              <div key={key} style={{ marginBottom:'.4rem' }}>
                                <strong style={{ fontSize:'.55rem', color:'#6c5ce7' }}>{key.replace(/_/g, ' ').toUpperCase()}:</strong>
                                <div style={{ fontSize:'.52rem', marginTop:'.15rem', color:'#2d3436' }}>{value as string}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {d.structured_report?.deployment_summary && (
                        <div style={{ marginTop:'.5rem' }}>
                          <strong style={{ fontSize:'.65rem' }}>Deployment Overview:</strong>
                          <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.25rem 0 0', maxHeight:'12rem', overflow:'auto', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0' }}>{d.structured_report.deployment_summary}</pre>
                        </div>
                      )}
                      {d.structured_report?.pillar_evidence && (
                        <div style={{ marginTop:'.6rem' }}>
                          <strong style={{ fontSize:'.65rem' }}>Pillar Evidence:</strong>
                          <div style={{ marginTop:'.3rem', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0', maxHeight:'14rem', overflow:'auto' }}>
                            {Object.entries(d.structured_report.pillar_evidence).map(([pillar, info]) => (
                              <div key={pillar} style={{ marginBottom:'.5rem' }}>
                                <strong style={{ fontSize:'.55rem', color:'#2c3e50' }}>{pillar.toUpperCase()} • {info.count}</strong>
                                <ul style={{ margin:'.2rem 0 0', paddingLeft:'1rem' }}>
                                  {info.excerpts.slice(0,6).map((ex, i) => (
                                    <li key={i} style={{ fontSize:'.5rem', lineHeight:1.15 }}>{ex}</li>
                                  ))}
                                  {info.excerpts.length > 6 && <li style={{ fontSize:'.5rem', opacity:.7 }}>… {info.excerpts.length - 6} more</li>}
                                </ul>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      {/* No structured report - show raw document text */}
                      <div style={{ marginTop:'.4rem' }}>
                        <strong style={{ fontSize:'.65rem' }}>📄 Raw Architecture Document</strong>
                        <div style={{ fontSize:'.6rem', color:'#666', marginTop:'.25rem', marginBottom:'.5rem' }}>
                          This document will be analyzed by the orchestrator agent during assessment.
                        </div>
                        <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'0', maxHeight:'24rem', overflow:'auto', background:'#fafafa', padding:'.5rem', border:'1px solid #ddd', lineHeight:1.4 }}>
{(d as any).raw_text || 'No content available'}
                        </pre>
                      </div>
                      {d.aiInsights && (
                        <details style={{ marginTop:'.5rem' }}>
                          <summary style={{ cursor:'pointer', fontSize:'.6rem' }}>Document Info</summary>
                          <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.35rem 0 0', color:'#666' }}>{d.aiInsights}</pre>
                        </details>
                      )}
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </details>
      )}
      {caseDocs.length > 0 && (
        <details style={{ marginTop:'1.25rem' }}>
          <summary style={{ cursor:'pointer', fontWeight:600 }}>Case Analysis Data ({caseDocs.length})</summary>
          <div style={{ marginTop:'.75rem' }}>
            {caseDocs.map(d => (
              <div key={d.id} className="rec-card" style={{ borderColor:'#b8eec5' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'.4rem', fontSize:'.75rem', fontWeight:600 }}>
                  <span style={{ background: theme.badge.supportCase.bg, color: theme.badge.supportCase.fg, padding:'2px 6px', borderRadius:'4px', fontSize:'.55rem', fontWeight:700 }}>SUPPORT CASES</span>
                  {d.filename} • {d.contentType}
                </div>
                <div className="details-box" style={{ marginTop:'.5rem' }}>
                  {d.structured_report?.executive_summary && (
                    <div style={{ marginTop:'.4rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Executive Summary:</strong>
                      <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.25rem 0 0', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0' }}>{d.structured_report.executive_summary}</pre>
                    </div>
                  )}
                  {d.structured_report?.support_case_concerns && (
                    <div style={{ marginTop:'.5rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Incident Patterns & Root Causes:</strong>
                      <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.25rem 0 0', maxHeight:'16rem', overflow:'auto', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0' }}>{d.structured_report.support_case_concerns}</pre>
                    </div>
                  )}
                  {d.structured_report?.cross_cutting_concerns && Object.keys(d.structured_report.cross_cutting_concerns).length > 0 && (
                    <div style={{ marginTop:'.5rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Cross-Cutting Concerns (Operational):</strong>
                      <div style={{ marginTop:'.25rem', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0', maxHeight:'14rem', overflow:'auto' }}>
                        {Object.entries(d.structured_report.cross_cutting_concerns).map(([key, value]) => (
                          <div key={key} style={{ marginBottom:'.4rem' }}>
                            <strong style={{ fontSize:'.55rem', color:'#1d6b32' }}>{key.replace(/_/g, ' ').toUpperCase()}:</strong>
                            <div style={{ fontSize:'.52rem', marginTop:'.15rem', color:'#2d3436' }}>{value as string}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {d.structured_report?.deployment_summary && (
                    <div style={{ marginTop:'.5rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Deployment / Environment Overview:</strong>
                      <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.25rem 0 0', maxHeight:'12rem', overflow:'auto', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0' }}>{d.structured_report.deployment_summary}</pre>
                    </div>
                  )}
                  {d.structured_report?.pillar_evidence && (
                    <div style={{ marginTop:'.6rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Pillar Evidence:</strong>
                      <div style={{ marginTop:'.3rem', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0', maxHeight:'14rem', overflow:'auto' }}>
                        {Object.entries(d.structured_report.pillar_evidence).map(([pillar, info]) => (
                          <div key={pillar} style={{ marginBottom:'.5rem' }}>
                            <strong style={{ fontSize:'.55rem', color:'#1d6b32' }}>{pillar.toUpperCase()} • {info.count}</strong>
                            <ul style={{ margin:'.2rem 0 0', paddingLeft:'1rem' }}>
                              {info.excerpts.slice(0,6).map((ex, i) => (
                                <li key={i} style={{ fontSize:'.5rem', lineHeight:1.15 }}>{ex}</li>
                              ))}
                              {info.excerpts.length > 6 && <li style={{ fontSize:'.5rem', opacity:.7 }}>… {info.excerpts.length - 6} more</li>}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </details>
      )}
      {diagrams.length > 0 && (
        <details style={{ marginTop:'1.25rem' }}>
          <summary style={{ cursor:'pointer', fontWeight:600 }}>Architecture Diagrams ({diagrams.length})</summary>
          <div style={{ marginTop:'.75rem' }}>
            {diagrams.map(d => (
              <div key={d.id} className="rec-card" style={{ borderColor:'#f5d9c9' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'.4rem', fontSize:'.75rem', fontWeight:600 }}>
                  <span style={{ background: theme.badge.architectureDiagram.bg, color: theme.badge.architectureDiagram.fg, padding:'2px 6px', borderRadius:'4px', fontSize:'.55rem', fontWeight:700 }}>ARCHITECTURE DIAGRAM</span>
                  {d.filename} • {d.contentType}
                </div>
                <div className="details-box" style={{ marginTop:'.5rem' }}>
                  {d.structured_report?.executive_summary && (
                    <div style={{ marginTop:'.4rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Executive Summary:</strong>
                      <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.25rem 0 0', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0' }}>{d.structured_report.executive_summary}</pre>
                    </div>
                  )}
                  {d.structured_report?.architecture_overview && (
                    <div style={{ marginTop:'.5rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Detailed Architecture Overview (Visual):</strong>
                      <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.25rem 0 0', maxHeight:'16rem', overflow:'auto', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0' }}>{d.structured_report.architecture_overview}</pre>
                    </div>
                  )}
                  {d.structured_report?.cross_cutting_concerns && Object.keys(d.structured_report.cross_cutting_concerns).length > 0 && (
                    <div style={{ marginTop:'.5rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Cross-Cutting Concerns (Inferred):</strong>
                      <div style={{ marginTop:'.25rem', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0', maxHeight:'14rem', overflow:'auto' }}>
                        {Object.entries(d.structured_report.cross_cutting_concerns).map(([key, value]) => (
                          <div key={key} style={{ marginBottom:'.4rem' }}>
                            <strong style={{ fontSize:'.55rem', color:'#8a5600' }}>{key.replace(/_/g, ' ').toUpperCase()}:</strong>
                            <div style={{ fontSize:'.52rem', marginTop:'.15rem', color:'#2d3436' }}>{value as string}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {d.structured_report?.deployment_summary && (
                    <div style={{ marginTop:'.5rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Deployment Overview (Visual Context):</strong>
                      <pre style={{ whiteSpace:'pre-wrap', fontSize:'.55rem', margin:'.25rem 0 0', maxHeight:'12rem', overflow:'auto', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0' }}>{d.structured_report.deployment_summary}</pre>
                    </div>
                  )}
                  {d.structured_report?.pillar_evidence && (
                    <div style={{ marginTop:'.6rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>Pillar Evidence (Inferred / Direct):</strong>
                      <div style={{ marginTop:'.3rem', background:'#fafafa', padding:'.35rem', border:'1px solid #e0e0e0', maxHeight:'14rem', overflow:'auto' }}>
                        {Object.entries(d.structured_report.pillar_evidence).map(([pillar, info]) => (
                          <div key={pillar} style={{ marginBottom:'.5rem' }}>
                            <strong style={{ fontSize:'.55rem', color:'#8a5600' }}>{pillar.toUpperCase()} • {info.count}{(info as any).inferred ? ' (inferred)' : ''}</strong>
                            <ul style={{ margin:'.2rem 0 0', paddingLeft:'1rem' }}>
                              {info.excerpts.slice(0,6).map((ex, i) => (
                                <li key={i} style={{ fontSize:'.5rem', lineHeight:1.15 }}>{ex}</li>
                              ))}
                              {info.excerpts.length > 6 && <li style={{ fontSize:'.5rem', opacity:.7 }}>… {info.excerpts.length - 6} more</li>}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </details>
      )}
      {!docs.length && <p style={{ fontSize:'.75rem', color:'#555', marginTop:'1.5rem' }}>No documents yet. Upload files to see AI artifact findings.</p>}
    </div>
  );
};

export default ArtifactFindingsTab;
