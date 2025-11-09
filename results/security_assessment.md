# Security Assessment Results

Generated: 2025-11-05T21:14:51.432550

Overall LLM Score: **22** / 100
Deterministic Maturity: **24.0%**

## Domain Scores
| Code | Title | Score |
|------|-------|-------|
| SE01 | Establish a Security Baseline | 20 |
| SE02 | Maintain a Secure Development Lifecycle | 20 |
| SE03 | Classify and Label Data Sensitivity | 15 |
| SE04 | Create Intentional Segmentation and Perimeters | 10 |
| SE05 | Implement Conditional Identity and Access Management | 15 |
| SE06 | Isolate, Filter, and Control Network Traffic | 10 |
| SE07 | Encrypt Data with Modern Methods | 30 |
| SE08 | Harden Workload Components | 10 |
| SE09 | Protect Application Secrets | 10 |
| SE10 | Implement Holistic Threat Detection and Monitoring | 25 |
| SE11 | Establish a Comprehensive Security Testing Regimen | 15 |
| SE12 | Define and Exercise Incident Response Procedures | 5 |

## Recommendations
| Title | Severity | Priority | Impact | Codes |
|-------|----------|----------|--------|-------|
| Implement Azure Key Vault and Secret Rotation | 1 | 1 | 9 | SE09, SE05, SE01 |
| Establish Robust Network Segmentation and Enable Network Security Controls | 1 | 1 | 10 | SE04, SE06, SE01 |
| Integrate Microsoft Defender for Containers and Mandatory Vulnerability Scanning in Pipelines | 1 | 1 | 8 | SE08, SE02, SE10 |
| Implement Data Classification, Encryption, and Compliance Policies | 2 | 2 | 8 | SE03, SE07, SE01 |
| Define and Drill Incident Response and Disaster Recovery Plans | 2 | 2 | 9 | SE12, SE01, SE07 |
| Enforce Least Privilege RBAC and Conditional Access Policies | 2 | 2 | 7 | SE05, SE04, SE01 |

## MCP References
| Title | URL |
|-------|-----|
| Azure Documentation | https://learn.microsoft.com/en-us/azure/architecture/framework/security/overview |
| Azure Documentation | https://learn.microsoft.com/en-us/azure/security/fundamentals/network-best-practices |
| Azure Documentation | https://learn.microsoft.com/en-us/azure/security/fundamentals/identity-management-best-practices |

## Deterministic Practice Scores
| Code | Score (0-5) | Weight | Coverage | Matched Signals |
|------|---------------|--------|----------|------------------|
| SE01 | 0 | 0.09 | 0.0 | - |
| SE02 | 0 | 0.09 | 0.0 | - |
| SE03 | 1 | 0.08 | 0.25 | data classification |
| SE04 | 2 | 0.09 | 0.4 | segmentation, isolation |
| SE05 | 0 | 0.1 | 0.0 | - |
| SE06 | 2 | 0.1 | 0.5 | azure firewall, ddos protection, web application firewall |
| SE07 | 2 | 0.08 | 0.4 | encryption at rest, https |
| SE08 | 1 | 0.08 | 0.2 | patching |
| SE09 | 2 | 0.07 | 0.5 | key vault, managed identity |
| SE10 | 3 | 0.07 | 0.667 | sentinel, azure monitor, siem, log analytics |
| SE11 | 1 | 0.07 | 0.25 | chaos engineering |
| SE12 | 1 | 0.08 | 0.2 | incident response |