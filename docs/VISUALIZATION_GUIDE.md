# Conservative Scoring Tuning Guide

This guide shows you how to adjust the scoring algorithm to make it more or less conservative. All changes are made in `backend/server.py` in the `_calculate_conservative_score` function (starting around line 816).

---

## 🎯 Quick Reference: Making Scoring MORE Conservative

To make scoring stricter (lower scores), increase these penalties or decrease these bonuses:

| Change | Current Value | Make More Conservative | Effect |
|--------|---------------|------------------------|--------|
| **Density Multiplier** (small docs) | 0.35 | → 0.25 | Penalize small documentation more |
| **Negative Mention Penalty** | 0.015 per mention | → 0.025 | Harsher penalty for gaps |
| **Critical Gap Penalty** | min(0.25, count/25) | → min(0.35, count/20) | Stronger penalty for critical gaps |
| **Missing Critical Deduction** | 3 points per missing | → 5 points per missing | Bigger penalty for missing concepts |
| **Low Critical Coverage** | 30% penalty (<50% cov) | → 40% penalty | Penalize incomplete coverage more |
| **Clean Bonus** | 15% boost (no gaps) | → 10% boost | Reduce reward for clean docs |
| **Coverage Gates** | <50%=cap70, <60%=cap75 | → <60%=cap70, <70%=cap75 | Lower score ceilings |
| **Advanced Practice Gate** | <1=cap80, <2=cap85 | → <2=cap75, <3=cap80 | Require more advanced practices |
| **Evidence Floor** | 15-32 range | → 10-25 range | Lower minimum scores |

---

## 📍 Detailed Parameter Locations

### 1. **Corpus Density Multipliers** (Lines ~1067-1074)
Controls how document size affects scoring.

```python
# CURRENT (Balanced)
if corpus_size < 800:
    density_multiplier = 0.35  # very small doc
elif corpus_size < 2500:
    density_multiplier = 0.7   # medium doc
else:
    density_multiplier = 1.0   # large doc

# MORE CONSERVATIVE (harsher on small docs)
if corpus_size < 1000:
    density_multiplier = 0.25  # penalize small docs more
elif corpus_size < 3000:
    density_multiplier = 0.6   # raise threshold
else:
    density_multiplier = 1.0

# LESS CONSERVATIVE (more forgiving)
if corpus_size < 600:
    density_multiplier = 0.5   # less harsh on small docs
elif corpus_size < 2000:
    density_multiplier = 0.8   # lower threshold
else:
    density_multiplier = 1.0
```

---

### 2. **Depth Factor** (Lines ~1089-1099)
Rewards implementation details, metrics, and advanced practices.

```python
# CURRENT (Balanced)
depth_factor = 0.6
if avg_sentence_len > 60:
    depth_factor += 0.15
if impl_hits >= 5:
    depth_factor += 0.15
if metric_pairs >= 3:
    depth_factor += 0.15
if advanced_hits >= 3:
    depth_factor += 0.1
depth_factor = min(depth_factor, 1.15)

# MORE CONSERVATIVE (harder to get depth bonus)
depth_factor = 0.5  # lower base
if avg_sentence_len > 80:  # require longer sentences
    depth_factor += 0.1   # smaller bonus
if impl_hits >= 7:     # require more implementation verbs
    depth_factor += 0.1
if metric_pairs >= 5:  # require more metrics
    depth_factor += 0.1
if advanced_hits >= 5: # require more advanced practices
    depth_factor += 0.05
depth_factor = min(depth_factor, 1.0)  # lower ceiling

# LESS CONSERVATIVE (easier to get depth bonus)
depth_factor = 0.7
if avg_sentence_len > 40:
    depth_factor += 0.2
if impl_hits >= 3:
    depth_factor += 0.2
if metric_pairs >= 2:
    depth_factor += 0.2
if advanced_hits >= 2:
    depth_factor += 0.15
depth_factor = min(depth_factor, 1.3)  # higher ceiling
```

---

### 3. **Negative Mention Penalties** (Lines ~1145-1165)
Penalizes documentation that mentions gaps/issues.

```python
# CURRENT (Softened)
if negative_mentions > 3:
    negative_penalty = min(0.50, (negative_mentions - 3) / 80)
    adjusted_score = int(adjusted_score * (1 - negative_penalty))
elif negative_mentions > 0:
    negative_penalty = negative_mentions * 0.015  # minor penalty
    adjusted_score = int(adjusted_score * (1 - negative_penalty))

# MORE CONSERVATIVE (harsher penalties)
if negative_mentions > 2:  # trigger earlier
    negative_penalty = min(0.60, (negative_mentions - 2) / 60)  # stronger
    adjusted_score = int(adjusted_score * (1 - negative_penalty))
elif negative_mentions > 0:
    negative_penalty = negative_mentions * 0.025  # bigger minor penalty
    adjusted_score = int(adjusted_score * (1 - negative_penalty))

# LESS CONSERVATIVE (lighter penalties)
if negative_mentions > 5:  # trigger later
    negative_penalty = min(0.40, (negative_mentions - 5) / 100)
    adjusted_score = int(adjusted_score * (1 - negative_penalty))
elif negative_mentions > 0:
    negative_penalty = negative_mentions * 0.01
    adjusted_score = int(adjusted_score * (1 - negative_penalty))
```

---

### 4. **Clean Bonus** (Lines ~1167-1173)
Rewards documentation with no gaps and good coverage.

```python
# CURRENT (Moderate boost)
if coverage_pct > 70 and corpus_size > 500:
    adjusted_score = min(100, int(adjusted_score * 1.15))  # 15% boost

# MORE CONSERVATIVE (smaller bonus, higher requirements)
if coverage_pct > 80 and corpus_size > 800:  # stricter
    adjusted_score = min(100, int(adjusted_score * 1.10))  # only 10% boost

# LESS CONSERVATIVE (bigger bonus, easier requirements)
if coverage_pct > 60 and corpus_size > 300:
    adjusted_score = min(100, int(adjusted_score * 1.25))  # 25% boost
```

---

### 5. **Critical Gap Penalty** (Lines ~1198-1207)
Penalizes specific critical implementation gaps.

```python
# CURRENT (Softened)
if critical_gap_count > 3:
    critical_penalty = min(0.25, critical_gap_count / 25)
    adjusted_score = int(adjusted_score * (1 - critical_penalty))

# MORE CONSERVATIVE (stricter)
if critical_gap_count > 2:  # trigger earlier
    critical_penalty = min(0.35, critical_gap_count / 20)  # bigger penalty
    adjusted_score = int(adjusted_score * (1 - critical_penalty))

# LESS CONSERVATIVE (lighter)
if critical_gap_count > 5:
    critical_penalty = min(0.20, critical_gap_count / 30)
    adjusted_score = int(adjusted_score * (1 - critical_penalty))
```

---

### 6. **Missing Critical Concept Deduction** (Lines ~1210-1218)
Direct point deduction for each missing critical concept.

```python
# CURRENT (Softened)
missing_critical = critical_total - critical_found
if missing_critical > 0:
    adjusted_score = max(0, adjusted_score - int(missing_critical * 3))  # 3 pts per

# MORE CONSERVATIVE (harsher)
if missing_critical > 0:
    adjusted_score = max(0, adjusted_score - int(missing_critical * 5))  # 5 pts per

# LESS CONSERVATIVE (lighter)
if missing_critical > 0:
    adjusted_score = max(0, adjusted_score - int(missing_critical * 2))  # 2 pts per
```

---

### 7. **Low Critical Coverage Penalty** (Lines ~1219-1227)
Applies when less than 50% of critical concepts are covered.

```python
# CURRENT (30% penalty)
if (critical_found / critical_total) < 0.5:
    adjusted_score = int(adjusted_score * 0.70)  # 30% penalty

# MORE CONSERVATIVE (40% penalty)
if (critical_found / critical_total) < 0.6:  # trigger at 60% instead of 50%
    adjusted_score = int(adjusted_score * 0.60)  # 40% penalty

# LESS CONSERVATIVE (20% penalty)
if (critical_found / critical_total) < 0.4:  # only trigger at 40%
    adjusted_score = int(adjusted_score * 0.80)  # 20% penalty
```

---

### 8. **Coverage-Based Score Caps** (Lines ~1230-1235)
Maximum scores based on concept coverage percentage.

```python
# CURRENT (Moderate gates)
max_allowed = 100
if coverage_pct < 50:
    max_allowed = min(max_allowed, 70)
elif coverage_pct < 60:
    max_allowed = min(max_allowed, 75)

# MORE CONSERVATIVE (stricter caps)
max_allowed = 100
if coverage_pct < 60:
    max_allowed = min(max_allowed, 65)
elif coverage_pct < 70:
    max_allowed = min(max_allowed, 70)
elif coverage_pct < 80:
    max_allowed = min(max_allowed, 80)

# LESS CONSERVATIVE (looser caps)
max_allowed = 100
if coverage_pct < 40:
    max_allowed = min(max_allowed, 75)
elif coverage_pct < 50:
    max_allowed = min(max_allowed, 85)
```

---

### 9. **Advanced Practice Gates** (Lines ~1236-1239)
Caps scores based on presence of advanced practices.

```python
# CURRENT (Moderate)
if advanced_hits < 1:
    max_allowed = min(max_allowed, 80)
elif advanced_hits < 2:
    max_allowed = min(max_allowed, 85)

# MORE CONSERVATIVE (require more advanced practices)
if advanced_hits < 2:
    max_allowed = min(max_allowed, 75)
elif advanced_hits < 3:
    max_allowed = min(max_allowed, 80)
elif advanced_hits < 4:
    max_allowed = min(max_allowed, 85)

# LESS CONSERVATIVE (fewer requirements)
if advanced_hits < 1:
    max_allowed = min(max_allowed, 85)
```

---

### 10. **Metrics Gate** (Lines ~1240-1241)
Caps score based on quantitative metrics presence.

```python
# CURRENT
if metric_pairs < 3:
    max_allowed = min(max_allowed, 90)

# MORE CONSERVATIVE
if metric_pairs < 4:
    max_allowed = min(max_allowed, 85)
elif metric_pairs < 2:
    max_allowed = min(max_allowed, 75)

# LESS CONSERVATIVE
if metric_pairs < 2:
    max_allowed = min(max_allowed, 92)
```

---

### 11. **Evidence Floor** (Lines ~1247-1266)
Minimum score boost for very low evidence-based scores.

```python
# CURRENT (Moderate floor, scaled)
if adjusted_score <= 8:
    floor = 15
elif adjusted_score <= 15:
    floor = 15 + int((adjusted_score - 8) * 0.5)
elif adjusted_score <= 25:
    floor = 19 + int((adjusted_score - 15) * 0.6)
elif adjusted_score <= 35:
    floor = 25 + int((adjusted_score - 25) * 0.7)
else:
    floor = 32

# MORE CONSERVATIVE (lower floors)
if adjusted_score <= 5:
    floor = 10
elif adjusted_score <= 15:
    floor = 10 + int((adjusted_score - 5) * 0.4)
elif adjusted_score <= 25:
    floor = 14 + int((adjusted_score - 15) * 0.5)
else:
    floor = 20

# LESS CONSERVATIVE (higher floors)
if adjusted_score <= 10:
    floor = 20
elif adjusted_score <= 20:
    floor = 20 + int((adjusted_score - 10) * 0.6)
else:
    floor = 26 + int((adjusted_score - 20) * 0.8)
```

---

## 🔧 Example: Making Cost Optimization More Conservative

Based on your question about the Cost Optimization penalty, here's how to make it more conservative so support cases have less negative impact:

```python
# OPTION 1: Reduce negative mention penalty
# Line ~1155 - change from:
negative_penalty = negative_mentions * 0.015
# To:
negative_penalty = negative_mentions * 0.010  # 33% lighter penalty

# OPTION 2: Increase threshold for negative mentions
# Line ~1151 - change from:
if negative_mentions > 3:
# To:
if negative_mentions > 5:  # require more mentions before heavy penalty

# OPTION 3: Filter support case negative mentions
# Add to positive_negations list (line ~983):
positive_negations = [
    "no public", "no internet", "no external access", "no direct access",
    "no single point", "no hardcoded", "no plaintext", "no unencrypted",
    "no manual", "no downtime", "zero downtime", "no data loss",
    "cost overrun", "budget overrun"  # ADD THESE - treat cost issues as observations not gaps
]
```

---

## 🎚️ Preset Configurations

### STRICT MODE (Very Conservative)
```python
# Density
density_multiplier = 0.25 (small), 0.6 (medium), 1.0 (large)
# Depth
depth_factor max = 1.0
# Penalties
negative_penalty = 0.025 per mention
critical_gap_penalty = min(0.35, count/20)
missing_critical = 5 points each
low_coverage = 40% penalty
# Gates
coverage <60% = cap 65, <70% = cap 70
advanced <2 = cap 75, <3 = cap 80
```

### BALANCED MODE (Current Settings)
Current values as shown above.

### LENIENT MODE (Less Conservative)
```python
# Density
density_multiplier = 0.5 (small), 0.8 (medium), 1.0 (large)
# Depth
depth_factor max = 1.3
# Penalties
negative_penalty = 0.01 per mention
critical_gap_penalty = min(0.20, count/30)
missing_critical = 2 points each
low_coverage = 20% penalty (only <40% coverage)
# Gates
coverage <40% = cap 75, <50% = cap 85
advanced <1 = cap 85
```

---

## 🧪 Testing Your Changes

After making changes, test with:

```bash
# Run scoring validation
python validate_strict_scoring.py

# Test on existing assessment
python analyze_cost_scoring.py

# Compare with/without support cases
python compare_support_cases.py

# Rescore all assessments
python apply_scoring_breakdown.py
```

---

## 📊 Monitoring Score Distribution

To see if your changes are working as intended, check:

1. **Score Range**: Are scores spread across 0-100 or clustered?
2. **Breakdown Steps**: Look at `scoring_breakdown.steps` to see which penalties triggered
3. **Coverage vs Score**: Compare `coverage_pct` to `overall_score` - should be correlated but not 1:1
4. **Confidence Levels**: High confidence should only appear with substantial evidence

Example check:
```python
import requests
r = requests.get('http://localhost:8000/api/assessments/assess_1762503071')
data = r.json()
for p in data['pillar_results']:
    bd = p['scoring_breakdown']
    print(f"{p['pillar']}: score={p['overall_score']}, coverage={bd['final']['coverage_pct']}%")
    for step in bd['steps']:
        print(f"  {step['step']}: {step.get('before', 'N/A')} → {step['after']}")
```

---

## 💡 Recommendations

- **Start small**: Adjust one parameter at a time
- **Test frequently**: Run comparisons after each change
- **Document changes**: Note why you made each adjustment
- **Monitor trends**: Track average scores over time
- **Collect feedback**: Ask users if scores feel right

The current "balanced" settings aim for:
- Evidence-rich docs with good coverage: 80-100
- Decent docs with some gaps: 60-80
- Weak docs or major gaps: 40-60
- Insufficient evidence: <40

---

## 📈 Visualization Layout Guide (Scorecard + Bubble Panels)

This section documents the new Visualization tab that complements the textual scorecard. It provides at-a-glance architecture insights using a top scoreboard pane and per-pillar bubble charts.

### 1. Top Scoreboard Pane
Displays key aggregate metrics across the assessed architecture. Each metric is shown in a compact card.

Recommended metrics (all derived from `selected.assessment` in the frontend):
- **Overall Score**: `overallArchitectureScore` or average of pillar scores.
- **Recommendations**: Total count of all pillar recommendations.
- **Critical Recs**: Count of recommendations whose priority = Critical.
- **Avg Coverage**: Mean of `coveragePct` across pillars (if provided by backend).
- **Confidence**: Rounded average confidence level (Low / Medium / High) inferred from pillar confidence or score.

You can extend with additional metrics later (e.g., negative mentions, gap density, advanced practice hits) by pushing more diagnostic fields into each `PillarScore` from the backend and aggregating similarly.

### 2. Pillar Bubble Panels
Each pillar gets a box containing a bubble chart of its recommendations. The chart layout:
- **X-Axis (Left → Right)**: Priority buckets in order Low, Medium, High, Critical.
- **Y-Axis**: Vertical jitter only (no semantic meaning) to spread bubbles and reduce overlap.
- **Bubble Size**: Relative recommendation weight. Currently based on the sum of `scoreRefs` (if present) or a fallback sizing per priority rank.
- **Bubble Color**: Encodes priority (Low = green, Medium = yellow, High = orange, Critical = red) with increasing intensity.
- **Bubble Label**: First letter of priority (L / M / H / C) for quick scanning.

If `scoreRefs` are absent for a recommendation, the component falls back to a size heuristic: `20 + priorityRank * 5`. To make bubble size more meaningful, you can add a numeric field (e.g. `impactScore` or `evidenceWeight`) to recommendation objects in the backend.

### 3. Data Contract (Frontend Assumptions)
For visualization the frontend currently expects each `Recommendation` to have:
- `priority`: one of Low | Medium | High | Critical (case-insensitive)
- `title`: short text used in tooltip
- `scoreRefs` (optional): numeric map whose summed values approximate contribution magnitude

Optional enhancements:
- Add `effort` as border style (e.g. dotted for High Effort)
- Add `pillar` color theme customization (distinct palette per pillar when many recommendations share priority)

### 4. Adding More Diagnostic Dimensions
You can evolve the bubble chart to encode additional diagnostic signals:
- **Stroke pattern** for recommendations with cross-pillar considerations
- **Halo / glow** for critical recommendations with low effort (quick wins)
- **Inner icon** for recommendations referencing security/privacy concerns

Extend the `Recommendation` interface and adjust the `BubbleDatum` mapping accordingly.

### 5. Backend Alignment (Optional)
To make bubble sizing truly reflect scoring mechanics, supply a new numeric field in each recommendation such as `weight` or `scoreContribution` derived from conservative scoring steps. This prevents front-end heuristics from drifting from real scoring logic.

Example backend addition (pseudo‑Python inside scoring pipeline):
```python
rec['scoreContribution'] = int(sum(score_refs.values()))  # already aggregated
```
Then map `rec.scoreContribution` directly to radius scaling in the visualization.

### 6. Accessibility & Usability Notes
- Provide a tooltip with: Title, Priority, Score Weight (if present).
- Maintain sufficient color contrast (reds and greens over dark backgrounds need WCAG AA). Consider optional dark theme adjustments.
- Ensure keyboard focus: future enhancement can add a list view mirroring chart items for screen reader compatibility.

### 7. Performance Considerations
- With dozens of recommendations per pillar Recharts remains performant. If scaling to hundreds, consider canvas-based libraries (e.g. `echarts`, `visx`, or direct D3 canvas).
- Memoize dataset computation to avoid unnecessary re-renders (`useMemo` already employed).

### 8. Future Extensions
- **Time Slider**: Plot recommendations over time if historical assessments are aggregated.
- **Filtering**: Toggle visibility by priority or effort.
- **Drilldown**: Clicking a bubble could open a side panel with full reasoning and cross-pillar considerations.

This visualization aims to give immediate prioritization cues: scan left-to-right for escalation, and scan bubble size for relative magnitude of impact or evidence weight.

---

### 9. Layout Refinements (Containment, Motion, Modal)

New interaction & layout specifications implemented (Nov 2025):

1. Bubble Containment & Spacing
    - Bubbles are now guaranteed to stay fully inside the chart area (domain expanded to 0.5 → 4.5 on X and clamped 0.7 → 4.3 on Y).
    - Per‑priority vertical stacking algorithm groups recommendations by priority rank and distributes them evenly within the usable vertical span.
    - Largest bubbles are placed first to minimize later overlap; dynamic step size adapts to bubble radius and total count in a column.
    - Radius capped (≤55px) to avoid clipping against chart boundaries.

2. Overlap Reduction Strategy
    - Instead of free jitter (which produced off‑screen or highly overlapping clusters), stacking + minimal deterministic jitter (±0.075 on Y) yields readable columns.
    - This keeps similar priority items visually comparable while reducing occlusion without invoking heavy force simulations.

3. Subtle Ambient Motion
    - A lightweight interval applies a tiny vertical drift (≈ ±0.02–0.14 Y units) every ~3.8s alternating direction per index.
    - Goal: prevent a “static infographic” feel while avoiding distraction; motion is clamped within containment bounds.
    - Implementation note: data is copied into local animated state; each tick maps to a constrained Y adjustment.

4. Centered Recommendation Modal
    - Detail view now appears as a centered modal (dark theme) with backdrop instead of a right-edge drawer.
    - Scrollable content container (max-height 80vh) preserves context; ESC/Backdrop click closes (backdrop click currently implemented; ESC optional future enhancement).
    - Modal is declared with role="dialog" and aria-modal="true"; focus management can be added later (planned enhancement).

5. Accessibility & Future Enhancements
    - Planned: keyboard focus trap, initial focus on close button, and ARIA labelling linking heading id.
    - Possible future: toggle to disable motion for reduced motion user preference.

6. Design Rationale
    - Containment prevents UX regressions on small screens and when many critical items accumulate.
    - Motion adds liveliness without requiring continuous animation frames (interval-based, low CPU cost).
    - Centered modal emphasizes deep-dive content parity with other analysis surfaces while avoiding horizontal layout shift.

7. Extension Hooks
    - Stacking algorithm can be swapped with a lightweight collision relaxation pass if future datasets exceed vertical density thresholds.
    - Drift interval can be disabled or replaced with a CSS transition system keyed on recomputed y positions for deterministic reflows.

Implementation references: see `VisualizationTab.tsx` (dataset construction & stacking), `PillarBubbleChart.tsx` (animation / domain adjustments), and `RecommendationDetailPane.tsx` (modal pattern).

---
## 10. Directional Priority Layout & Subcategory Aggregation (In Progress – Nov 2025)

This section documents the next evolution of the bubble charts: a horizontally biased, directionally meaningful priority flow and subcategory aggregation. Instead of one bubble per recommendation stacked vertically, we now render one bubble per subcategory (derived from `recommendation.source`) and list all recommendations for that subcategory inside a unified detail modal.

### 10.1 Goals
1. Remove rigid vertical stacking columns – allow organic horizontal spread.
2. Encode directional flow: Medium (and Low) originate left; High cluster near center; Critical originate right – all subtly drift inward over time (future enhancement) while preserving containment.
3. Aggregate recommendations per subcategory so bubble size reflects cumulative value rather than single-item randomness.
4. Provide clear top legend: `Medium` (far left), centered `← Priority →`, `Critical` (far right). Low priority items share the far-left zone with Medium but are visually smaller / lighter.
5. Make bubble radius proportional to an aggregated numeric signal (interim: sum of `scoreRefs` across recommendations in that subcategory). Future: replace with backend-provided `subcategoryScore` or `scoreContribution`.

### 10.2 Aggregation Logic
Grouping key: `rec.source` (string). For each pillar:
```
subcatGroups = Map<source, Recommendation[]>
priorityRank = max( PRIORITY_ORDER[rec.priority] ) among group members
aggregatedScore = Σ(scoreRefs values) across all recs in group (skipping missing maps)
count = number of recommendations in the group
```
If a group contains mixed priorities, the bubble’s priority is the highest (Critical > High > Medium > Low) to guarantee worst-case visibility.

### 10.3 Radius Formula (Interim Normalization)
Let `maxAgg = max(aggregatedScore)` for all groups in the pillar (≥ 1). For each group:
```
base = 20
scale = 35
radius = aggregatedScore > 0 ? base + (aggregatedScore / maxAgg) * scale : 18
radius = min(radius, 55)
```
This yields a bounded 20–55px range with a fallback of 18px for groups lacking score data. When future backend scores arrive, swap `aggregatedScore` for `subcategoryScore` without changing the formula.

### 10.4 Horizontal Placement (Directional Ranges)
Instead of discrete x=1..4 buckets, we sample continuous ranges inside the existing domain `[0.5, 4.5]`:
| Priority | Range (uniform) | Intent |
|----------|-----------------|--------|
| Low      | 0.60 – 1.40     | Far-left supporting items |
| Medium   | 0.80 – 2.00     | Left → center migration |
| High     | 1.90 – 2.70     | Central focus band |
| Critical | 2.70 – 4.20     | Right → center pressure |

Ranges overlap slightly (Medium/High, High/Critical) to avoid hard visual seams and encourage natural clustering near center for higher urgency. The chart domain stays `[0.5,4.5]` for containment.

### 10.5 Vertical Placement & Collision Avoidance
Y remains non-semantic (visual dispersion only). We sample candidate y positions (uniform `[0.8, 4.2]`) and apply a lightweight collision pass:
1. Generate initial positions sequentially.
2. For each new bubble, compare distance to previously accepted bubbles.
3. If `distance < (r1 + r2) * 0.85`, shift x slightly (±0.12) or resample y (max attempts 12).
4. Clamp post-adjusted x to its priority range and y to `[0.7, 4.3]`.

This avoids O(n²) iterative relaxation while giving a reasonably separated layout for typical recommendation counts (< 60). If density increases substantially, we may upgrade to a force-directed or grid-based packing routine.

### 10.6 Legend Overlay
The priority legend is no longer bound to axis ticks. We render an absolutely positioned overlay above the chart canvas:
```
[ Medium ]      ← Priority →      [ Critical ]
```
Styling considerations:
- Small uppercase / muted font for side labels.
- Arrow label slightly brighter to draw central focus.
- Pointer events disabled so tooltips remain accessible.

### 10.7 Detail Modal (Subcategory View)
Clicking a bubble opens a modal listing all recommendations in that subcategory:
- Header: Subcategory name + aggregated score + total recommendations count.
- Body: Each recommendation enumerated with priority pill, title, and its individual scoreRefs sum.
- Existing sections (Business Impact, Cross-Pillar Considerations, Score References) remain scoped to the first (or aggregated) recommendation where logical; future refinement will merge or summarize these across items.

### 10.8 Data Contract Changes
`BubbleDatum` extended:
```
interface BubbleDatum {
    x: number;              // continuous horizontal position
    y: number;              // vertical position (non-semantic)
    r: number;              // radius
    subcategory: string;    // grouping key (recommendation.source)
    priority: string;       // highest priority among grouped recs
    priorityRank: number;   // numeric rank 1..4
    aggregatedScore?: number; // sum of scoreRefs across group
    count: number;          // number of recommendations
    recommendations: Recommendation[]; // all recs in group
}
```
Backward compatibility: the original single `recommendation` field is retained temporarily or replaced with the first item in `recommendations` if needed by existing components.

### 10.9 Motion Preservation
The subtle vertical drift interval continues, applied to the aggregated bubbles (`±0.02–0.14` Y units every ~3.8s) and clamped inside `[0.7,4.3]`. Horizontal positions remain static to preserve directional semantics.

### 10.10 Transition Plan
1. Implement aggregation + new types.
2. Replace dataset builder in `VisualizationTab.tsx` (remove vertical stacking logic).
3. Update `PillarBubbleChart.tsx` to read `priorityRank` for color and overlay labels.
4. Adapt modal component to list recommendations for the selected subcategory.
5. Keep fallback radius heuristic until backend supplies subcategory-level scores.
6. Add reduced-motion toggle (future) to disable drift.

### 10.11 Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Mixed-priority subcategory hides lower urgency items | Show per-item priority in modal list |
| Overlapping due to dense clusters | Increase max attempts or apply post-pass minor shifts |
| Large score variance compresses small bubbles | Apply minimum radius floor (18px) |
| Backend field mismatch when `source` absent | Fallback group key: `Unknown-{index}` |
| Tooltip ambiguity (single title) | Use subcategory name + count; list items in modal |

### 10.12 Future Enhancements
- Inward horizontal drift for High/Critical items to visually “pull” toward center urgency zone.
- Encoded Y axis (e.g., Effort or estimated implementation time) once reliable numeric values exist.
- Force-directed packing for extremely dense categories.
- Bulk selection: Shift‑click or lasso to compare aggregated scores.

Implementation will proceed incrementally; see repository history for commit references to this section.

---
