"""Reliability pillar agent implementation."""

import asyncio
import logging
from backend.app.utils.logging_config import init_logging

from .pillar_agent_base import BasePillarAgent
from .reliability_constants import DOMAIN_TITLES, PILLAR_CODE, PILLAR_PREFIX


class ReliabilityAgent(BasePillarAgent):
    """Agent specialized in Azure Well-Architected Reliability pillar assessment."""

    def __init__(self, enable_mcp: bool = True, assessment_mode: str = "comprehensive"):
        """Initialize the Reliability agent.
        
        Args:
            enable_mcp: Whether to enable MCP documentation integration
            assessment_mode: Assessment mode (for backward compatibility, not used in base class)
        """
        super().__init__(
            pillar_code=PILLAR_CODE,
            pillar_prefix=PILLAR_PREFIX,
            domain_titles=DOMAIN_TITLES,
            instructions_filename="reliability_agent_instructions.txt",
            agent_name="ReliabilityAgent",
            pillar_display_name="Reliability",
            mcp_topic="reliability",
            enable_mcp=enable_mcp,
        )
        self.assessment_mode = assessment_mode
    
    async def assess_architecture_reliability(
        self,
        architecture_content: str,
        business_criticality: str = "high",
        compliance_requirements: str = "",
        rto_rpo_targets: str = "",
    ):
        """Assess architecture reliability with additional context parameters.
        
        This method provides backward compatibility with the original ReliabilityAgent API
        while using the standardized BasePillarAgent implementation.
        
        Args:
            architecture_content: Architecture description text
            business_criticality: Business criticality level
            compliance_requirements: Compliance requirements
            rto_rpo_targets: RTO/RPO targets
            
        Returns:
            PillarAssessment with reliability evaluation
        """
        # Enhance architecture content with additional context
        enhanced_content = architecture_content
        
        if business_criticality:
            enhanced_content += f"\n\nBusiness Criticality: {business_criticality}"
        if compliance_requirements:
            enhanced_content += f"\nCompliance Requirements: {compliance_requirements}"
        if rto_rpo_targets:
            enhanced_content += f"\nRTO/RPO Targets: {rto_rpo_targets}"
        
        # Use base class assessment method
        assessment = await self.assess_architecture(enhanced_content)
        
        # Add backward-compatible attribute for overall_reliability_score
        assessment.overall_reliability_score = assessment.overall_score
        
        return assessment
    
    async def write_assessment_files(self, assessment, output_dir: str = "results"):
        """Write assessment results to files.
        
        Args:
            assessment: PillarAssessment object
            output_dir: Output directory path
        """
        from pathlib import Path
        import json
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Write markdown report
        markdown_content = self.build_results_markdown(assessment)
        markdown_file = output_path / "reliability_assessment.md"
        markdown_file.write_text(markdown_content, encoding="utf-8")
        
        # Write JSON data
        json_data = {
            "overall_score": assessment.overall_score,
            "domain_scores": assessment.domain_scores,
            "recommendations": assessment.recommendations,
            "maturity": assessment.maturity,
            "mcp_references": assessment.mcp_references,
            "timestamp": assessment.timestamp,
        }
        json_file = output_path / "reliability_assessment.json"
        json_file.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        
        return {
            "markdown": str(markdown_file),
            "json": str(json_file),
        }


async def main():
    """CLI entry point for Reliability pillar agent."""
    import sys
    from pathlib import Path
    from backend.app.utils.cli_utils import create_agent_argument_parser, apply_log_level_override

    parser = create_agent_argument_parser("Reliability")
    args = parser.parse_args()
    apply_log_level_override(args.log_level)

    architecture_file = Path(args.architecture_file)
    if not architecture_file.exists():
        print(f"Error: File not found: {architecture_file}")
        sys.exit(1)

    architecture_text = architecture_file.read_text(encoding="utf-8")
    cases_path = Path(args.cases_file) if args.cases_file else None

    # Central logging init (idempotent)
    init_logging()

    print("Initializing Reliability Agent...")
    agent = ReliabilityAgent(enable_mcp=True, assessment_mode="comprehensive")

    print(f"\nAssessing architecture from {architecture_file.name}...")
    try:
        if cases_path:
            # Merge cases into architecture via new helper (bypasses reliability wrapper)
            assessment = await agent.assess_architecture_with_cases(architecture_text, cases_path)
            # Backward-compatible attribute expected by legacy printing logic
            assessment.overall_reliability_score = assessment.overall_score
        else:
            assessment = await agent.assess_architecture_reliability(
                architecture_content=architecture_text,
                business_criticality="high",
                compliance_requirements="SOC2, PCI-DSS",
                rto_rpo_targets="RTO: 15min, RPO: 5min",
            )

        print("\n" + "=" * 80)
        print("RELIABILITY ASSESSMENT")
        print("=" * 80)
        print(f"Overall Score: {assessment.overall_reliability_score}/100")
        print(f"Maturity: {assessment.maturity.get('overall_maturity_percent')}%")
        
        # Write results
        files = await agent.write_assessment_files(assessment)
        print(f"\nResults written to:")
        print(f"  - {files['markdown']}")
        print(f"  - {files['json']}")
    finally:
        # Ensure proper resource cleanup to avoid unclosed session warnings
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
