import { Recommendation } from '../types';

// Aggregated bubble datum representing a subcategory (recommendation.source)
export interface BubbleDatum {
  x: number;              // continuous horizontal position
  y: number;              // vertical position (non-semantic)
  r: number;              // bubble radius (size)
  subcategory: string;    // grouping key (recommendation.source)
  priority: string;       // highest priority among grouped recs
  priorityRank: number;   // numeric rank 1..4 for color mapping
  aggregatedScore?: number; // sum of scoreRefs across group
  count: number;          // number of recommendations in this subcategory
  recommendations: Recommendation[]; // all recs in the subcategory
  // Backward compatibility fields
  title: string;          // representative title (first recommendation)
  pillar: string;         // pillar name
  scoreRefTotal?: number; // retained for tooltip compatibility (same as aggregatedScore)
  recommendation?: Recommendation; // first recommendation (legacy consumers)
}

export interface ScoreboardMetrics {
  overall: number;
  totalRecs: number;
  criticalRecs: number;
  highRecs: number;
  mediumRecs: number;
  lowRecs: number;
}

export interface PillarDataset {
  pillar: string;
  data: BubbleDatum[];
}
