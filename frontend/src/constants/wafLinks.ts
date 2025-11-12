// Centralized Azure Well-Architected Framework pillar & subcategory documentation links
// Minimal types for stronger reuse across components.

export type WellArchitectedPillar =
  | 'Reliability'
  | 'Security'
  | 'Cost Optimization'
  | 'Operational Excellence'
  | 'Performance Efficiency';

// Root pillar documentation links
export const AZURE_WAF_PILLAR_LINKS: Record<WellArchitectedPillar, string> = {
  Reliability: 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/',
  Security: 'https://learn.microsoft.com/en-us/azure/well-architected/security/',
  'Cost Optimization': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/',
  'Operational Excellence': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/',
  'Performance Efficiency': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/'
};

// Subcategory documentation links (normalized + legacy names). These keys intentionally include
// variations observed in assessment output to reduce missing-link scenarios.
export const AZURE_WAF_SUBCATEGORY_LINKS: Record<string, string> = {
  // ---------------- Reliability ----------------
  'Reliability-Focused Design Foundations': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/simplify',
  'Identify and Rate User and System Flows': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/identify-flows',
  'Perform Failure Mode Analysis (FMA)': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/failure-mode-analysis',
  'Define Reliability and Recovery Targets': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/metrics',
  'Add Redundancy at Different Levels': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/redundancy',
  'Implement a Timely and Reliable Scaling Strategy': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/scaling',
  'Strengthen Resiliency with Self-Preservation and Self-Healing': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/self-preservation',
  'Test for Resiliency and Availability Scenarios': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/testing-strategy',
  'Implement Structured, Tested, and Documented Disaster Plans': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/disaster-recovery',
  'Implement Structured, Tested, and Documented BCDR Plans': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/disaster-recovery',
  'Measure and Model the Solution\'s Health Indicators': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/monitoring',
  // Normalized / alternate reliability names
  'Simplicity & Efficiency': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/principles',
  'Flow Identification & Criticality': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/identify-flows',
  'Failure Mode Analysis': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/failure-mode-analysis',
  'Reliability & Recovery Targets': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/metrics',
  'Redundancy': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/redundancy',
  'Scaling Strategy': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/scaling',
  'Self-Healing & Resilience Patterns': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/self-preservation',
  'Resiliency & Chaos Testing': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/testing-strategy',
  'BCDR Planning': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/disaster-recovery',
  'Health Indicators & Monitoring': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/monitoring',

  // ---------------- Security ----------------
  'Establish a Security Baseline': 'https://learn.microsoft.com/en-us/azure/well-architected/security/establish-baseline',
  'Maintain a Secure Development Lifecycle': 'https://learn.microsoft.com/en-us/azure/well-architected/security/secure-development-lifecycle',
  'Classify and Label Data Sensitivity': 'https://learn.microsoft.com/en-us/azure/well-architected/security/data-classification',
  'Create Intentional Segmentation and Perimeters': 'https://learn.microsoft.com/en-us/azure/well-architected/security/segmentation',
  'Implement Conditional Identity and Access Management': 'https://learn.microsoft.com/en-us/azure/well-architected/security/identity-access',
  'Isolate, Filter, and Control Network Traffic': 'https://learn.microsoft.com/en-us/azure/well-architected/security/segmentation',
  'Encrypt Data with Modern Methods': 'https://learn.microsoft.com/en-us/azure/well-architected/security/encryption',
  'Harden Workload Components': 'https://learn.microsoft.com/en-us/azure/well-architected/security/harden-resources',
  'Protect Application Secrets': 'https://learn.microsoft.com/en-us/azure/well-architected/security/application-secrets',
  'Establish a Comprehensive Security Testing Regimen': 'https://learn.microsoft.com/en-us/azure/well-architected/security/test',
  'Implement Holistic Threat Detection and Monitoring': 'https://learn.microsoft.com/en-us/azure/well-architected/security/monitor-threats',
  'Define and Exercise Incident Response Procedures': 'https://learn.microsoft.com/en-us/azure/well-architected/security/incident-response',

  // ---------------- Operational Excellence ----------------
  'Define standard practices to develop and operate workload': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-development-practices',
  'Formalize operational tasks': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-operations-tasks',
  'Formalize software ideation and planning': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-software-ideation',
  'Enhance software development and quality assurance': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-development-practices',
  'Use infrastructure as code': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/infrastructure-as-code-design',
  'Build workload supply chain with pipelines': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/release-engineering-continuous-integration',
  'Establish structured incident management': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/incident-response',
  'Automate repetitive tasks': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/automate-tasks',
  'Expand Observability and Operational Monitoring': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/observability',

  // ---------------- Cost Optimization ----------------
  'Create a culture of financial responsibility': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/culture',
  'Create and maintain a cost model': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/cost-model',
  'Collect and review cost data': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/collect-review-cost-data',
  'Set spending guardrails': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/set-spending-guardrails',
  'Get the best rates from providers': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/get-best-rates',
  'Align usage to billing increments': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/align-usage-to-billing-increments',
  'Optimize component costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-component-costs',
  'Optimize environment costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-environment-costs',
  'Optimize flow costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-flow-costs',
  'Optimize data costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-data-costs',
  'Optimize code costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-code-costs',
  'Optimize scaling costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-scaling-costs',
  'Optimize personnel time': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-personnel-time',
  'Consolidate resources and responsibility': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/consolidation',

  // ---------------- Performance Efficiency ----------------
  'Performance Targets & SLIs/SLOs': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/performance-targets',
  'Capacity & Demand Planning': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/capacity-planning',
  'Service & Architecture Selection': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/select-services',
  'Data Collection & Telemetry': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/collect-performance-data',
  'Performance Testing & Benchmarking': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/performance-test',
  'Code & Runtime Optimization': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/optimize-code-infrastructure',
  'Data Usage Optimization': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/optimize-data-performance',
  'Critical Flow Optimization': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/prioritize-critical-flows',
  'Operational Load Efficiency': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/respond-live-performance-issues',
  'Live Issue Triage & Remediation': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/respond-live-performance-issues',
  'Continuous Optimization & Feedback Loop': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/continuous-performance-optimize',
  'Implement Proactive Scaling and Partitioning Strategy': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/optimize-scaling-costs',

  // ---------------- Pillar-level fallbacks ----------------
  'Reliability Best Practices': AZURE_WAF_PILLAR_LINKS.Reliability,
  'Security Best Practices': AZURE_WAF_PILLAR_LINKS.Security,
  'Cost Optimization Best Practices': AZURE_WAF_PILLAR_LINKS['Cost Optimization'],
  'Operational Excellence Best Practices': AZURE_WAF_PILLAR_LINKS['Operational Excellence'],
  'Performance Efficiency Best Practices': AZURE_WAF_PILLAR_LINKS['Performance Efficiency']
};

// Optional aliases for future normalization (unused currently, reserved for extension)
export const AZURE_WAF_SUBCATEGORY_ALIASES: Record<string, string> = {
  // Example: 'BCDR Planning': 'Implement Structured, Tested, and Documented BCDR Plans'
};

export function getWafLink(key: string): string | undefined {
  if (AZURE_WAF_PILLAR_LINKS[key as WellArchitectedPillar]) return AZURE_WAF_PILLAR_LINKS[key as WellArchitectedPillar];
  if (AZURE_WAF_SUBCATEGORY_LINKS[key]) return AZURE_WAF_SUBCATEGORY_LINKS[key];
  if (AZURE_WAF_SUBCATEGORY_ALIASES[key] && AZURE_WAF_SUBCATEGORY_LINKS[AZURE_WAF_SUBCATEGORY_ALIASES[key]]) {
    return AZURE_WAF_SUBCATEGORY_LINKS[AZURE_WAF_SUBCATEGORY_ALIASES[key]];
  }
  return undefined;
}
