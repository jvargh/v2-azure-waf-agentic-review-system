# Backend Diagrams

This document provides visual diagrams to help developers understand the architecture and workflow of the Azure Well-Architected Agents backend.

---

## 1. Sequence Diagram: Assessment Request

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Normalizer
    participant Analyzer
    participant Orchestrator
    participant Agents
    participant Scoring
    participant Export
    User->>API: POST /api/assess
    API->>Normalizer: Normalize artifacts
    Normalizer->>Analyzer: Analyze documents
    Analyzer->>Orchestrator: Pass features
    Orchestrator->>Agents: Invoke pillar agents
    Agents->>Scoring: Return scores
    Scoring->>API: Aggregate & respond
    User->>API: GET /api/export/{id}
    API->>Export: Generate Excel
    Export->>User: Return file
```

---

## 2. Component Diagram: Backend Modules

```mermaid
flowchart TD
    A[server.py] --> B[app/analysis/orchestrator.py]
    B --> C1[app/agents/cost_agent.py]
    B --> C2[app/agents/operational_agent.py]
    B --> C3[app/agents/performance_agent.py]
    B --> C4[app/agents/reliability_agent.py]
    B --> C5[app/agents/security_agent.py]
    C1 & C2 & C3 & C4 & C5 --> D[app/scoring/scoring.py]
    D --> E[app/excel_export.py]
    D --> F[app/progress_api.py]
    B --> G[app/analysis/artifact_normalizer.py]
    B --> H[app/analysis/document_analyzer.py]
    A --> I[app/config/azure_openai.py]
    A --> J[utils/env_utils.py]
```

---

## 3. Data Flow Diagram (Text)

- User submits assessment request
- API receives and validates input
- Artifacts normalized
- Documents analyzed
- Orchestrator coordinates agent execution
- Agents evaluate pillars and return scores
- Scoring module aggregates results
- Results exported and progress tracked

---

For more details, see the other documentation files in this directory.