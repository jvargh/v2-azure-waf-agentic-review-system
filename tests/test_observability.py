"""(Relocated) Observability quick check."""
import asyncio
from backend.app.agents.cost_agent import CostAgent

async def run():
    agent = CostAgent()
    assessment = await agent.assess_architecture("Azure App Service with SQL Database")
    assert assessment.overall_score >= 0

def test_observability_smoke():
    asyncio.run(run())

if __name__ == '__main__':  # pragma: no cover
    test_observability_smoke(); print('✅ observability smoke passed')
