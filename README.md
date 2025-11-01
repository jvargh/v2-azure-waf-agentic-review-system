# Azure Well-Architected Review Agentic Solution

A comprehensive multi-agent system built on the Microsoft Agent Framework to assess and improve Azure workloads across the five pillars of the Well-Architected Framework.

## Overview

This solution provides automated assessment and recommendations for Azure workloads using specialized agents for each pillar:

- **Reliability Framework Agent** - Assesses resiliency, availability, disaster recovery, and monitoring posture
- **Security Framework Agent** - Evaluates security controls, identity management, and threat protection
- **Cost Optimization Framework Agent** - Analyzes resource utilization and cost efficiency
- **Operational Excellence Framework Agent** - Reviews deployment processes, monitoring, and operational procedures
- **Performance Efficiency Framework Agent** - Assesses scalability, performance optimization, and resource efficiency

## Architecture

The system uses the Microsoft Agent Framework with each agent specializing in one pillar of the Well-Architected Framework. Agents communicate through a structured messaging protocol to coordinate assessments and resolve cross-pillar tradeoffs.

## Getting Started

### Prerequisites
- Python 3.8+
- Azure CLI
- Access to Microsoft Learn documentation

### Installation
```bash
pip install -r requirements.txt
```

### Running the Reliability Agent
```bash
python -m agents.reliability.main --config config/reliability.json
```

## Project Structure

```
azure-well-architected-agents/
├── agents/
│   ├── reliability/          # Reliability Framework Agent
│   ├── security/            # Security Framework Agent  
│   ├── cost/                # Cost Optimization Agent
│   ├── operational/         # Operational Excellence Agent
│   └── performance/         # Performance Efficiency Agent
├── shared/
│   ├── models/              # Common data models
│   ├── messaging/           # Agent-to-Agent communication
│   └── utils/               # Shared utilities
├── config/                  # Configuration files
├── tests/                   # Unit and integration tests
└── docs/                    # Documentation
```

## License

MIT License