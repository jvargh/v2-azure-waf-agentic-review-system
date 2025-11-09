import asyncio
from pathlib import Path

from backend.app.agents.cost_agent import CostAgent

SAMPLE_ARCH = "Sample workload running on Azure App Service with Azure Storage backend."
CSV_PATH = Path(__file__).parent / "data" / "azure_support_cases_sample.csv"

async def _run():
    agent = CostAgent()
    assessment = await agent.assess_architecture_with_cases(SAMPLE_ARCH, CSV_PATH)
    # Ensure support cases were merged
    assert "Historical Azure Support Cases" in assessment.architecture_text
    assert "High CPU on App Service" in assessment.architecture_text
    await agent.cleanup()

def test_support_cases_integration():
    asyncio.run(_run())
