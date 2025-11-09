"""Cost Optimization pillar agent implementation."""

import asyncio
import logging
import sys
import argparse

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
    from pathlib import Path
    from src.app.utils.logging_config import init_logging
    from src.app.utils.cli_utils import create_agent_argument_parser, apply_log_level_override

    parser = create_agent_argument_parser("Cost Optimization")
    args = parser.parse_args()
    apply_log_level_override(args.log_level)
    init_logging()

    architecture_file = Path(args.architecture_file)
    if not architecture_file.exists():
        print(f"Error: File not found: {architecture_file}")
        sys.exit(1)

    architecture_text = architecture_file.read_text(encoding="utf-8")
    cases_path = Path(args.cases_file) if args.cases_file else None

    print("Initializing Cost Optimization Agent...")
    agent = CostAgent()

    print(f"\nAssessing architecture from {architecture_file.name}...")
    try:
        if cases_path:
            assessment = await agent.assess_architecture_with_cases(architecture_text, cases_path)
        else:
            assessment = await agent.assess_architecture(architecture_text)
        print("\n" + "=" * 80)
        print("COST OPTIMIZATION ASSESSMENT")
        print("=" * 80)
        markdown = agent.build_results_markdown(assessment)
        print(markdown)

        artifacts = agent.write_assessment_artifacts(
            assessment,
            markdown_filename="cost_optimization_assessment.md",
            json_filename="cost_optimization_assessment.json",
        )
        print("\nResults written to:")
        print(f"  - {artifacts['markdown']}")
        print(f"  - {artifacts['json']}")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
