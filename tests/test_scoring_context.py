"""(Relocated) Context-aware scoring verification with positive negations."""
import sys
sys.path.insert(0, r'C:\_Projects\MAF\wara\azure-well-architected-agents')
from backend.server import _calculate_conservative_score

good_arch = """
No single point of failure; automated failover; Key Vault secrets; zero trust; availability zones.
"""

bad_arch = """
Single region only; backup not configured; failover not configured; encryption not enabled; MFA not configured.
"""

def test_good_vs_bad():
    g_score, g_conf, *_ = _calculate_conservative_score(good_arch, 'reliability', 'Reliability')
    b_score, b_conf, *_ = _calculate_conservative_score(bad_arch, 'reliability', 'Reliability')
    assert g_score > b_score
    assert g_conf in ("Medium", "High")
    assert b_conf in ("Low", "Medium")

if __name__ == '__main__':  # pragma: no cover
    test_good_vs_bad(); print('✅ scoring context quick check passed')
