"""
LeedHunter CLI - Command line interface

This module provides the main CLI application using Typer.
"""

import asyncio

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from leedhunter import __version__

# Create the main Typer application
app = typer.Typer(
    name="leedhunter",
    help="AI-powered prospect research engine",
    add_completion=False,
)

# Create Rich console for formatted output
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit"""
    if value:
        console.print(
            f"[bold blue]LeedHunter[/bold blue] version [bold green]{__version__}[/bold green]"
        )
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """
    LeedHunter - AI-powered prospect research engine

    Find qualified business opportunities through intelligent research.
    """
    pass


@app.command()
def doctor() -> None:
    """
    Check system health and configuration

    Verifies that all required services and configurations are properly set up.
    """
    from leedhunter.cli.doctor import run_doctor_check

    success = run_doctor_check()
    if not success:
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="Search provider to use (fixture, web)",
    ),
    max_results: int = typer.Option(
        10,
        "--max-results",
        "-n",
        help="Maximum number of results",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show detailed output",
    ),
) -> None:
    """
    Execute a search query

    Returns candidates found through the specified search provider.
    """
    from leedhunter.domain.search.query import QueryBuilder

    console.print(f"\n[bold blue]Searching:[/bold blue] {query}\n")

    # Build query from string
    search_query = QueryBuilder.from_string(query)

    # Select provider
    search_provider = _get_search_provider(provider)

    # Execute search
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Searching...", total=None)
        result = asyncio.run(search_provider.search(search_query))
        progress.update(task, completed=True)

    if not result.success:
        console.print(f"[red]Search failed: {result.error_message}[/red]")
        raise typer.Exit(code=1)

    # Display results
    console.print(f"[green]Found {len(result.candidates)} candidates[/green]\n")

    if result.candidates:
        table = Table(title="Search Results")
        table.add_column("#", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Source", style="green")
        table.add_column("Domain", style="blue")
        table.add_column("Phone", style="yellow")

        for i, candidate in enumerate(result.candidates[:max_results], 1):
            table.add_row(
                str(i),
                candidate.observed_name or "-",
                candidate.source,
                candidate.observed_domain or "-",
                candidate.observed_phone or "-",
            )

        console.print(table)
    else:
        console.print("[yellow]No results found[/yellow]")


@app.command()
def hunt(
    objective: str = typer.Argument(..., help="Prospecting objective"),
    location: str | None = typer.Option(
        None,
        "--location",
        "-l",
        help="Target location",
    ),
    industry: str | None = typer.Option(
        None,
        "--industry",
        "-i",
        help="Target industry",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="Search provider to use (fixture, web)",
    ),
    max_queries: int = typer.Option(
        5,
        "--max-queries",
        "-q",
        help="Maximum number of queries to generate",
    ),
    min_score: float = typer.Option(
        50.0,
        "--min-score",
        "-s",
        help="Minimum lead score",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show detailed output",
    ),
) -> None:
    """
    Run a full research job

    Turns a prospecting objective into qualified business opportunities.
    """
    from leedhunter.application.orchestrator import ResearchConfig, ResearchOrchestrator
    from leedhunter.domain.models import SearchIntent

    console.print(f"\n[bold blue]Starting research:[/bold blue] {objective}\n")

    # Create search intent
    intent = SearchIntent(
        objective=objective,
        location=location,
        industry=industry,
    )

    # Create config
    config = ResearchConfig(
        max_queries=max_queries,
        min_score=min_score,
    )

    # Get provider
    search_provider = _get_search_provider(provider)

    # Create orchestrator
    orchestrator = ResearchOrchestrator(
        search_provider=search_provider,
        config=config,
    )

    # Run research
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running research...", total=None)
        result = asyncio.run(orchestrator.research(intent))
        progress.update(task, completed=True)

    # Display results
    if result.success:
        console.print("\n[bold green]Research Complete![/bold green]\n")

        # Summary
        table = Table(title="Research Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        table.add_row("Queries Generated", str(result.queries_generated))
        table.add_row("Queries Executed", str(result.queries_executed))
        table.add_row("Candidates Found", str(result.candidates_found))
        table.add_row("Entities Created", str(result.entities_created))
        table.add_row("Leads Qualified", str(result.leads_qualified))
        table.add_row("Duration", f"{result.duration_seconds:.1f}s")

        console.print(table)

        # Display leads
        if result.leads:
            console.print(f"\n[bold]Qualified Leads ({len(result.leads)}):[/bold]\n")

            leads_table = Table(title="Qualified Leads")
            leads_table.add_column("#", style="dim")
            leads_table.add_column("Name", style="cyan")
            leads_table.add_column("Score", justify="right")
            leads_table.add_column("Status", style="green")
            leads_table.add_column("Signals", justify="right")
            leads_table.add_column("Opportunities", justify="right")

            for i, lead in enumerate(result.leads, 1):
                leads_table.add_row(
                    str(i),
                    lead.entity.canonical_name,
                    f"{lead.score:.1f}",
                    lead.status.value,
                    str(len(lead.signals)),
                    str(len(lead.opportunities)),
                )

            console.print(leads_table)

            # Show details for top lead
            if verbose and result.leads:
                top_lead = result.leads[0]
                console.print("\n[bold]Top Lead Details:[/bold]")
                console.print(f"  Name: {top_lead.entity.canonical_name}")
                console.print(f"  Score: {top_lead.score:.1f}")
                console.print(f"  Domain: {top_lead.entity.canonical_domain or 'N/A'}")

                if top_lead.entity.identities:
                    console.print("  Identities:")
                    for identity in top_lead.entity.identities:
                        console.print(f"    - {identity.type.value}: {identity.value}")

                if top_lead.signals:
                    console.print("  Signals:")
                    for signal in top_lead.signals:
                        console.print(f"    - {signal.signal_type.value}: {signal.description}")

                if top_lead.opportunities:
                    console.print("  Opportunities:")
                    for opp in top_lead.opportunities:
                        console.print(
                            f"    - {opp.description} (relevance: {opp.relevance_score:.1f})"
                        )
        else:
            console.print("[yellow]No qualified leads found[/yellow]")
    else:
        console.print(f"[red]Research failed: {result.error_message}[/red]")
        raise typer.Exit(code=1)


@app.command()
def entity(
    entity_id: str | None = typer.Argument(None, help="Entity ID to inspect"),
    list_all: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all entities",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show detailed output",
    ),
) -> None:
    """
    Manage and inspect entities

    View entity details, identities, and evidence.
    """
    if list_all:
        console.print("[bold]Listing all entities...[/bold]")
        console.print("[yellow]Database not connected - no entities to display[/yellow]")
    elif entity_id:
        console.print(f"[bold]Inspecting entity: {entity_id}[/bold]")
        console.print("[yellow]Database not connected - cannot fetch entity[/yellow]")
    else:
        console.print("[yellow]Please specify an entity ID or use --list[/yellow]")
        raise typer.Exit(code=1)


@app.command()
def score(
    entity_name: str = typer.Argument(..., help="Entity name to score"),
    has_phone: bool = typer.Option(False, "--phone", help="Entity has phone"),
    has_email: bool = typer.Option(False, "--email", help="Entity has email"),
    has_website: bool = typer.Option(False, "--website", help="Entity has website"),
    industry: str | None = typer.Option(None, "--industry", "-i", help="Industry"),
    location: str | None = typer.Option(None, "--location", "-l", help="Location"),
) -> None:
    """
    Score a lead

    Calculate and display the lead score for an entity.
    """
    from leedhunter.application.scoring.engine import ScoringEngine
    from leedhunter.domain.models import (
        Entity,
        EntityIdentity,
        EntityIdentityType,
        Opportunity,
        Signal,
        SignalType,
    )

    console.print(f"\n[bold blue]Scoring:[/bold blue] {entity_name}\n")

    # Create entity
    identities = []
    if has_phone:
        identities.append(
            EntityIdentity(
                type=EntityIdentityType.PHONE,
                value="+98 912 123 4567",
                normalized_value="09121234567",
                source="manual",
                source_url="manual",
            )
        )
    if has_email:
        identities.append(
            EntityIdentity(
                type=EntityIdentityType.EMAIL,
                value="info@example.com",
                normalized_value="info@example.com",
                source="manual",
                source_url="manual",
            )
        )
    if has_website:
        identities.append(
            EntityIdentity(
                type=EntityIdentityType.WEBSITE,
                value="example.com",
                normalized_value="example.com",
                source="manual",
                source_url="manual",
            )
        )

    metadata = {}
    if industry:
        metadata["industry"] = industry
    if location:
        metadata["location"] = location

    entity = Entity(
        id="manual",
        canonical_name=entity_name,
        identities=identities,
        metadata=metadata,
    )

    # Create sample signals and opportunities
    signals = [
        Signal(
            entity_id="manual",
            signal_type=SignalType.DIGITAL_PRESENCE,
            description="Active digital presence",
            confidence=0.7,
        ),
    ]
    opportunities = [
        Opportunity(
            entity_id="manual",
            description="Potential partnership",
            relevance_score=0.6,
        ),
    ]

    # Calculate score
    engine = ScoringEngine()
    breakdown = engine.calculate_score(entity, signals, opportunities)
    explanation = engine.explain_score(breakdown)

    # Display score
    console.print(
        f"[bold]Total Score: [{_score_color(breakdown.total_score)}]{breakdown.total_score:.1f}/100[/{_score_color(breakdown.total_score)}][/bold]\n"
    )

    table = Table(title="Score Breakdown")
    table.add_column("Factor", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Max", justify="right")
    table.add_column("Percentage", justify="right")

    for factor_name, factor_data in explanation["factors"].items():
        table.add_row(
            factor_name.replace("_", " ").title(),
            f"{factor_data['score']:.1f}",
            f"{factor_data['max']:.1f}",
            f"{factor_data['percentage']:.1f}%",
        )

    console.print(table)

    if explanation["recommendations"]:
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in explanation["recommendations"]:
            console.print(f"  • {rec}")


@app.command()
def export(
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Export format (json, csv)",
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by status (qualified, new, disqualified)",
    ),
    objective: str = typer.Option(
        "Find business leads",
        "--objective",
        help="Research objective to export results for",
    ),
    location: str | None = typer.Option(
        None,
        "--location",
        "-l",
        help="Target location",
    ),
    industry: str | None = typer.Option(
        None,
        "--industry",
        "-i",
        help="Target industry",
    ),
    min_score: float = typer.Option(
        0.0,
        "--min-score",
        help="Minimum lead score to export",
    ),
) -> None:
    """
    Export leads and results

    Run a research job and export qualified leads.
    """
    from leedhunter.application.export.exporter import ExportFormat, ExportOptions, ExportService
    from leedhunter.application.orchestrator import ResearchConfig, ResearchOrchestrator
    from leedhunter.domain.models import LeadStatus, SearchIntent

    console.print("\n[bold blue]Researching and exporting...[/bold blue]\n")

    # Create intent
    intent = SearchIntent(
        objective=objective,
        location=location,
        industry=industry,
    )

    # Run research
    config = ResearchConfig(min_score=min_score)
    orchestrator = ResearchOrchestrator(config=config)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running research...", total=None)
        result = asyncio.run(orchestrator.research(intent))
        progress.update(task, completed=True)

    if not result.success:
        console.print(f"[red]Research failed: {result.error_message}[/red]")
        raise typer.Exit(code=1)

    if not result.leads:
        console.print("[yellow]No qualified leads to export[/yellow]")
        raise typer.Exit(code=0)

    # Determine export format
    if format not in ["json", "csv"]:
        console.print(f"[red]Invalid format: {format}. Use 'json' or 'csv'[/red]")
        raise typer.Exit(code=1)

    export_format = ExportFormat.JSON if format == "json" else ExportFormat.CSV

    # Build status filter
    status_filter = None
    if status:
        try:
            status_filter = LeadStatus(status)
        except ValueError:
            console.print(f"[red]Invalid status: {status}. Use: qualified, new, disqualified[/red]")
            raise typer.Exit(code=1)

    # Export options
    options = ExportOptions(
        format=export_format,
        include_signals=True,
        include_opportunities=True,
        status_filter=status_filter,
        min_score=min_score if min_score > 0 else None,
    )

    # Export
    exporter = ExportService()
    exported = exporter.export_leads(result.leads, options)

    # Output
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(exported)
        console.print(f"[green]Exported {len(result.leads)} leads to {output}[/green]")
    else:
        console.print(exported)

    # Summary
    console.print("\n[bold]Export Summary:[/bold]")
    console.print(f"  Leads exported: {len(result.leads)}")
    console.print(f"  Format: {format}")
    if output:
        console.print(f"  Output: {output}")


def _get_search_provider(provider_name: str | None = None):
    """Get search provider by name"""
    import os

    from leedhunter.application.search.providers.fixture import FixtureSearchProvider

    # Available providers
    providers = {
        "fixture": lambda: FixtureSearchProvider(),
    }

    # Try to add Tavily provider if API key is available
    tavily_key = os.environ.get("LEEDHUNTER_SEARCH_TAVILY_API_KEY", "")
    if tavily_key:
        try:
            from leedhunter.application.search.providers.tavily import (
                TavilyConfig,
                TavilySearchProvider,
            )

            providers["tavily"] = lambda: TavilySearchProvider(TavilyConfig(api_key=tavily_key))
        except Exception:
            pass

    # Try to add Brave provider if API key is available
    brave_key = os.environ.get("LEEDHUNTER_SEARCH_BRAVE_API_KEY", "")
    if brave_key:
        try:
            from leedhunter.application.search.providers.brave import (
                BraveConfig,
                BraveSearchProvider,
            )

            providers["brave"] = lambda: BraveSearchProvider(BraveConfig(api_key=brave_key))
        except Exception:
            pass

    # Select provider
    if provider_name and provider_name in providers:
        return providers[provider_name]()

    # Default provider
    default_provider = os.environ.get("LEEDHUNTER_SEARCH_DEFAULT_PROVIDER", "fixture")
    if default_provider in providers:
        return providers[default_provider]()

    # Fallback to fixture
    return providers["fixture"]()


def _score_color(score: float) -> str:
    """Get color for score"""
    if score >= 70:
        return "green"
    elif score >= 50:
        return "yellow"
    else:
        return "red"


if __name__ == "__main__":
    app()
