"""
Main entry point for the Reliability Framework Agent.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

from agents.reliability.agent import ReliabilityFrameworkAgent
from shared.models import (
    AssessmentInput, ArchitectureDocument, DiagramFindings, 
    IncidentPattern, NonFunctionalRequirement, AzureService, 
    SeverityLevel
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_sample_data() -> AssessmentInput:
    """Load sample assessment data for testing."""
    
    SAMPLE_REGION = "East US"
    
    # Sample Azure services
    sample_services = [
        AzureService(
            name="web-app-01",
            service_type="App Service",
            tier="Standard",
            region=SAMPLE_REGION,
            zones=["1"],
            dependencies=["sql-db-01", "storage-01"],
            properties={"instances": 1, "auto_scale": False}
        ),
        AzureService(
            name="sql-db-01",
            service_type="SQL Database",
            tier="General Purpose",
            region=SAMPLE_REGION,
            zones=["1"],
            dependencies=["storage-01"],
            properties={"backup_retention": 7}
        ),
        AzureService(
            name="storage-01",
            service_type="Storage Account",
            tier="Standard_LRS",
            region=SAMPLE_REGION,
            zones=["1"],
            dependencies=[],
            properties={"replication": "LRS"}
        )
    ]
    
    # Sample architecture document
    arch_doc = ArchitectureDocument(
        title="E-commerce Platform Architecture",
        content="Three-tier web application with App Service, SQL Database, and Storage Account",
        document_type="architecture_overview",
        services=sample_services
    )
    
    # Sample incident patterns
    incidents = [
        IncidentPattern(
            incident_id="INC-2024-001",
            root_cause="Single zone failure in East US Zone 1",
            outage_duration_minutes=45,
            affected_services=["web-app-01", "sql-db-01"],
            severity=SeverityLevel.HIGH,
            description="Zone 1 outage caused complete service unavailability"
        )
    ]
    
    # Sample non-functional requirements
    nonfunc_req = NonFunctionalRequirement(
        rto_hours=0.5,  # 30 minutes
        rpo_minutes=5.0,
        availability_target=99.9,
        slo_targets={"response_time_p95": 2.0},
        error_budget=0.1
    )
    
    return AssessmentInput(
        arch_docs=[arch_doc],
        incident_patterns=incidents,
        nonfunc_requirements=nonfunc_req
    )


async def run_assessment() -> Dict[str, Any]:
    """Run reliability assessment."""
    
    logger.info("Starting Reliability Framework Agent assessment")
    
    # Initialize agent
    agent = ReliabilityFrameworkAgent()
    
    # Load assessment data (in production, this would come from external sources)
    assessment_input = load_sample_data()
    
    # Run assessment
    result = await agent.assess(assessment_input)
    
    # Convert result to dict for output
    result_dict = result.dict()
    
    logger.info(f"Assessment completed. Overall reliability score: {result.overall_score}")
    logger.info(f"Found {len(result.findings)} findings and {len(result.recommendations)} recommendations")
    
    return result_dict


def print_assessment_summary(result: Dict[str, Any]):
    """Print a formatted summary of the assessment results."""
    
    print("\n" + "="*80)
    print("AZURE WELL-ARCHITECTED RELIABILITY ASSESSMENT RESULTS")
    print("="*80)
    
    print(f"\nOVERALL RELIABILITY SCORE: {result['overall_score']}/100")
    print(f"Assessment Date: {result['assessment_timestamp']}")
    
    print("\nSUBSCORES:")
    for category, score in result['subscores'].items():
        print(f"  {category.replace('_', ' ').title()}: {score}/100")
    
    print(f"\nFINDINGS ({len(result['findings'])}):")
    for i, finding in enumerate(result['findings'], 1):
        severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(finding['severity'], "⚪")
        print(f"  {i}. {severity_icon} [{finding['severity'].upper()}] {finding['title']}")
        print(f"     {finding['description']}")
    
    print(f"\nTOP RECOMMENDATIONS ({len(result['recommendations'])}):")
    for i, rec in enumerate(result['recommendations'][:5], 1):  # Show top 5
        effort_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(rec['effort_estimate'], "⚪")
        print(f"  {i}. [Priority {rec['priority']}] {effort_icon} {rec['title']}")
        print(f"     {rec['description']}")
        print(f"     Impact: {rec['impact_score']}/10 | Effort: {rec['effort_estimate']}")
    
    print("\nCONSTRAINTS FOR OTHER AGENTS:")
    for key, value in result['constraints_for_other_agents'].items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*80)


async def main():
    """Main entry point."""
    
    try:
        # Run assessment
        result = await run_assessment()
        
        # Print summary
        print_assessment_summary(result)
        
        # Save detailed results
        output_file = "reliability_assessment_results.json"
        import aiofiles
        async with aiofiles.open(output_file, 'w') as f:
            await f.write(json.dumps(result, indent=2, default=str))
        
        print(f"\nDetailed results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())