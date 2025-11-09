import React, { useMemo, useState } from 'react';
import { useAssessments } from '../context/AssessmentsContext';
import { PillarScore, Recommendation } from '../types';
import Scoreboard from './Scoreboard';
import PillarBubbleChart from './PillarBubbleChart';
import RecommendationDetailPane from './RecommendationDetailPane';
import { BubbleDatum, ScoreboardMetrics, PillarDataset } from './types';
import { PRIORITY_ORDER, PRIORITY_BAND_BY_RANK } from './utils';

// Helper to choose highest priority rank among a list
function highestPriority(recs: Recommendation[]): { priority: string; rank: number } {
  let bestRank = 1; // low
  let bestPriority = 'Low';
  recs.forEach(r => {
    const p = r.priority || 'Medium';
    const rank = PRIORITY_ORDER[p] || PRIORITY_ORDER[p.toLowerCase()] || 2;
    if (rank > bestRank) { bestRank = rank; bestPriority = p; }
  });
  return { priority: bestPriority, rank: bestRank };
}

const VisualizationTab: React.FC = () => {
  const { selected } = useAssessments();
  const pillarResults: PillarScore[] = selected?.pillarResults || selected?.pillarScores || [];
  const [selectedBubble, setSelectedBubble] = useState<BubbleDatum | null>(null);

  // Aggregate metrics for scoreboard at top
  const scoreboard: ScoreboardMetrics | null = useMemo(() => {
    if (!pillarResults.length) return null;
    const overall = selected?.overallArchitectureScore ?? (
      pillarResults.reduce((s, p) => s + (p.overallScore || p.score || 0), 0) / pillarResults.length
    );
    const allRecs: Recommendation[] = [];
    pillarResults.forEach(p => (p.recommendations || []).forEach(r => allRecs.push(r)));
    const totalRecs = allRecs.length;
    const norm = (p: string | undefined) => (p || '').toLowerCase();
    const criticalRecs = allRecs.filter(r => norm(r.priority) === 'critical').length;
    const highRecs = allRecs.filter(r => norm(r.priority) === 'high').length;
    const mediumRecs = allRecs.filter(r => norm(r.priority) === 'medium').length;
    const lowRecs = allRecs.filter(r => norm(r.priority) === 'low').length;
    return { overall: Math.round(overall), totalRecs, criticalRecs, highRecs, mediumRecs, lowRecs };
  }, [pillarResults, selected?.overallArchitectureScore]);

  // Build per-pillar aggregated bubble datasets (subcategory-level)
  const datasets: PillarDataset[] = useMemo(() => {
    // First pass: compute global maxCount across all pillars for uniform sizing
    let globalMaxCount = 1;
    pillarResults.forEach(pillar => {
      const recs = pillar.recommendations || [];
      const groups: Record<string, Recommendation[]> = {};
      recs.forEach(r => {
        const key = (r.source || 'Unknown').trim() || 'Unknown';
        if (!groups[key]) groups[key] = [];
        groups[key].push(r);
      });
      Object.values(groups).forEach(list => {
        if (list.length > globalMaxCount) globalMaxCount = list.length;
      });
    });

    return pillarResults.map(pillar => {
      const recs = pillar.recommendations || [];
      // Group by subcategory AND priority (so each bubble = one subcategory + one priority)
      const groups: Record<string, Recommendation[]> = {};
      recs.forEach(r => {
        const subcategory = (r.source || 'Unknown').trim() || 'Unknown';
        const priority = (r.priority || 'Medium').toLowerCase();
        const key = `${subcategory}|${priority}`;
        if (!groups[key]) groups[key] = [];
        groups[key].push(r);
      });
      // compute aggregated scores
      const aggregatedScores = Object.entries(groups).map(([key, list]) => {
        const [subcategory] = key.split('|');
        let sumScoreRefs = 0;
        list.forEach(r => {
          if (r.scoreRefs) sumScoreRefs += Object.values(r.scoreRefs).reduce((a, b) => a + b, 0);
        });
        return { subcategory, list, aggregatedScore: sumScoreRefs };
      });
      const maxAgg = Math.max(1, ...aggregatedScores.map(a => a.aggregatedScore));

      // Use centralized priority band map
      const rangeMap = PRIORITY_BAND_BY_RANK;

      const bubbles: BubbleDatum[] = [];

      // Pre-group by priority rank to assign evenly spaced vertical positions per band
      const grouped: Record<number, typeof aggregatedScores> = { 1: [], 2: [], 3: [], 4: [] };
      aggregatedScores.forEach(a => { grouped[highestPriority(a.list).rank].push(a); });

      Object.entries(grouped).forEach(([rankStr, arr]) => {
        const rank = Number(rankStr);
        if (!arr.length) return;
        // Sort by count descending inside band
        arr.sort((a, b) => b.list.length - a.list.length);
        const [minX, maxX] = rangeMap[rank] || [0.6, 1.6];
        const availMinY = 1.4;
        const availMaxY = 3.7;
        
        arr.forEach((entry, i) => {
          const { subcategory, list, aggregatedScore } = entry;
          const { priority } = highestPriority(list);
          const count = list.length;
          // Bubble radius in pixels (adjusted: lower max to reduce overflow)
          // If all counts ==1 (globalMaxCount==1) give modest radius for clarity
          const MIN_R = 10; // slightly larger base for legibility
          const MAX_R = 20; // reduced from 32 to fit vertical bounds
          const r = (globalMaxCount === 1)
            ? 14 // uniform when no variation
            : Math.max(MIN_R, Math.min(MAX_R, MIN_R + (count / globalMaxCount) * (MAX_R - MIN_R)));
          
          // Calculate spacing needed in coordinate units (conversion from pixel radius)
          const rInUnits = r / 60.0; // adjusted unit conversion for smaller radii
          const TOP_PAD = 0.15; // axis units padding
          const BOTTOM_PAD = 0.15;
          // Even vertical layout baseline
          const ySpacing = Math.max(0.28, rInUnits * 2.2);
          let y = arr.length === 1 ? 2.5 : (availMinY + i * ySpacing);
          if (y > (availMaxY - BOTTOM_PAD)) {
            // Wrap to start plus jitter to discourage direct overlap
            const wrapIndex = (i % 4);
            y = availMinY + wrapIndex * ySpacing + (wrapIndex * 0.02);
          }
          // Clamp with padding so circle stays inside chart vertically
          y = Math.max(availMinY + TOP_PAD, Math.min(availMaxY - BOTTOM_PAD, y));
          
          // Horizontal placement: spread across band based on index
          const xSpacing = (maxX - minX) / Math.max(1, Math.ceil(arr.length / 4));
          let x = minX + (Math.floor(i / 4) * xSpacing) + xSpacing / 2;
          x = Math.max(minX + 0.1, Math.min(maxX - 0.1, x));
          
          bubbles.push({
            x,
            y,
            r,
            subcategory,
            priority,
            priorityRank: rank,
            aggregatedScore: aggregatedScore || undefined,
            count: list.length,
            recommendations: list,
            title: list[0]?.title || subcategory,
            pillar: pillar.pillar,
            scoreRefTotal: aggregatedScore || undefined,
            recommendation: list[0]
          });
        });
      });

      // Simple overlap mitigation pass: adjust positions within band so overlap area <=25%
      // Convert 25% area threshold to distance threshold: two circles of radius r1,r2 have >25% overlap roughly when center distance < 0.75*min(r1,r2)
      // We work in pixel space approximation using X domain scaling heuristic.
      const adjusted = bubbles.map(b => ({ ...b }));
      const toPixelsX = (x: number) => x * 100; // heuristic scale (domain ~0.3..4.0)
      const toPixelsY = (y: number) => y * 75;  // heuristic scale (domain 1..4 mapped to 300px height)
      for (let i = 0; i < adjusted.length; i++) {
        for (let j = i + 1; j < adjusted.length; j++) {
          const a = adjusted[i];
          const b = adjusted[j];
          if (a.priorityRank !== b.priorityRank) continue; // only resolve within same band
          const dx = toPixelsX(a.x) - toPixelsX(b.x);
          const dy = toPixelsY(a.y) - toPixelsY(b.y);
          const dist = Math.sqrt(dx*dx + dy*dy);
          const minR = Math.min(a.r, b.r);
          const threshold = 0.75 * minR; // center distance threshold
          if (dist < threshold && dist > 0) {
            // Push them apart vertically slightly inside bounds
            const push = (threshold - dist) / threshold * 0.08; // small push factor in axis units
            const direction = dy >= 0 ? 1 : -1;
            const [minX, maxX] = rangeMap[a.priorityRank];
            a.y = Math.min(3.7 - 0.15, Math.max(1.4 + 0.15, a.y + direction * push));
            b.y = Math.min(3.7 - 0.15, Math.max(1.4 + 0.15, b.y - direction * push));
            // Optional slight horizontal jitter within band
            const jitter = push * 0.6;
            a.x = Math.min(maxX - 0.12, Math.max(minX + 0.12, a.x + jitter));
            b.x = Math.min(maxX - 0.12, Math.max(minX + 0.12, b.x - jitter));
          }
        }
      }

      return { pillar: pillar.pillar, data: adjusted };
    });
  }, [pillarResults]);

  const handleBubbleClick = (bubble: BubbleDatum) => {
    setSelectedBubble(bubble);
  };

  if (!pillarResults.length) {
    return <p style={{ fontSize:'.75rem', color:'#555' }}>Visualization will appear after analysis completes.</p>;
  }

  return (
    <div>
      <h3>Architecture Insights Visualization</h3>
      {scoreboard && <Scoreboard metrics={scoreboard} />}

      <div className="pillar-viz-grid" style={{ display:'grid', gap:'1.25rem', gridTemplateColumns:'repeat(auto-fit,minmax(380px,1fr))' }}>
        {datasets.map(ds => (
          <PillarBubbleChart key={ds.pillar} dataset={ds} onBubbleClick={handleBubbleClick} />
        ))}
      </div>
      
      <div style={{ marginTop:'2rem', fontSize:'.6rem', color:'#666' }}>
        Bubble size reflects the number of recommendations per subcategory (scaled, capped). Horizontal axis: Low → Medium → High → Critical. Overlap minimized to preserve readability. Click a bubble for details.
      </div>

      {selectedBubble && (
        <RecommendationDetailPane 
          recommendations={selectedBubble.recommendations}
          subcategory={selectedBubble.subcategory}
          aggregatedScore={selectedBubble.aggregatedScore}
          priority={selectedBubble.priority}
          onClose={() => setSelectedBubble(null)} 
        />
      )}
    </div>
  );
};

export default VisualizationTab;
