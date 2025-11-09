"""Cost Optimization pillar agent implementation."""

import asyncio
import logging

from .pillar_agent_base import BasePillarAgent
from .cost_constants import DOMAIN_TITLES, PILLAR_CODE, PILLAR_PREFIX


class CostAgent(BasePillarAgent):
    """Agent specialized in Azure Well-Architected Cost Optimization pillar assessment."""

    def __init__(self):
        """Initialize the Cost Optimization agent."""
        super().__init__(
            pillar_code=PILLAR_CODE,
            pillar_prefix=PILLAR_PREFIX,
            domain_titles=DOMAIN_TITLES,
            instructions_filename="cost_agent_instructions.txt",
            agent_name="CostOptimizationAgent",
            pillar_display_name="Cost Optimization",
            mcp_topic="cost-optimization",
        )


async def main():
    """CLI entry point for Cost Optimization agent."""
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Usage: python -m src.app.agents.cost_agent <architecture_file>")
        sys.exit(1)

    architecture_file = Path(sys.argv[1])
    if not architecture_file.exists():
        print(f"Error: File not found: {architecture_file}")
        sys.exit(1)

    architecture_text = architecture_file.read_text(encoding="utf-8")

    print("Initializing Cost Optimization Agent...")
    agent = CostAgent()

    print(f"\nAssessing architecture from {architecture_file.name}...")
    try:
        assessment = await agent.assess_architecture(architecture_text)
        print("\n" + "=" * 80)
        print("COST OPTIMIZATION ASSESSMENT")
        print("=" * 80)
        markdown = agent.build_results_markdown(assessment)
        print(markdown)

        from pathlib import Path
        import json
        results_dir = Path("results")
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "cost_optimization_assessment.md").write_text(markdown, encoding="utf-8")
        json_payload = {
            "overall_score": assessment.overall_score,
            "domain_scores": assessment.domain_scores,
            "recommendations": assessment.recommendations,
            "maturity": assessment.maturity,
            "mcp_references": assessment.mcp_references,
            "timestamp": assessment.timestamp,
        }
        (results_dir / "cost_optimization_assessment.json").write_text(json.dumps(json_payload, indent=2), encoding="utf-8")
        print("\nResults written to:")
        print(f"  - {results_dir / 'cost_optimization_assessment.md'}")
        print(f"  - {results_dir / 'cost_optimization_assessment.json'}")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
