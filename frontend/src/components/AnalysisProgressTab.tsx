import React from 'react';
import { useAssessments } from '../context/AssessmentsContext';
import { PhaseTask } from '../types';

const pillars = [
  { key: 'Reliability', desc: 'Resiliency, availability, recovery' },
  { key: 'Security', desc: 'Data protection, threat detection' },
  { key: 'Cost Optimization', desc: 'Cost modeling, budgets, reduce waste' },
  { key: 'Operational Excellence', desc: 'Monitoring, DevOps practices' },
  { key: 'Performance Efficiency', desc: 'Scalability, load testing' }
];

const AnalysisProgressTab: React.FC = () => {
  const { selected } = useAssessments();
  const enhancedProgress = selected?.enhancedProgress;
  const [cohesiveExpanded, setCohesiveExpanded] = React.useState(false);
  const [phaseDetailsExpanded, setPhaseDetailsExpanded] = React.useState(false);
  
  // Fallback to legacy progress calculation if enhanced progress not available
  const progress = enhancedProgress?.overall_progress ?? selected?.progress ?? 0;
  const currentPhase = enhancedProgress?.current_phase ?? selected?.currentPhase ?? '';
  const status = enhancedProgress?.status ?? selected?.status ?? 'pending';
  const pillarStatuses = selected?.pillarStatuses || {};
  const pillarProgress = selected?.pillarProgress || {};

  function pillarState(pillarKey: string) {
    // Use real-time pillar status if available
    const pillarStatus = pillarStatuses[pillarKey];
    if (pillarStatus === 'completed') return 'complete';
    if (pillarStatus === 'analyzing') return 'analyzing';
    if (pillarStatus === 'failed') return 'failed';
    
    // Fallback to progress-based for backward compatibility
    if (!selected || !pillarStatus) {
      // If assessment is completed, all pillars are complete
      if (selected?.status === 'completed') return 'complete';
      // Otherwise show waiting
      return 'waiting';
    }
    
    return 'waiting';
  }
  
  function getStatusText() {
    if (status === 'preprocessing') return 'Analyzing documents and building context...';
    if (status === 'analyzing') return 'Running AI agent assessments...';
    if (status === 'aligning') return 'Performing cross-pillar alignment...';
    if (status === 'completed') return 'Analysis complete!';
    return 'Ready to start';
  }

  function getPhaseIcon(phase: PhaseTask) {
    switch (phase.status) {
      case 'completed': return '✓';
      case 'active': return '🔄';
      case 'failed': return '❌';
      default: return '○';
    }
  }

  function getPhaseColor(phase: PhaseTask) {
    switch (phase.status) {
      case 'completed': return '#0b7a30';
      case 'active': return '#004bcc';
      case 'failed': return '#dc3545';
      default: return '#999';
    }
  }

  return (
    <div>
      <h3>Analysis Progress</h3>
      <p style={{ fontSize:'.8rem', color:'#555', marginTop:'.35rem' }}>Our specialized AI agents are analyzing your architecture against each pillar of the Well-Architected Framework.</p>
      
      {/* Current Phase Indicator */}
      {currentPhase && status !== 'completed' && (
        <div style={{ padding:'.75rem', backgroundColor:'#e3f2fd', borderRadius:'6px', marginBottom:'1rem', fontSize:'.75rem' }}>
          <strong>Current Phase:</strong> {currentPhase}
          {enhancedProgress?.estimated_total_time && (
            <span style={{ marginLeft: '0.5rem', color: '#004bcc', fontWeight: 600 }}>
              (Est. {enhancedProgress.estimated_total_time})
            </span>
          )}
        </div>
      )}
      
      <div className="progress-wrapper">
        <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'.35rem' }}>
          <span style={{ fontSize:'.7rem', fontWeight:600 }}>{getStatusText()}</span>
          <span style={{ fontSize:'.7rem', fontWeight:600 }}>{progress}%</span>
        </div>
        <div className="progress-bar-bg">
          <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>
      
      <div className="pillars-grid">
        {pillars.map((p) => {
          const state = pillarState(p.key);
          const pillarProg = pillarProgress[p.key] || 0;
          const statusIcon = state === 'complete' ? '✓' : state === 'analyzing' ? '🔄' : state === 'failed' ? '❌' : '⏳';
          const statusText = state === 'complete' ? 'Complete' : state === 'analyzing' ? 'Analyzing' : state === 'failed' ? 'Failed' : 'Waiting';
          const statusColor = state === 'complete' ? '#0b7a30' : state === 'analyzing' ? '#004bcc' : state === 'failed' ? '#dc3545' : '#555';
          
          // Find corresponding subtask from enhanced progress
          const subtask = enhancedProgress?.subtasks?.find(s => 
            s.name.toLowerCase().includes(p.key.toLowerCase())
          );
          
          return (
            <div key={p.key} className={`pillar ${state}`} style={{ backgroundColor: state === 'complete' ? '#e6f9ed' : 'white' }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                <strong style={{ fontSize:'.85rem' }}>{p.key}</strong>
                {statusIcon}
              </div>
              <small>{p.desc}</small>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginTop:'.25rem' }}>
                <span style={{ fontSize:'.65rem', fontWeight:600, color: statusColor }}>
                  {statusText}
                  {subtask?.estimated_time_remaining && state === 'analyzing' && (
                    <span style={{ marginLeft: '0.25rem', color: '#666' }}>
                      ({subtask.estimated_time_remaining})
                    </span>
                  )}
                </span>
                {state === 'analyzing' && pillarProg > 0 && (
                  <span style={{ fontSize:'.65rem', fontWeight:600, color: '#004bcc' }}>
                    {pillarProg}%
                  </span>
                )}
              </div>
              {state === 'analyzing' && pillarProg > 0 && (
                <div style={{ width:'100%', height:'3px', backgroundColor:'#e0e0e0', borderRadius:'2px', marginTop:'.25rem', overflow:'hidden' }}>
                  <div style={{ width:`${pillarProg}%`, height:'100%', backgroundColor:'#004bcc', transition:'width 0.3s ease' }} />
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Enhanced Phase Timeline */}
      {enhancedProgress && progress > 0 && progress < 100 && (
        <div style={{ marginTop:'1.25rem', fontSize:'.7rem' }}>
          <strong>Assessment Phases:</strong>
          <div style={{ marginTop:'.5rem', paddingLeft:'.5rem' }}>
            {enhancedProgress.phases.map((phase) => (
              <div key={phase.id} style={{ 
                color: getPhaseColor(phase), 
                marginBottom: '0.25rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span>
                  {getPhaseIcon(phase)} {phase.name}
                  {phase.status === 'active' && phase.progress > 0 && (
                    <span style={{ marginLeft: '0.25rem', fontSize: '0.65rem' }}>
                      ({phase.progress}%)
                    </span>
                  )}
                </span>
                {phase.estimated_time_remaining && (
                  <span style={{ fontSize: '0.65rem', color: '#666' }}>
                    {phase.estimated_time_remaining}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fallback Legacy Phase Timeline */}
      {!enhancedProgress && progress > 0 && progress < 100 && (
        <div style={{ marginTop:'1.25rem', fontSize:'.7rem' }}>
          <strong>Assessment Phases:</strong>
          <div style={{ marginTop:'.5rem', paddingLeft:'.5rem' }}>
            <div style={{ color: progress >= 5 ? '#0b7a30' : '#999' }}>
              {progress >= 5 ? '✓' : '○'} Initialization (0-5%)
            </div>
            <div style={{ color: progress >= 15 ? '#0b7a30' : progress > 5 ? '#004bcc' : '#999' }}>
              {progress >= 15 ? '✓' : progress > 5 ? '🔄' : '○'} Document Processing (5-15%)
            </div>
            <div style={{ color: progress >= 20 ? '#0b7a30' : progress > 15 ? '#004bcc' : '#999' }}>
              {progress >= 20 ? '✓' : progress > 15 ? '🔄' : '○'} Corpus Assembly (15-20%)
            </div>
            <div style={{ color: progress >= 80 ? '#0b7a30' : progress >= 20 ? '#004bcc' : '#999' }}>
              {progress >= 80 ? '✓' : progress >= 20 ? '🔄' : '○'} Pillar Evaluation (20-80%)
            </div>
            <div style={{ color: progress >= 90 ? '#0b7a30' : progress >= 80 ? '#004bcc' : '#999' }}>
              {progress >= 90 ? '✓' : progress >= 80 ? '🔄' : '○'} Cross-Pillar Alignment (80-90%)
            </div>
            <div style={{ color: progress >= 95 ? '#0b7a30' : progress >= 90 ? '#004bcc' : '#999' }}>
              {progress >= 95 ? '✓' : progress >= 90 ? '🔄' : '○'} Synthesis (90-95%)
            </div>
            <div style={{ color: progress === 100 ? '#0b7a30' : progress > 95 ? '#004bcc' : '#999' }}>
              {progress === 100 ? '✓' : progress > 95 ? '🔄' : '○'} Finalization (95-100%)
            </div>
          </div>
        </div>
      )}

      {/* Active Background Tasks */}
      {enhancedProgress && enhancedProgress.subtasks.length > 0 && (
        <div style={{ marginTop:'1rem', fontSize:'.7rem' }}>
          <strong>Active Tasks:</strong>
          <div style={{ marginTop:'.5rem', paddingLeft:'.5rem' }}>
            {enhancedProgress.subtasks
              .filter(task => task.status === 'active' || task.status === 'completed')
              .map((task) => (
                <div key={task.id} style={{ 
                  color: getPhaseColor(task), 
                  marginBottom: '0.25rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  backgroundColor: task.status === 'completed' ? '#f0f8f0' : 'transparent',
                  padding: '0.25rem',
                  borderRadius: '3px'
                }}>
                  <span>
                    {getPhaseIcon(task)} {task.name}
                    {task.status === 'active' && task.progress > 0 && (
                      <span style={{ marginLeft: '0.25rem', fontSize: '0.65rem' }}>
                        ({task.progress}%)
                      </span>
                    )}
                  </span>
                  {task.estimated_time_remaining && (
                    <span style={{ fontSize: '0.65rem', color: '#666' }}>
                      {task.estimated_time_remaining}
                    </span>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}
      
      {selected?.status === 'completed' && (
        <div style={{ marginTop:'1.25rem' }}>
          <div style={{
            padding:'.6rem .75rem',
            background:'#e6f9ed',
            border:'1px solid #bde7cb',
            borderRadius:'6px',
            fontSize:'.65rem',
            display:'flex',
            flexWrap:'wrap',
            gap:'0.75rem',
            alignItems:'center'
          }}>
            <strong style={{ fontSize:'.7rem', color:'#0b7a30' }}>✓ Assessment Phases Complete:</strong>
            <span>✓ Initialization</span>
            <span>✓ Document Processing</span>
            <span>✓ Corpus Assembly</span>
            <span>✓ Pillar Evaluation</span>
            <span>✓ Cross-Pillar Alignment</span>
            <span>✓ Synthesis</span>
            <span>✓ Finalization</span>
            {selected.crossPillarConflicts && (
              <span style={{ marginLeft:'auto', color:'#555' }}>Conflicts: {selected.crossPillarConflicts.length}</span>
            )}
            {selected.cohesiveRecommendations && selected.cohesiveRecommendations.length > 0 && (
              <span style={{ color:'#555' }}>Cohesive Recs: {selected.cohesiveRecommendations.length}</span>
            )}
            {typeof selected.overallArchitectureScore === 'number' && (
              <span style={{ color:'#004bcc', fontWeight:600 }}>Final Score: {selected.overallArchitectureScore}%</span>
            )}
          </div>
          <div style={{ fontSize:'.6rem', marginTop:'.4rem', color:'#444' }}>
            View detailed conflicts & recommendations in the Results tab.
          </div>
          {/* Cohesive Recommendations & Cross-Pillar Considerations (migrated from Scorecard) */}
          {selected.cohesiveRecommendations && selected.cohesiveRecommendations.length > 0 && (
            <div style={{ marginTop:'0.85rem', border:'1px solid #d0d7de', borderRadius:'6px', background:'#f6f8fa' }}>
              <div 
                onClick={() => setCohesiveExpanded(!cohesiveExpanded)}
                style={{
                  padding:'.55rem .7rem',
                  display:'flex',
                  justifyContent:'space-between',
                  alignItems:'center',
                  background:'#f6f8fa',
                  borderBottom: cohesiveExpanded ? '1px solid #d0d7de' : 'none',
                  cursor: 'pointer',
                  userSelect: 'none'
                }}>
                <span style={{ fontSize:'.7rem', fontWeight:600 }}>
                  {cohesiveExpanded ? '▼' : '▶'} Cohesive Recommendations (Synthesis)
                </span>
                <span style={{ fontSize:'.6rem', color:'#555' }}>{selected.cohesiveRecommendations.length} items</span>
              </div>
              {cohesiveExpanded && (
                <div style={{ padding:'.6rem .75rem' }}>
                  {selected.cohesiveRecommendations.map((rec, idx) => (
                  <div key={idx} style={{
                    background:'#fff',
                    border:'1px solid #e1e4e8',
                    borderRadius:'4px',
                    padding:'.5rem .6rem',
                    marginBottom:'.55rem'
                  }}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'.35rem' }}>
                      <strong style={{ fontSize:'.65rem' }}>{rec.title || rec.recommendation || 'Recommendation'}</strong>
                      {rec.priority && (
                        <span style={{
                          fontSize:'.55rem',
                          fontWeight:600,
                          background: rec.priority.toUpperCase() === 'CRITICAL' ? '#dc3545' : 
                                      rec.priority.toUpperCase() === 'HIGH' ? '#ff8c00' : 
                                      rec.priority.toUpperCase() === 'MEDIUM' ? '#ffa500' : 
                                      rec.priority.toUpperCase() === 'LOW' ? '#28a745' : '#004bcc',
                          color:'#fff',
                          padding:'.15rem .4rem',
                          borderRadius:'3px'
                        }}>{rec.priority}</span>
                      )}
                    </div>
                    {rec.reasoning && (
                      <div style={{ fontSize:'.55rem', color:'#333', marginBottom:'.3rem' }}>{rec.reasoning}</div>
                    )}
                    {(rec.recommendation || rec.details) && (
                      <div style={{ fontSize:'.55rem', color:'#0b7a30', marginBottom:'.3rem' }}>💡 {(rec.recommendation || rec.details)}</div>
                    )}
                    {Array.isArray((rec as any).crossPillarConsiderations) && (rec as any).crossPillarConsiderations.length > 0 && (
                      <div style={{
                        background:'#fffbe6',
                        border:'1px solid #ffe58f',
                        borderRadius:'4px',
                        padding:'.35rem .45rem'
                      }}>
                        <div style={{ fontSize:'.55rem', fontWeight:600, color:'#856404', marginBottom:'.2rem' }}>Cross-Pillar Considerations</div>
                        {(rec as any).crossPillarConsiderations.map((c:string,i:number)=>(
                          <div key={i} style={{ fontSize:'.5rem', color:'#856404', lineHeight:1.3 }}>• {c}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  ))}
                </div>
              )}
            </div>
          )}
          {/* Assessment Phase Details Panel */}
          <div style={{ marginTop:'1.1rem', border:'1px solid #e1e4e8', borderRadius:'6px', background:'#fff' }}>
            <div 
              onClick={() => setPhaseDetailsExpanded(!phaseDetailsExpanded)}
              style={{
                padding:'.6rem .75rem',
                borderBottom: phaseDetailsExpanded ? '1px solid #e1e4e8' : 'none',
                background:'#f6f8fa',
                display:'flex',
                justifyContent:'space-between',
                alignItems:'center',
                cursor: 'pointer',
                userSelect: 'none'
              }}>
              <strong style={{ fontSize:'.7rem' }}>
                {phaseDetailsExpanded ? '▼' : '▶'} Assessment Phase Details
              </strong>
              <span style={{ fontSize:'.55rem', color:'#555' }}>End-to-end agent activity summary</span>
            </div>
            {phaseDetailsExpanded && (
              <div style={{ padding:'.65rem .85rem', fontSize:'.6rem', lineHeight:1.35 }}>
                <div style={{ marginBottom:'.5rem' }}>
                <strong style={{ fontSize:'.6rem' }}>Initialization (0–5%)</strong>
                <div>Environment prepared, documents registered, basic metadata captured.</div>
              </div>
              <div style={{ marginBottom:'.5rem' }}>
                <strong style={{ fontSize:'.6rem' }}>Document Processing (5–15%)</strong>
                <div>Text extraction, cleanup (format normalization), and segmentation for semantic indexing.</div>
              </div>
              <div style={{ marginBottom:'.5rem' }}>
                <strong style={{ fontSize:'.6rem' }}>Corpus Assembly (15–20%)</strong>
                <div>Unified knowledge corpus built; embeddings & semantic references generated for each artifact slice.</div>
              </div>
              <div style={{ marginBottom:'.5rem' }}>
                <strong style={{ fontSize:'.6rem' }}>Pillar Evaluation (20–80%)</strong>
                <div>Parallel specialized agents score subcategories with evidence tracing and concept coverage detection.</div>
              </div>
              <div style={{ marginBottom:'.5rem' }}>
                <strong style={{ fontSize:'.6rem' }}>Cross-Pillar Alignment (80–90%)</strong>
                <div>Recommendations compared across pillars to surface conflicts, dependencies, or enabling synergies.</div>
                {selected.crossPillarConflicts && selected.crossPillarConflicts.length > 0 ? (
                  <div style={{ marginTop:'.35rem', border:'1px solid #ffe58f', background:'#fffbe6', borderRadius:'4px', padding:'.4rem .5rem' }}>
                    <div style={{ fontWeight:600, fontSize:'.55rem', color:'#856404', marginBottom:'.25rem' }}>Detected Conflicts & Dependencies ({selected.crossPillarConflicts.length})</div>
                    {selected.crossPillarConflicts.map((c:any,i:number)=>(
                      <div key={i} style={{ marginBottom:'.3rem' }}>
                        <div style={{ fontSize:'.55rem', fontWeight:600, color:'#856404' }}>{c.type === 'operational_enabler' ? '💡' : '⚠️'} {c.pillarA} ↔ {c.pillarB}</div>
                        <div style={{ fontSize:'.5rem', color:'#444' }}>{c.description}</div>
                        <div style={{ fontSize:'.5rem', fontStyle:'italic', color:'#0078d4' }}>Mitigation: {c.mitigation}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ marginTop:'.35rem', fontSize:'.55rem', color:'#0b7a30' }}>✓ All recommendations aligned; no conflicts detected.</div>
                )}
              </div>
              <div style={{ marginBottom:'.5rem' }}>
                <strong style={{ fontSize:'.6rem' }}>Synthesis (90–95%)</strong>
                <div>Cohesive recommendations consolidated, duplicates merged, cross-pillar considerations appended.</div>
              </div>
              <div style={{ marginBottom:'.5rem' }}>
                <strong style={{ fontSize:'.6rem' }}>Finalization (95–100%)</strong>
                <div>Scores normalized (if required), final architecture score computed, outputs persisted.</div>
              </div>
              {(() => {
                const conflictsCount = selected.crossPillarConflicts ? selected.crossPillarConflicts.length : 0;
                const cohesiveCount = selected.cohesiveRecommendations ? selected.cohesiveRecommendations.length : 0;
                const hasScore = typeof selected.overallArchitectureScore === 'number';
                const empty = conflictsCount === 0 && cohesiveCount === 0 && !hasScore;
                return (
                  <div style={{ marginTop:'.75rem', padding:'.5rem .6rem', background:'#f6f8fa', border:'1px solid #e1e4e8', borderRadius:'4px', display:'flex', flexWrap:'wrap', gap:'.6rem' }}>
                    {empty && (
                      <span style={{ fontSize:'.55rem', color:'#666' }}>No conflicts • No cohesive recommendations yet • Final score pending</span>
                    )}
                    {!empty && (
                      <>
                        <span style={{ fontSize:'.55rem', color:'#555' }}>Conflicts: {conflictsCount}</span>
                        <span style={{ fontSize:'.55rem', color:'#555' }}>Cohesive Recs: {cohesiveCount}</span>
                        <span style={{ fontSize:'.55rem', fontWeight:600, color: hasScore ? '#004bcc' : '#555' }}>
                          {hasScore ? `Final Score: ${selected.overallArchitectureScore}%` : 'Final Score: pending'}
                        </span>
                      </>
                    )}
                  </div>
                );
              })()}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisProgressTab;
