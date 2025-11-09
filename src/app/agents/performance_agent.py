"""Performance Efficiency pillar agent implementation."""

import asyncio
import logging
from src.app.utils.logging_config import init_logging

from .pillar_agent_base import BasePillarAgent
from .performance_constants import DOMAIN_TITLES, PILLAR_CODE, PILLAR_PREFIX


class PerformanceAgent(BasePillarAgent):
    """Agent specialized in Azure Well-Architected Performance Efficiency pillar assessment."""

    def __init__(self):
        """Initialize the Performance Efficiency agent."""
        super().__init__(
            pillar_code=PILLAR_CODE,
            pillar_prefix=PILLAR_PREFIX,
            domain_titles=DOMAIN_TITLES,
            instructions_filename="performance_agent_instructions.txt",
            agent_name="PerformanceEfficiencyAgent",
            pillar_display_name="Performance Efficiency",
            mcp_topic="performance-efficiency",
        )


async def main():
    """CLI entry point for Performance Efficiency agent."""
    import sys
    from pathlib import Path
    from src.app.utils.cli_utils import create_agent_argument_parser, apply_log_level_override

    parser = create_agent_argument_parser("Performance Efficiency")
    args = parser.parse_args()
    apply_log_level_override(args.log_level)

    architecture_file = Path(args.architecture_file)
    if not architecture_file.exists():
        print(f"Error: File not found: {architecture_file}")
        sys.exit(1)

    architecture_text = architecture_file.read_text(encoding="utf-8")
    cases_path = Path(args.cases_file) if args.cases_file else None

    init_logging()
    print("Initializing Performance Efficiency Agent...")
    agent = PerformanceAgent()

    print(f"\nAssessing architecture from {architecture_file.name}...")
    try:
        if cases_path:
            assessment = await agent.assess_architecture_with_cases(architecture_text, cases_path)
        else:
            assessment = await agent.assess_architecture(architecture_text)
        print("\n" + "=" * 80)
        print("PERFORMANCE EFFICIENCY ASSESSMENT")
        print("=" * 80)
        markdown = agent.build_results_markdown(assessment)
        print(markdown)

        artifacts = agent.write_assessment_artifacts(
            assessment,
            markdown_filename="performance_efficiency_assessment.md",
            json_filename="performance_efficiency_assessment.json",
        )
        print("\nResults written to:")
        print(f"  - {artifacts['markdown']}")
        print(f"  - {artifacts['json']}")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
