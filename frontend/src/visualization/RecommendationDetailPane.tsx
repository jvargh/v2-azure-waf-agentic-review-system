import React, { useEffect } from 'react';
import { Recommendation } from '../types';

interface Props {
  recommendations: Recommendation[];
  subcategory: string;
  aggregatedScore?: number;
  priority: string;
  onClose: () => void;
}

const RecommendationDetailPane: React.FC<Props> = ({ recommendations, subcategory, aggregatedScore, priority, onClose }) => {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);
  const priorityClass = (priority || 'medium').toLowerCase();
  const priorityColor = priorityClass === 'critical' ? '#dc3545' : priorityClass === 'high' ? '#fd7e14' : priorityClass === 'medium' ? '#ffc107' : '#28a745';
  const azureDocsMap: Record<string, string> = {
    'Reliability-Focused Design Foundations': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/simplify',
    'Identify and Rate User and System Flows': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/identify-flows',
    'Perform Failure Mode Analysis (FMA)': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/failure-mode-analysis',
    'Define Reliability and Recovery Targets': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/metrics',
    'Add Redundancy at Different Levels': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/redundancy',
    'Implement a Timely and Reliable Scaling Strategy': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/scaling',
    'Strengthen Resiliency with Self-Preservation and Self-Healing': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/self-preservation',
    'Test for Resiliency and Availability Scenarios': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/testing-strategy',
    'Implement Structured, Tested, and Documented Disaster Plans': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/disaster-recovery',
    'Measure and Model the Solution\'s Health Indicators': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/monitoring',
    'Establish a Security Baseline': 'https://learn.microsoft.com/en-us/azure/well-architected/security/establish-baseline',
    'Maintain a Secure Development Lifecycle': 'https://learn.microsoft.com/en-us/azure/well-architected/security/secure-development-lifecycle',
    'Classify and Label Data Sensitivity': 'https://learn.microsoft.com/en-us/azure/well-architected/security/data-classification',
    'Create Intentional Segmentation and Perimeters': 'https://learn.microsoft.com/en-us/azure/well-architected/security/segmentation',
    'Implement Conditional Identity and Access Management': 'https://learn.microsoft.com/en-us/azure/well-architected/security/identity-access',
    'Define standard practices to develop and operate workload': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-development-practices',
    'Formalize operational tasks': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-operations-tasks',
    'Formalize software ideation and planning': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-software-ideation',
    'Establish structured incident management': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/incident-response',
    'Automate repetitive tasks': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/automate-tasks',
    'Create a culture of financial responsibility': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/culture',
    'Create and maintain a cost model': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/cost-model',
    'Collect and review cost data': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/collect-review-cost-data',
    'Set spending guardrails': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/set-spending-guardrails',
    'Optimize component costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-component-costs',
    'Optimize flow costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-flow-costs',
    'Optimize data costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-data-costs',
    'Optimize code costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-code-costs',
    'Optimize personnel time': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-personnel-time',
    'Performance Targets & SLIs/SLOs': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/performance-targets',
    'Capacity & Demand Planning': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/capacity-planning',
    'Performance Testing & Benchmarking': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/performance-test',
    'Code & Runtime Optimization': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/optimize-code-infrastructure',
    'Critical Flow Optimization': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/prioritize-critical-flows',
    'Live Issue Triage & Remediation': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/continuous-performance-optimize'
  };
  const sourceUrl = azureDocsMap[subcategory] || null;

  const items = recommendations.map(r => {
    const scoreRefsTotal = r.scoreRefs ? Object.values(r.scoreRefs).reduce((a,b)=>a+b,0) : undefined;
    return { r, scoreRefsTotal };
  });

  return (
    <>
      <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(2px)', zIndex: 1000 }} />
      <div
        role="dialog"
        aria-modal="true"
        style={{
          position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: 'min(880px, 94vw)', maxHeight: '82vh',
          background: '#10141a', color: '#f0f3f6', borderRadius: '12px', boxShadow: '0 12px 40px rgba(0,0,0,0.45)', zIndex: 1001,
          display: 'flex', flexDirection: 'column', overflow: 'hidden', border: '1px solid #1f2733'
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'0.85rem 1.1rem', borderBottom:'1px solid #1f2733' }}>
          <h3 style={{ margin:0, fontSize:'1.05rem', fontWeight:600 }}>{subcategory} <span style={{ fontSize:'.75rem', fontWeight:400, marginLeft:'.5rem', color:'#7f8b96' }}>({items.length} recs)</span></h3>
          <div style={{ display:'flex', gap:'.5rem', alignItems:'center' }}>
            {aggregatedScore !== undefined && (
              <span style={{ fontSize:'.65rem', background:'#18222d', padding:'.25rem .45rem', borderRadius:'4px', border:'1px solid #253241', color:'#b9c4ce' }}>Score Σ {aggregatedScore}</span>
            )}
            <span style={{ padding: '.3rem .55rem', backgroundColor: priorityColor, color:'#fff', fontSize:'.65rem', fontWeight:600, borderRadius:'4px', letterSpacing:'.4px' }}>{priority} Priority</span>
            <button onClick={onClose} style={{ background:'none', border:'none', color:'#8896a8', fontSize:'1.4rem', cursor:'pointer', lineHeight:1 }} aria-label="Close">×</button>
          </div>
        </div>
        <div style={{ padding:'1rem 1.15rem', overflowY:'auto', flex:1 }}>
          <div style={{ marginBottom:'1.1rem' }}>
            <h5 style={{ fontSize:'.68rem', textTransform:'uppercase', letterSpacing:'.6px', color:'#90a4b7', margin:'0 0 .35rem' }}>Subcategory</h5>
            <div style={{ fontSize:'.8rem' }}>
              {sourceUrl ? <a href={sourceUrl} target="_blank" rel="noopener noreferrer" style={{ color:'#4aa8ff', textDecoration:'underline' }}>{subcategory}</a> : subcategory}
            </div>
          </div>
          <div style={{ marginBottom:'1.2rem' }}>
            <h5 style={{ fontSize:'.68rem', textTransform:'uppercase', letterSpacing:'.6px', color:'#90a4b7', margin:'0 0 .4rem' }}>Recommendations</h5>
            <div style={{ display:'flex', flexDirection:'column', gap:'.65rem' }}>
              {items.map(({ r, scoreRefsTotal }, idx) => {
                const rcPriorityClass = (r.priority || 'medium').toLowerCase();
                const rcColor = rcPriorityClass === 'critical' ? '#dc3545' : rcPriorityClass === 'high' ? '#fd7e14' : rcPriorityClass === 'medium' ? '#ffc107' : '#28a745';
                return (
                  <div key={idx} style={{ background:'#18222d', border:'1px solid #1f2733', borderRadius:'8px', padding:'.75rem .85rem' }}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', gap:'.75rem' }}>
                      <div style={{ flex:1 }}>
                        <div style={{ display:'flex', alignItems:'center', gap:'.5rem', flexWrap:'wrap', marginBottom:'.35rem' }}>
                          <span style={{ padding:'.25rem .5rem', background:rcColor, color:'#fff', fontSize:'.55rem', fontWeight:600, borderRadius:'4px', letterSpacing:'.4px' }}>{r.priority}</span>
                          {r.effort && <span style={{ padding:'.25rem .5rem', background:'#243041', color:'#d4d9e0', fontSize:'.55rem', fontWeight:600, borderRadius:'4px' }}>{r.effort} Effort</span>}
                          {scoreRefsTotal !== undefined && <span style={{ padding:'.25rem .5rem', background:'#243041', color:'#b9c4ce', fontSize:'.55rem', borderRadius:'4px' }}>Score {scoreRefsTotal}</span>}
                        </div>
                        <div style={{ fontSize:'.8rem', fontWeight:600, lineHeight:1.4 }}>{r.title}</div>
                        {(r.reasoning || r.insight) && <div style={{ fontSize:'.65rem', marginTop:'.4rem', lineHeight:1.5, color:'#c7d0d8' }}>{r.reasoning || r.insight}</div>}
                      </div>
                    </div>
                    {r.crossPillarConsiderations && r.crossPillarConsiderations.length > 0 && (
                      <div style={{ marginTop:'.55rem', background:'#142435', padding:'.55rem .6rem', borderRadius:'6px', border:'1px solid #203344' }}>
                        <div style={{ fontSize:'.58rem', fontWeight:600, marginBottom:'.3rem', color:'#4aa8ff' }}>Cross-Pillar Considerations</div>
                        {r.crossPillarConsiderations.map((c,i2)=>(<div key={i2} style={{ fontSize:'.55rem', lineHeight:1.4, color:'#d4d9e0' }}>• {c}</div>))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          {aggregatedScore !== undefined && (
            <div style={{ fontSize:'.55rem', color:'#7f8b96' }}>Aggregated score is the sum of individual recommendation scoreRefs totals (if provided).</div>
          )}
        </div>
        <div style={{ padding:'.6rem .9rem', borderTop:'1px solid #1f2733', display:'flex', justifyContent:'flex-end' }}>
          <button onClick={onClose} style={{ background:'#243041', color:'#e2e6ea', border:'1px solid #34485d', fontSize:'.7rem', padding:'.45rem .85rem', borderRadius:'4px', cursor:'pointer' }}>Close</button>
        </div>
      </div>
    </>
  );
};

export default RecommendationDetailPane;
