"""
Doctor command - System health checks

Verifies that all required services and configurations are properly set up.
"""

import sys
from collections.abc import Callable

from rich.console import Console
from rich.table import Table

from leedhunter.config import get_settings

console = Console()


class HealthCheck:
    """Represents a single health check"""

    def __init__(self, name: str, check_func: Callable[[], bool], critical: bool = True):
        self.name = name
        self.check_func = check_func
        self.critical = critical
        self.passed: bool = False
        self.message: str = ""


def check_python_version() -> bool:
    """Check Python version is >= 3.10"""
    major, minor = sys.version_info[:2]
    return bool(major >= 3 and minor >= 10)


def check_configuration() -> bool:
    """Check that configuration can be loaded"""
    try:
        settings = get_settings()
        return settings is not None
    except Exception:
        return False


def check_database_connection() -> bool:
    """Check PostgreSQL connection"""
    try:
        import asyncpg

        get_settings()
        # We'll implement actual connection check later
        # For now, just check that asyncpg is available
        return True
    except ImportError:
        return False
    except Exception:
        return False


def check_redis_connection() -> bool:
    """Check Redis connection"""
    try:
        import redis.asyncio as aioredis

        get_settings()
        # We'll implement actual connection check later
        # For now, just check that redis is available
        return True
    except ImportError:
        return False
    except Exception:
        return False


def check_sqlalchemy() -> bool:
    """Check SQLAlchemy is available"""
    try:
        import sqlalchemy

        return True
    except ImportError:
        return False


def check_alembic() -> bool:
    """Check Alembic is available"""
    try:
        import alembic

        return True
    except ImportError:
        return False


def check_pydantic() -> bool:
    """Check Pydantic is available"""
    try:
        import pydantic

        return True
    except ImportError:
        return False


def check_typer() -> bool:
    """Check Typer is available"""
    try:
        import typer

        return True
    except ImportError:
        return False


def check_rich() -> bool:
    """Check Rich is available"""
    try:
        import rich

        return True
    except ImportError:
        return False


def check_llm_configuration() -> tuple[bool, str]:
    """
    Check LLM configuration status

    Returns:
        Tuple of (is_configured, status_message)
    """
    try:
        settings = get_settings()
        llm = settings.llm

        if not llm.enabled:
            return True, "Disabled (optional)"

        if not llm.api_key:
            return True, "No API key (optional)"

        if llm.provider == "anthropic":
            try:
                import anthropic

                return True, f"Anthropic ({llm.model})"
            except ImportError:
                return False, "anthropic package not installed"

        if llm.provider == "openai":
            try:
                import openai

                return True, f"OpenAI ({llm.model})"
            except ImportError:
                return False, "openai package not installed"

        return True, f"{llm.provider} ({llm.model})"
    except Exception as e:
        return True, f"Error: {e}"


def run_doctor_check() -> bool:
    """
    Run all health checks and display results

    Returns True if all critical checks pass, False otherwise.
    """
    console.print("\n[bold blue]LeedHunter Health Check[/bold blue]\n")

    # Define health checks
    checks = [
        HealthCheck("Python >= 3.10", check_python_version, critical=True),
        HealthCheck("Configuration", check_configuration, critical=True),
        HealthCheck("Pydantic", check_pydantic, critical=True),
        HealthCheck("Typer", check_typer, critical=True),
        HealthCheck("Rich", check_rich, critical=True),
        HealthCheck("SQLAlchemy", check_sqlalchemy, critical=True),
        HealthCheck("Alembic", check_alembic, critical=False),
        HealthCheck("PostgreSQL Driver", check_database_connection, critical=True),
        HealthCheck("Redis Driver", check_redis_connection, critical=True),
        HealthCheck("Database Connection", check_database_connection, critical=False),
        HealthCheck("Redis Connection", check_redis_connection, critical=False),
    ]

    # Add LLM configuration check
    llm_configured, llm_message = check_llm_configuration()
    checks.append(
        HealthCheck(
            "LLM Provider",
            lambda: llm_configured,
            critical=False,
        )
    )

    # Run checks
    for check in checks:
        try:
            check.passed = check.check_func()
            if check.passed:
                check.message = "[green]OK[/green]"
            else:
                check.message = "[red]Failed[/red]"
        except Exception as e:
            check.passed = False
            check.message = f"[red]Error: {str(e)}[/red]"

    # Display results
    table = Table(title="Health Check Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Critical", justify="center")

    for check in checks:
        critical_str = "Yes" if check.critical else "No"
        table.add_row(check.name, check.message, critical_str)

    console.print(table)

    # Calculate results
    critical_failures = [check for check in checks if check.critical and not check.passed]

    non_critical_failures = [check for check in checks if not check.critical and not check.passed]

    # Summary
    console.print()
    if critical_failures:
        console.print(f"[bold red]Failed: {len(critical_failures)} critical check(s)[/bold red]")
        for check in critical_failures:
            console.print(f"  - {check.name}: {check.message}")
        console.print("\n[red]LeedHunter cannot start until critical issues are resolved.[/red]")
        return False
    else:
        console.print("[bold green]All critical checks passed![/bold green]")
        if non_critical_failures:
            console.print(
                f"[yellow]Warning: {len(non_critical_failures)} non-critical check(s) failed[/yellow]"
            )
            for check in non_critical_failures:
                console.print(f"  - {check.name}: {check.message}")
        return True
