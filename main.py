"""
Main entry point for Azure Well-Architected Framework Agents.
"""

import asyncio
import argparse
import logging
from pathlib import Path

from agents.reliability.main import run_assessment as run_reliability_assessment


async def main():
    """Main application entry point."""
    
    parser = argparse.ArgumentParser(
        description="Azure Well-Architected Framework Multi-Agent Assessment"
    )
    
    parser.add_argument(
        "--agent", 
        choices=["reliability", "security", "cost", "operational", "performance"],
        default="reliability",
        help="Which agent to run (default: reliability)"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to agent configuration file"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default="assessment_results.json",
        help="Output file for results (default: assessment_results.json)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {args.agent} agent assessment")
    
    # Run the specified agent
    if args.agent == "reliability":
        result = await run_reliability_assessment()
        logger.info("Reliability assessment completed successfully")
    else:
        logger.error(f"Agent '{args.agent}' not yet implemented")
        return 1
    
    # Save results if output file specified
    if args.output:
        import json
        import aiofiles
        async with aiofiles.open(args.output, 'w') as f:
            await f.write(json.dumps(result, indent=2, default=str))
        logger.info(f"Results saved to {args.output}")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)