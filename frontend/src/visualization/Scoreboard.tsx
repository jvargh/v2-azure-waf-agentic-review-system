import React from 'react';
import { ScoreboardMetrics } from './types';

interface Props {
  metrics: ScoreboardMetrics;
}

const Scoreboard: React.FC<Props> = ({ metrics }) => {
  return (
    <div className="viz-scoreboard" style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(160px,1fr))', gap:'.75rem', margin:'1rem 0 2rem' }}>
      <div className="card" style={{ padding:'1rem' }}>
        <h4 style={{ margin:'0 0 .35rem', fontSize:'.7rem', letterSpacing:'.5px', textTransform:'uppercase', color:'#555' }}>Overall Score</h4>
        <div className="metric" style={{ fontSize:'1.7rem' }}>{metrics.overall}%</div>
      </div>
      <div className="card" style={{ padding:'1rem' }}>
        <h4 style={{ margin:'0 0 .35rem', fontSize:'.7rem', letterSpacing:'.5px', textTransform:'uppercase', color:'#555' }}>Recommendations</h4>
        <div className="metric" style={{ fontSize:'1.7rem' }}>{metrics.totalRecs}</div>
      </div>
      <div className="card" style={{ padding:'1rem' }}>
        <h4 style={{ margin:'0 0 .35rem', fontSize:'.7rem', letterSpacing:'.5px', textTransform:'uppercase', color:'#555' }}>Critical Recs</h4>
        <div className="metric" style={{ fontSize:'1.7rem', color:'#dc3545' }}>{metrics.criticalRecs}</div>
      </div>
      <div className="card" style={{ padding:'1rem' }}>
        <h4 style={{ margin:'0 0 .35rem', fontSize:'.7rem', letterSpacing:'.5px', textTransform:'uppercase', color:'#555' }}>High Recs</h4>
        <div className="metric" style={{ fontSize:'1.7rem', color:'#fd7e14' }}>{metrics.highRecs}</div>
      </div>
      <div className="card" style={{ padding:'1rem' }}>
        <h4 style={{ margin:'0 0 .35rem', fontSize:'.7rem', letterSpacing:'.5px', textTransform:'uppercase', color:'#555' }}>Medium Recs</h4>
        <div className="metric" style={{ fontSize:'1.7rem', color:'#ffc107' }}>{metrics.mediumRecs}</div>
      </div>
      <div className="card" style={{ padding:'1rem' }}>
        <h4 style={{ margin:'0 0 .35rem', fontSize:'.7rem', letterSpacing:'.5px', textTransform:'uppercase', color:'#555' }}>Low Recs</h4>
        <div className="metric" style={{ fontSize:'1.7rem', color:'#28a745' }}>{metrics.lowRecs}</div>
      </div>
    </div>
  );
};

export default Scoreboard;
