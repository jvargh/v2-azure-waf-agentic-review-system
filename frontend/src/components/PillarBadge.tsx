import React from 'react';
import { PillarScore } from '../types';

export interface PillarBadgeProps {
  pillar: string;
  score: number;
  scoreSource: 'floor' | 'evidence' | 'elevated';
  coveragePct: number;
  negativeMentions: number;
  confidence: 'Low' | 'Medium' | 'High';
}

// Utility to derive CSS class for primary badge tone
function toneClass(source: PillarBadgeProps['scoreSource'], coverage: number): string {
  if (source === 'floor') return 'badge-needs-evidence';
  if (source === 'evidence') {
    if (coverage < 60) return 'badge-evidence-low';
    if (coverage < 75) return 'badge-evidence-med';
    return 'badge-evidence-high';
  }
  // elevated
  if (coverage < 75) return 'badge-elevated-med';
  return 'badge-elevated-high';
}

function confidenceBorder(confidence: PillarBadgeProps['confidence']): string {
  switch (confidence) {
    case 'High': return 'conf-high';
    case 'Medium': return 'conf-medium';
    default: return 'conf-low';
  }
}

function gapIndicator(neg: number): React.ReactNode {
  if (neg === 0) return null;
  if (neg <= 2) return <span className="gap-dot" title="Minor gaps detected" />;
  return <span className="gap-alert" title="Multiple gaps flagged" />;
}

function buildTooltip(props: PillarBadgeProps): string {
  const lines: string[] = [];
  lines.push(`${props.pillar} Pillar`);
  lines.push(`Score: ${props.score} (source: ${props.scoreSource})`);
  lines.push(`Coverage: ${props.coveragePct.toFixed(1)}%`);
  lines.push(`Confidence: ${props.confidence}`);
  lines.push(`Gaps: ${props.negativeMentions === 0 ? 'none' : props.negativeMentions}`);
  // hint logic
  if (props.scoreSource === 'floor') {
    lines.push('Hint: Add concrete architecture details to raise evidence.');
  } else if (props.scoreSource === 'evidence' && props.coveragePct < 60) {
    lines.push('Hint: Broaden coverage across missing critical concepts.');
  } else if (props.scoreSource === 'elevated' && props.coveragePct >= 75) {
    lines.push('Strength: Strong evidence + architectural maturity.');
  }
  return lines.join('\n');
}

export const PillarBadge: React.FC<PillarBadgeProps> = (props) => {
  const tone = toneClass(props.scoreSource, props.coveragePct);
  const border = confidenceBorder(props.confidence);
  const tooltip = buildTooltip(props);
  return (
    <div className={`pillar-badge ${tone} ${border}`} title={tooltip}>
      <div className="pb-header">
        <span className="pb-name">{props.pillar}</span>
        {gapIndicator(props.negativeMentions)}
      </div>
      <div className="pb-score-row">
        <span className="pb-score">{props.score}</span>
        <span className="pb-coverage">{props.coveragePct.toFixed(0)}% cov</span>
      </div>
      <div className="pb-footer">
        <span className={`pb-source source-${props.scoreSource}`}>{props.scoreSource}</span>
        <span className={`pb-confidence conf-${props.confidence.toLowerCase()}`}>{props.confidence}</span>
      </div>
    </div>
  );
};

export default PillarBadge;
