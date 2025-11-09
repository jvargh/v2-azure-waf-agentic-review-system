"""Azure Well-Architected Framework Security agent."""

import asyncio
import logging
from src.app.utils.logging_config import init_logging

from .pillar_agent_base import BasePillarAgent
from .security_constants import DOMAIN_TITLES, PILLAR_CODE, PILLAR_PREFIX


class SecurityAgent(BasePillarAgent):
    """Security pillar implementation using the shared base agent."""

    def __init__(self, enable_mcp: bool = True) -> None:
        super().__init__(
            pillar_code=PILLAR_CODE,
            pillar_prefix=PILLAR_PREFIX,
            domain_titles=DOMAIN_TITLES,
            instructions_filename="security_agent_instructions.txt",
            agent_name="SecurityAgent",
            pillar_display_name="Security",
            mcp_topic="azure-well-architected",
            enable_mcp=enable_mcp,
        )


async def main():
    """CLI entry point for Security agent."""
    import sys
    from pathlib import Path
    from src.app.utils.cli_utils import create_agent_argument_parser, apply_log_level_override

    parser = create_agent_argument_parser("Security")
    args = parser.parse_args()
    apply_log_level_override(args.log_level)

    architecture_file = Path(args.architecture_file)
    if not architecture_file.exists():
        print(f"Error: File not found: {architecture_file}")
        sys.exit(1)

    architecture_text = architecture_file.read_text(encoding="utf-8")
    cases_path = Path(args.cases_file) if args.cases_file else None

    init_logging()
    print("Initializing Security Agent...")
    agent = SecurityAgent(enable_mcp=True)

    print(f"\nAssessing architecture from {architecture_file.name}...")
    try:
        if cases_path:
            assessment = await agent.assess_architecture_with_cases(architecture_text, cases_path)
        else:
            assessment = await agent.assess_architecture(architecture_text)
        print("\n" + "=" * 80)
        print("SECURITY ASSESSMENT")
        print("=" * 80)
        markdown = agent.build_results_markdown(assessment)
        print(markdown)

        artifacts = agent.write_assessment_artifacts(
            assessment,
            markdown_filename="security_assessment.md",
            json_filename="security_assessment.json",
        )
        print("\nResults written to:")
        print(f"  - {artifacts['markdown']}")
        print(f"  - {artifacts['json']}")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
