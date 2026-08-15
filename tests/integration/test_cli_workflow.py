"""
Integration tests for LeedHunter CLI workflow

Tests the complete first-user acceptance workflow in fixture mode.
No external services required.
"""

import json
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from leedhunter.cli import app


@pytest.fixture
def runner():
    """Create CLI test runner"""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestVersionCommand:
    """Test version command"""

    def test_version_flag(self, runner):
        """Test --version flag"""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "LeedHunter" in result.output
        assert "0.1.0" in result.output

    def test_version_short_flag(self, runner):
        """Test -v flag"""
        result = runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert "LeedHunter" in result.output


class TestHelpCommand:
    """Test help command"""

    def test_help_flag(self, runner):
        """Test --help flag"""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "LeedHunter" in result.output
        assert "prospect research engine" in result.output.lower()

    def test_all_commands_listed(self, runner):
        """Test that all commands are listed in help"""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "doctor" in result.output
        assert "search" in result.output
        assert "hunt" in result.output
        assert "score" in result.output
        assert "export" in result.output


class TestDoctorCommand:
    """Test doctor command"""

    def test_doctor_runs(self, runner):
        """Test that doctor command runs successfully"""
        result = runner.invoke(app, ["doctor"])

        # Should exit with 0 (non-critical failures are acceptable)
        assert result.exit_code == 0

    def test_doctor_shows_health_checks(self, runner):
        """Test that doctor shows health check results"""
        result = runner.invoke(app, ["doctor"])

        assert "Health Check" in result.output
        assert "Python" in result.output
        assert "Configuration" in result.output

    def test_doctor_critical_checks_pass(self, runner):
        """Test that critical health checks pass"""
        result = runner.invoke(app, ["doctor"])

        assert "All critical checks passed" in result.output


class TestSearchCommand:
    """Test search command"""

    def test_search_basic(self, runner):
        """Test basic search query"""
        result = runner.invoke(app, ["search", "auto importers"])

        assert result.exit_code == 0
        assert "Searching" in result.output
        assert "Found" in result.output
        assert "candidates" in result.output.lower()

    def test_search_with_max_results(self, runner):
        """Test search with --max-results flag"""
        result = runner.invoke(app, ["search", "auto importers", "--max-results", "5"])

        assert result.exit_code == 0
        assert "Found" in result.output

    def test_search_displays_table(self, runner):
        """Test that search displays results in table format"""
        result = runner.invoke(app, ["search", "auto importers"])

        assert result.exit_code == 0
        # Check for table headers
        assert "Name" in result.output
        assert "Source" in result.output
        assert "Domain" in result.output


class TestHuntCommand:
    """Test hunt command"""

    def test_hunt_basic(self, runner):
        """Test basic research job"""
        result = runner.invoke(
            app,
            [
                "hunt",
                "Find auto importers",
                "--location", "Tehran",
                "--industry", "Automotive",
            ]
        )

        assert result.exit_code == 0
        assert "Starting research" in result.output or "Research Complete" in result.output

    def test_hunt_with_max_queries(self, runner):
        """Test research with --max-queries flag"""
        result = runner.invoke(
            app,
            [
                "hunt",
                "Find auto importers",
                "--max-queries", "2",
            ]
        )

        assert result.exit_code == 0

    def test_hunt_shows_summary(self, runner):
        """Test that hunt shows research summary"""
        result = runner.invoke(
            app,
            [
                "hunt",
                "Find auto importers",
                "--location", "Tehran",
                "--industry", "Automotive",
            ]
        )

        assert result.exit_code == 0
        assert "Queries Generated" in result.output or "Research" in result.output


class TestScoreCommand:
    """Test score command"""

    def test_score_basic(self, runner):
        """Test basic lead scoring"""
        result = runner.invoke(
            app,
            [
                "score",
                "Test Business",
                "--phone",
                "--email",
                "--website",
            ]
        )

        assert result.exit_code == 0
        assert "Scoring" in result.output
        assert "Total Score" in result.output

    def test_score_with_industry(self, runner):
        """Test scoring with industry flag"""
        result = runner.invoke(
            app,
            [
                "score",
                "Test Business",
                "--phone",
                "--industry", "automotive",
            ]
        )

        assert result.exit_code == 0
        assert "Total Score" in result.output

    def test_score_shows_breakdown(self, runner):
        """Test that score shows breakdown table"""
        result = runner.invoke(
            app,
            [
                "score",
                "Test Business",
                "--phone",
                "--email",
            ]
        )

        assert result.exit_code == 0
        assert "Score Breakdown" in result.output
        assert "ICP Fit" in result.output or "Icp Fit" in result.output
        assert "Opportunity" in result.output
        assert "Signals" in result.output
        assert "Contactability" in result.output


class TestExportCommand:
    """Test export command"""

    def test_export_json(self, runner, temp_dir):
        """Test JSON export"""
        output_file = temp_dir / "test_output.json"

        result = runner.invoke(
            app,
            [
                "export",
                "--format", "json",
                "--output", str(output_file),
                "--objective", "Find auto importers",
            ]
        )

        assert result.exit_code == 0
        assert "Exported" in result.output
        assert output_file.exists()

        # Verify JSON is valid
        with open(output_file) as f:
            data = json.load(f)
            assert isinstance(data, list)

    def test_export_csv(self, runner, temp_dir):
        """Test CSV export"""
        output_file = temp_dir / "test_output.csv"

        result = runner.invoke(
            app,
            [
                "export",
                "--format", "csv",
                "--output", str(output_file),
                "--objective", "Find auto importers",
            ]
        )

        assert result.exit_code == 0
        assert "Exported" in result.output
        assert output_file.exists()

        # Verify CSV has content
        content = output_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) > 1  # Header + at least one data row

    def test_export_json_to_stdout(self, runner):
        """Test JSON export to stdout"""
        result = runner.invoke(
            app,
            [
                "export",
                "--format", "json",
                "--objective", "Find auto importers",
            ]
        )

        assert result.exit_code == 0

    def test_export_shows_summary(self, runner, temp_dir):
        """Test that export shows summary"""
        output_file = temp_dir / "test_output.json"

        result = runner.invoke(
            app,
            [
                "export",
                "--format", "json",
                "--output", str(output_file),
                "--objective", "Find auto importers",
            ]
        )

        assert result.exit_code == 0
        assert "Export Summary" in result.output
        assert "Leads exported" in result.output


class TestCompleteWorkflow:
    """Test complete first-user workflow"""

    def test_full_workflow(self, runner, temp_dir):
        """Test complete workflow: search → hunt → score → export"""
        # Step 1: Search
        result = runner.invoke(app, ["search", "auto importers"])
        assert result.exit_code == 0
        assert "Found" in result.output

        # Step 2: Hunt
        result = runner.invoke(
            app,
            [
                "hunt",
                "Find auto importers",
                "--location", "Tehran",
                "--industry", "Automotive",
            ]
        )
        assert result.exit_code == 0

        # Step 3: Score
        result = runner.invoke(
            app,
            [
                "score",
                "Test Business",
                "--phone",
                "--email",
                "--website",
            ]
        )
        assert result.exit_code == 0
        assert "Total Score" in result.output

        # Step 4: Export JSON
        json_file = temp_dir / "workflow_output.json"
        result = runner.invoke(
            app,
            [
                "export",
                "--format", "json",
                "--output", str(json_file),
                "--objective", "Find auto importers",
            ]
        )
        assert result.exit_code == 0
        assert json_file.exists()

        # Step 5: Export CSV
        csv_file = temp_dir / "workflow_output.csv"
        result = runner.invoke(
            app,
            [
                "export",
                "--format", "csv",
                "--output", str(csv_file),
                "--objective", "Find auto importers",
            ]
        )
        assert result.exit_code == 0
        assert csv_file.exists()


class TestPersianSupport:
    """Test Persian/Arabic language support"""

    def test_persian_search(self, runner):
        """Test search with Persian query"""
        result = runner.invoke(app, ["search", "واردکنندگان خودرو"])

        assert result.exit_code == 0

    def test_persian_hunt(self, runner):
        """Test research with Persian objective"""
        result = runner.invoke(
            app,
            [
                "hunt",
                "پیدا کردن واردکنندگان خودرو در تهران",
                "--location", "تهران",
                "--industry", "خودرو",
            ]
        )

        assert result.exit_code == 0


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_export_format(self, runner):
        """Test invalid export format"""
        result = runner.invoke(
            app,
            [
                "export",
                "--format", "invalid",
                "--objective", "test",
            ]
        )

        # Should fail gracefully
        assert result.exit_code != 0 or "error" in result.output.lower()

    def test_search_empty_query(self, runner):
        """Test search with empty query"""
        # Typer should handle this - it requires a query argument
        result = runner.invoke(app, ["search"])

        assert result.exit_code != 0  # Should fail - missing required argument


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
