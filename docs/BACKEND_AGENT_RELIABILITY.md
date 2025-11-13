# Reliability Agent Walkthrough

This document provides a code-level walkthrough of the reliability agent in the Azure Well-Architected Agents backend, including its constants, analysis logic, and integration with the orchestrator and scoring modules.

---

## 1. Constants & Configuration

Reliability-specific criteria and configuration are defined in:
- `reliability_constants.py`: Contains weights, thresholds, and key concepts.
- `reliability_pillar.json`: Stores scoring rules and criteria for reliability.
- `utils/concepts/reliability_expected_concepts.json`: Domain knowledge for reliability analysis.

---

## 2. Agent Structure

```python
# app/agents/reliability_agent.py (simplified)
from .pillar_agent_base import PillarAgentBase
from .reliability_constants import RELIABILITY_CRITERIA
import json

class ReliabilityAgent(PillarAgentBase):
    def __init__(self, input_data):
        super().__init__(input_data)
        self.criteria = RELIABILITY_CRITERIA
        self.expected_concepts = self._load_expected_concepts()

    def _load_expected_concepts(self):
        with open('utils/concepts/reliability_expected_concepts.json') as f:
            return json.load(f)

    def analyze(self):
        findings = self._extract_reliability_findings()
        score = self._score_findings(findings)
        return score, findings

    def _extract_reliability_findings(self):
        # Custom logic to analyze reliability-related data
        # Compare input_data against expected concepts
        return {...}

    def _score_findings(self, findings):
        # Apply scoring rules from RELIABILITY_CRITERIA
        return ...
```

---

## 3. Orchestrator Integration

The orchestrator instantiates the reliability agent and collects its results:

```python
# app/analysis/orchestrator.py (relevant part)
from app.agents.reliability_agent import ReliabilityAgent

class Orchestrator:
    def __init__(self, normalized_data):
        self.data = normalized_data
        self.agents = [
            ReliabilityAgent(self.data),
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
    reliability_score = agent_results['ReliabilityAgent']['score']
    # Combine with other pillar scores as needed
    return reliability_score
```

---

## 5. Export & Reporting

Results are exported for review:

```python
# app/excel_export.py (relevant part)
def export_to_excel(results, filename):
    # Write reliability findings and score to Excel
    pass
```

---

## 6. Summary

- Reliability agent loads expected concepts and criteria.
- Analyzes input data for reliability best practices.
- Scores findings using pillar-specific rules.
- Orchestrator coordinates agent execution and aggregates results.

For more details, see the other documentation files in this directory.