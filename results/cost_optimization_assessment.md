# Cost Optimization Assessment Results

Generated: 2025-11-05T11:24:53.322562

Overall LLM Score: **0** / 100
Deterministic Maturity: **20.98%**

## Domain Scores
| Code | Title | Score |
|------|-------|-------|
| CO01 | Create a culture of financial responsibility | 35 |
| CO02 | Create and maintain a cost model | 30 |
| CO03 | Collect and review cost data | 20 |
| CO04 | Set spending guardrails | 20 |
| CO05 | Get the best rates from providers | 25 |
| CO06 | Align usage to billing increments | 40 |
| CO07 | Optimize component costs | 30 |
| CO08 | Optimize environment costs | 20 |
| CO09 | Optimize flow costs | 25 |
| CO10 | Optimize data costs | 35 |
| CO11 | Optimize code costs | 30 |
| CO12 | Optimize scaling costs | 25 |
| CO13 | Optimize personnel time | 35 |
| CO14 | Consolidate resources and responsibility | 20 |

## Recommendations
| Title | Severity | Priority | Impact | Codes |
|-------|----------|----------|--------|-------|
| Implement Azure Cost Management with Budgets and Alerts | 1 | Critical | 10 | CO01, CO03, CO04 |
| Eliminate Unused Resources and Orphaned Persistent Volumes | 1 | Critical | 9 | CO07, CO14 |
| Right-Size Non-Production Environments | 2 | High | 8 | CO08, CO06, CO07 |
| Enable Cluster Autoscaler and Improve Scaling Policies | 2 | High | 8 | CO12, CO06 |
| Switch to Consumption-Based and Autoscale Tiers for Key Services | 2 | High | 8 | CO05, CO07, CO10 |
| Use Azure Reservations, Savings Plans, and Hybrid Benefit | 2 | Medium | 7 | CO05, CO07 |
| Set Resource Quotas and Policies for Governance | 1 | Critical | 10 | CO04, CO14, CO01 |
| Tag Resources for Team Accountability and Chargeback | 2 | High | 8 | CO01, CO14, CO03 |
| Optimize Log Analytics and Application Insights Costs | 3 | Medium | 6 | CO07, CO10 |
| Deploy Automated Backup Policies for Stateful Data | 2 | High | 8 | CO10, CO04 |
| Move Microservices to Separate Namespaces and Resource Groups | 3 | Medium | 6 | CO14, CO04 |
| Automate Container Image Patch and Retention Policies | 2 | Medium | 7 | CO07, CO13 |
| Train Development Teams in Cloud Cost Fundamentals | 3 | Medium | 6 | CO01 |

## MCP References
| Title | URL |
|-------|-----|
| Cost optimization checklist | https://learn.microsoft.com/en-us/azure/architecture/checklist/cost-optimization |
| Cost optimization in the Microsoft Azure Well-Architected Framework | https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/ |
| Five pillars of the Azure Well-Architected Framework - Cost optimization | https://learn.microsoft.com/en-us/azure/well-architected/pillars |

## Deterministic Practice Scores
| Code | Score (0-5) | Weight | Coverage | Matched Signals |
|------|---------------|--------|----------|------------------|
| CO01 | 0 | 0.08 | 0.0 | - |
| CO02 | 0 | 0.09 | 0.0 | - |
| CO03 | 1 | 0.08 | 0.286 | cost management, azure cost |
| CO04 | 2 | 0.07 | 0.429 | policy, rbac, governance |
| CO05 | 1 | 0.08 | 0.143 | spot |
| CO06 | 0 | 0.06 | 0.0 | - |
| CO07 | 2 | 0.07 | 0.429 | orphaned, legacy, unused |
| CO08 | 1 | 0.07 | 0.143 | environment |
| CO09 | 1 | 0.06 | 0.167 | feature |
| CO10 | 2 | 0.08 | 0.429 | retention, backup, replication |
| CO11 | 2 | 0.07 | 0.429 | performance, caching, optimization |
| CO12 | 1 | 0.08 | 0.143 | autoscale |
| CO13 | 2 | 0.06 | 0.429 | ci/cd, debugging, observability |
| CO14 | 0 | 0.07 | 0.0 | - |