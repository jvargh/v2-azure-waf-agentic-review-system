# Visualization Components

This folder contains visualization-specific components for the Azure Well-Architected Assessment application.

## Structure

```
visualization/
├── types.ts                      # TypeScript interfaces for visualization data
├── utils.ts                      # Utility functions (priority mappings, colors, jitter)
├── Scoreboard.tsx                # Top metrics panel component
├── PillarBubbleChart.tsx         # Reusable bubble chart for individual pillars
├── RecommendationDetailPane.tsx  # Side panel for detailed recommendation view
└── VisualizationTab.tsx          # Main orchestrator component
```

## Components

### VisualizationTab
Main container that:
- Fetches assessment data from context
- Computes scoreboard metrics
- Transforms recommendations into bubble chart datasets
- Manages selected recommendation state
- Renders scoreboard, bubble charts, and detail pane

### Scoreboard
Displays 5 key metrics:
- Overall Architecture Score
- Total Recommendations
- Critical Recommendations
- Average Coverage %
- Confidence Level

### PillarBubbleChart
Renders a Recharts scatter plot for a single pillar:
- X-axis: Priority (Low → Medium → High → Critical)
- Y-axis: Jittered vertical positioning for spacing
- Bubble size: Based on `scoreRefs` total or priority fallback
- Bubble color: Encoded by priority (green → yellow → orange → red)
- Click handler: Opens detail pane

### RecommendationDetailPane
Fixed-position side panel showing:
- Recommendation title
- Priority and effort badges
- Subcategory with Azure Learn link
- Full recommendation text
- Business impact
- Cross-pillar considerations
- Score references breakdown

## Data Flow

1. `useAssessments` context provides selected assessment
2. `VisualizationTab` computes metrics and datasets using `useMemo`
3. Each `PillarBubbleChart` receives its dataset and click handler
4. On bubble click, `VisualizationTab` sets `selectedRecommendation`
5. `RecommendationDetailPane` renders if recommendation is selected

## Integration

Import from frontend components (same as other components):

```tsx
import VisualizationTab from '../visualization/VisualizationTab';
```

The visualization folder is located at `frontend/src/visualization/`, making it part of the main frontend application structure.

## Styling

Uses inline styles for portability. Future enhancement: extract to CSS modules or styled-components for theming support.

## Future Enhancements

- Keyboard navigation and accessibility improvements
- Export visualization as PNG/SVG
- Filter bubbles by priority or effort
- Timeline view for historical assessments
- Heatmap view for cross-pillar risk analysis
