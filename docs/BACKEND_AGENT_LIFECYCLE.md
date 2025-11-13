# Backend Agent Lifecycle & Interactions

This document provides a code-level walkthrough of the agent lifecycle and interactions in the Azure Well-Architected Agents backend. It covers agent structure, orchestrator coordination, and scoring aggregation.

---

## 1. Agent Structure & Operation

Each agent (e.g., `cost_agent.py`) inherits from a base class and implements pillar-specific logic:

```python
# app/agents/pillar_agent_base.py (simplified)
class PillarAgentBase:
    def __init__(self, input_data):
        self.input_data = input_data

    def analyze(self):
        raise NotImplementedError("Subclasses must implement analyze()")
```

```python
# app/agents/cost_agent.py (simplified)
from .pillar_agent_base import PillarAgentBase
from .cost_constants import COST_CRITERIA

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
        return {...}

    def _score_findings(self, findings):
        # Apply scoring rules from COST_CRITERIA
        return ...
```

---

## 2. Orchestrator Coordination

The orchestrator instantiates agents and runs the assessment:

```python
# app/analysis/orchestrator.py (simplified)
from app.agents.cost_agent import CostAgent
from app.agents.operational_agent import OperationalAgent
# ... other agents

class Orchestrator:
    def __init__(self, normalized_data):
        self.data = normalized_data
        self.agents = [
            CostAgent(self.data),
            OperationalAgent(self.data),
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

## 3. Scoring & Results Aggregation

After agent evaluation, scoring modules aggregate and finalize results:

```python
# app/scoring/scoring.py (simplified)
def aggregate_scores(agent_results):
    total_score = 0
    for pillar, result in agent_results.items():
        total_score += result['score']
    return total_score / len(agent_results)
```

- Scores from each agent are combined for an overall assessment.
- Criteria and thresholds are loaded from JSON files for flexibility.

---

## 4. Export & Reporting

Results are exported for review:

```python
# app/excel_export.py (simplified)
def export_to_excel(results, filename):
    # Use pandas or openpyxl to write results to Excel
    pass
```

---

## 5. Summary

- Agents encapsulate pillar-specific logic and scoring.
- Orchestrator coordinates agent execution and aggregates results.
- Scoring modules finalize and export assessment outcomes.

For more details, see the other documentation files in this directory.