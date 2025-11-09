// Priority ranking order (left to right)
export const PRIORITY_ORDER: Record<string, number> = {
  low: 1, Low: 1,
  medium: 2, Medium: 2,
  high: 3, High: 3,
  critical: 4, Critical: 4
};

export const PRIORITY_LABELS: Record<number, string> = {
  1: 'Low',
  2: 'Medium',
  3: 'High',
  4: 'Critical'
};

export const PRIORITY_COLOR: Record<number, string> = {
  1: '#28a745', // green
  2: '#ffc107', // yellow
  3: '#fd7e14', // orange
  4: '#dc3545'  // red
};

// Centralized horizontal band ranges for priority buckets used by visualization charts.
// Values chosen to provide consistent spacing across 0.3..4.0 X domain.
export interface PriorityBand { key: string; range: [number, number]; label: string; }
export const PRIORITY_BANDS: PriorityBand[] = [
  { key: 'low', range: [0.45, 0.95], label: 'LOW' },
  { key: 'medium', range: [1.30, 1.90], label: 'MEDIUM' },
  { key: 'high', range: [2.25, 2.80], label: 'HIGH' },
  { key: 'critical', range: [3.20, 3.70], label: 'CRITICAL' }
];

// Quick lookup map by rank for convenience (rank 1..4)
export const PRIORITY_BAND_BY_RANK: Record<number, [number, number]> = {
  1: PRIORITY_BANDS[0].range,
  2: PRIORITY_BANDS[1].range,
  3: PRIORITY_BANDS[2].range,
  4: PRIORITY_BANDS[3].range
};

/**
 * Stable deterministic jitter for vertical positioning
 * Returns a value between 0 and 1
 */
export function stableJitter(seed: string): number {
  let h = 0;
  for (let i = 0; i < seed.length; i++) {
    h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return (h % 1000) / 1000; // 0..0.999
}
