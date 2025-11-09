"""(Relocated) Quick reliability concept coverage smoke test."""

def test_concept_coverage_smoke():
    corpus_minimal = "We use Azure VMs for hosting."
    corpus_moderate = (
        "Our architecture uses Azure Kubernetes Service with multi-region deployment. "
        "We implement Key Vault for secret management and Azure Monitor for alerting."
    )
    concepts = ["redundancy", "failover", "backup", "disaster recovery", "availability"]
    hits_min = sum(1 for c in concepts if c in corpus_minimal.lower())
    hits_mod = sum(1 for c in concepts if c in corpus_moderate.lower())
    assert hits_mod >= hits_min

if __name__ == '__main__':  # pragma: no cover
    test_concept_coverage_smoke(); print('✅ scoring quick smoke passed')
