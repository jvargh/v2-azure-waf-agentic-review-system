import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, ResponsiveContainer, ReferenceArea } from 'recharts';
import { BubbleDatum, PillarDataset } from './types';
import { PRIORITY_BANDS } from './utils';

interface Props {
  dataset: PillarDataset;
  onBubbleClick: (bubble: BubbleDatum) => void;
}


const PillarBubbleChart: React.FC<Props> = ({ dataset, onBubbleClick }) => {
  const data = dataset.data; // static, no animation

  if (!data.length) {
    return <p style={{ fontSize:'.65rem', color:'#666' }}>No recommendations for this pillar.</p>;
  }

  return (
    <div className="pillar-viz-card" style={{ border:'1px solid #1c2833', borderRadius:'10px', background:'#0e151c', padding:'1rem', color:'#d8dee4' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'.5rem' }}>
        <h4 style={{ margin:0, fontSize:'.9rem', fontWeight:600 }}>{dataset.pillar}</h4>
        <div style={{ fontSize:'.55rem', opacity:.65 }}>Subcategories: {data.length}</div>
      </div>
      <div style={{ width:'100%', height:300 }}>
        <ResponsiveContainer>
          <ScatterChart margin={{ top:25, right:10, bottom:28, left:10 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="#22313f" />
            <XAxis type="number" dataKey="x" domain={[0.3,4.0]} tick={false}
              label={{ value:'← Priority →', position:'insideBottom', dy:14, fontSize:12, fill:'#7f8b96' }}
            />
            <YAxis type="number" dataKey="y" domain={[1,4]} hide />

            {/* Priority band labels */}
            {PRIORITY_BANDS.map(band => (
              <ReferenceArea key={band.key} x1={band.range[0]} x2={band.range[1]} y1={1} y2={4} ifOverflow="extendDomain"
                label={{
                  position:'top',
                  value: band.label,
                  fontSize:9,
                  fill:'#4aa8ff',
                  dy:-12
                }}
                strokeOpacity={0} fill="#142435" fillOpacity={0.04}
              />
            ))}

            <Scatter data={data} shape={(props: any) => {
              const { cx, cy, payload } = props;
              // Color by priorityRank (1..4) rather than x directly for flexibility
              const rankColorMap: Record<number,string> = {
                1: '#28a745', // low
                2: '#ffc107', // medium
                3: '#fd7e14', // high
                4: '#dc3545'  // critical
              };
              const color = rankColorMap[payload.priorityRank] || '#0078d4';
              return (
                <g onClick={() => onBubbleClick(payload)} style={{ cursor:'pointer' }}>
                  <circle cx={cx} cy={cy} r={payload.r} fill={color} fillOpacity={0.6} stroke={color} strokeWidth={1.4} />
                  {/* Font size tuned for new smaller radii range */}
                  {/* Increased number font sizing for readability while keeping bubble radius intact */}
                  <text x={cx} y={cy} textAnchor="middle" dominantBaseline="middle" fontSize={Math.max(10, Math.min(16, payload.r * 0.60))} fill="#fff" style={{ pointerEvents:'none', fontWeight:600 }}>
                    {payload.count}
                  </text>
                </g>
              );
            }} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default PillarBubbleChart;
