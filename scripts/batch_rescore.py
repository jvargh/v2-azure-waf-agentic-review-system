"""
Batch Rescore Script
====================
Rescores all historical assessments to populate subcategory_details with:
- Base scores, final scores, deltas
- Coverage penalties, gap penalties
- Evidence found/missing lists
- Normalization factors

Usage:
    python scripts/batch_rescore.py [--dry-run]

Options:
    --dry-run    Show what would be rescored without making changes
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx
import asyncio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

console = Console()

API_BASE = "http://localhost:8000/api"


async def get_all_assessments():
    """Fetch all assessment IDs from the API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{API_BASE}/assessments")
            response.raise_for_status()
            assessments = response.json()
            return [a["id"] for a in assessments]
        except httpx.HTTPError as e:
            console.print(f"[red]Error fetching assessments: {e}[/red]")
            return []


async def rescore_assessment(assessment_id: str, dry_run: bool = False):
    """Rescore a single assessment."""
    if dry_run:
        return {"id": assessment_id, "status": "skipped (dry-run)", "success": True}
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(f"{API_BASE}/assessments/{assessment_id}/rescore")
            response.raise_for_status()
            data = response.json()
            return {
                "id": assessment_id,
                "status": "rescored",
                "pillars_updated": len(data.get("pillar_scores", [])),
                "success": True
            }
        except httpx.HTTPError as e:
            return {
                "id": assessment_id,
                "status": f"failed: {str(e)}",
                "success": False
            }


async def batch_rescore(dry_run: bool = False):
    """Rescore all assessments with progress tracking."""
    console.print("[bold cyan]Batch Rescore Utility[/bold cyan]")
    console.print()
    
    if dry_run:
        console.print("[yellow]DRY-RUN MODE: No changes will be made[/yellow]")
        console.print()
    
    # Fetch all assessments
    console.print("Fetching assessments...")
    assessment_ids = await get_all_assessments()
    
    if not assessment_ids:
        console.print("[yellow]No assessments found to rescore[/yellow]")
        return
    
    console.print(f"[green]Found {len(assessment_ids)} assessment(s)[/green]")
    console.print()
    
    # Rescore with progress bar
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task(
            f"{'[DRY-RUN] ' if dry_run else ''}Rescoring assessments...",
            total=len(assessment_ids)
        )
        
        for assessment_id in assessment_ids:
            result = await rescore_assessment(assessment_id, dry_run)
            results.append(result)
            progress.update(task, advance=1)
    
    # Summary table
    console.print()
    table = Table(title="Rescore Summary")
    table.add_column("Assessment ID", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Pillars Updated", justify="right")
    
    for result in results:
        status_style = "green" if result["success"] else "red"
        table.add_row(
            result["id"],
            f"[{status_style}]{result['status']}[/{status_style}]",
            str(result.get("pillars_updated", "-"))
        )
    
    console.print(table)
    
    # Final stats
    console.print()
    success_count = sum(1 for r in results if r["success"])
    console.print(f"[bold]Total:[/bold] {len(results)}")
    console.print(f"[bold green]Success:[/bold green] {success_count}")
    console.print(f"[bold red]Failed:[/bold red] {len(results) - success_count}")
    
    if dry_run:
        console.print()
        console.print("[yellow]Run without --dry-run to apply changes[/yellow]")


def main():
    parser = argparse.ArgumentParser(description="Batch rescore all assessments")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be rescored without making changes"
    )
    args = parser.parse_args()
    
    try:
        asyncio.run(batch_rescore(dry_run=args.dry_run))
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
