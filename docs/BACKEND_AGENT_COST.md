# Cost Agent Walkthrough

This document provides a code-level walkthrough of the cost agent in the Azure Well-Architected Agents backend, including its constants, analysis logic, and integration with the orchestrator and scoring modules.

---

## 1. Constants & Configuration

Cost-specific criteria and configuration are defined in:
- `cost_constants.py`: Contains weights, thresholds, and key concepts for cost optimization.
- `cost_pillar.json`: Stores scoring rules and criteria for cost.

---

## 2. Agent Structure

```python
# app/agents/cost_agent.py (simplified)
from .pillar_agent_base import PillarAgentBase
from .cost_constants import COST_CRITERIA
import json

class CostAgent(PillarAgentBase):
    def __init__(self, input_data):
        super().__init__(input_data)
        self.criteria = COST_CRITERIA

    def analyze(self):
        findings = self._extract_cost_findings()
        score = self._score_findings(findings)
        return score, findings

    def _extract_cost_findings(self):
        # Custom logic to analyze cost-related data
        # Example: Identify unused resources, over-provisioned services
        return {...}

    def _score_findings(self, findings):
        # Apply scoring rules from COST_CRITERIA
        return ...
```

---

## 3. Orchestrator Integration

The orchestrator instantiates the cost agent and collects its results:

```python
# app/analysis/orchestrator.py (relevant part)
from app.agents.cost_agent import CostAgent

class Orchestrator:
    def __init__(self, normalized_data):
        self.data = normalized_data
        self.agents = [
            CostAgent(self.data),
            # ... other agents
        ]

    def run_assessment(self):
        results = {}
        for agent in self.agents:
            score, findings = agent.analyze()
            results[agent.__class__.__name__] = {
                'score': score,
                'findings': findings
            }
        return results
```

---

## 4. Scoring & Aggregation

Scoring logic uses criteria from JSON and constants files:

```python
# app/scoring/scoring.py (relevant part)
def aggregate_scores(agent_results):
    cost_score = agent_results['CostAgent']['score']
    # Combine with other pillar scores as needed
    return cost_score
```

---

## 5. Export & Reporting

Results are exported for review:

```python
# app/excel_export.py (relevant part)
def export_to_excel(results, filename):
    # Write cost findings and score to Excel
    pass
```

---

## 6. Summary

- Cost agent loads criteria and configuration.
- Analyzes input data for cost optimization opportunities.
- Scores findings using pillar-specific rules.
- Orchestrator coordinates agent execution and aggregates results.

For more details, see the other documentation files in this directory.