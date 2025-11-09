import asyncio
from backend.server import _evaluate_pillar, PILLARS, ASSESSMENTS

HIGH_CORPUS = """
This production workload implements comprehensive reliability and security practices.
Redundancy across availability zones with active-active failover and documented RTO/RPO (RTO 30 minutes, RPO 5 minutes).
Automated backups configured and tested monthly; Azure Site Recovery orchestrates multi-region disaster recovery drills.
Health checks, monitoring dashboards, distributed tracing, and chaos engineering fault injection scenarios in staging.
Encryption in transit and at rest with Azure Key Vault managed key rotation; RBAC and MFA enforced with Conditional Access.
Network security via private endpoints, firewall and WAF; threat detection integrated (Microsoft Defender + Sentinel SIEM) with alerting and incident response runbooks.
Cost optimization includes reserved instances, rightsizing, tagging for chargeback, anomaly detection alerts, and FinOps governance reviews.
Operational excellence: infrastructure as code (Bicep/Terraform), automated canary + blue-green deployments, runbook automation, postmortem reviews and error budget tracking.
Performance efficiency: auto-scaling (HPA), load balancing, caching (Redis), CDN, query optimization, latency SLOs (p95 < 220ms), throughput benchmarking and profiling.
"""

LOW_CORPUS = """
Basic app. No backup policy; redundancy not configured; failover not configured; monitoring not configured.
Encryption not enabled; mfa not configured; logging not enabled; threat detection not implemented.
Reserved instance strategy not implemented; optimization not performed; cost monitoring not configured.
Automation not implemented; deployment manual only; documentation missing; testing not implemented.
Scalability not configured; latency high; caching not implemented; optimization not configured.
"""

async def simulate(label: str, corpus: str):
    aid = f"sim_{label}"
    ASSESSMENTS[aid] = {"unified_corpus": corpus}
    print(f"\n===== Simulation: {label} corpus =====")
    for code, name in PILLARS:
        result = await _evaluate_pillar(aid, code, name)
        priorities = [r.priority for r in result.recommendations]
        print(f"{name:<22} score={result.overall_score:3d} recs={len(result.recommendations):2d} priorities={priorities}")

async def main():
    await simulate("HIGH", HIGH_CORPUS)
    await simulate("LOW", LOW_CORPUS)

if __name__ == "__main__":
    asyncio.run(main())
