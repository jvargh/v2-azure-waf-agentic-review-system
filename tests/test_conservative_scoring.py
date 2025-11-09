"""(Relocated) Conservative scoring evidence level tests."""
import sys
sys.path.insert(0, 'backend')
from server import _calculate_conservative_score

PILLARS = [
    ('reliability', 'Reliability'),
    ('security', 'Security'),
    ('cost', 'Cost Optimization'),
    ('operational', 'Operational Excellence'),
    ('performance', 'Performance Efficiency')
]

def _run_case(label: str, corpus: str):
    results = {}
    for code, name in PILLARS:
        score, confidence, subcats, source, coverage, gaps = _calculate_conservative_score(corpus, code, name)
        results[name] = (score, confidence, coverage, gaps)
    return results

def test_minimal_evidence():
    corpus = "We use Azure VMs for hosting."
    results = _run_case("minimal", corpus)
    for name, (score, conf, cov, gaps) in results.items():
        assert score <= 25
        assert conf in ("Low", "Medium")

def test_moderate_evidence():
    corpus = (
        "Our architecture uses Azure Kubernetes Service for container orchestration with "
        "multi-region deployment across East US and West Europe. We implement Azure Key Vault "
        "for secret management and encryption at rest. For monitoring, we use Azure Monitor "
        "with custom dashboards and alerting. Cost optimization includes reserved instances "
        "for predictable workloads. We use Azure Front Door with caching to improve latency "
        "and throughput for global users."
    )
    results = _run_case("moderate", corpus)
    for name, (score, conf, cov, gaps) in results.items():
        assert score >= 20
        assert conf in ("Medium", "High")

def test_comprehensive_evidence():
    corpus = """
    Multi-region active-active deployment with automatic failover using Azure Traffic Manager.
    Database replication, automated backup & DR testing, health checks, circuit breakers.
    Key Vault secrets + RBAC + network isolation + encryption + threat detection enabled.
    Reserved instances, autoscaling, tagging, rightsizing, spot for batch jobs.
    CI/CD pipelines, IaC Terraform + GitOps, observability stack with tracing and alerting.
    Front Door CDN + Redis caching + query tuning + performance testing + auto-scaling.
    """
    results = _run_case("comprehensive", corpus)
    highs = sum(1 for _, (score, conf, _cov, _gaps) in results.items() if score >= 60)
    assert highs >= 3

if __name__ == '__main__':  # pragma: no cover
    test_minimal_evidence(); test_moderate_evidence(); test_comprehensive_evidence(); print("✅ Manual run passed")
