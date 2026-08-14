"""
Tests for CLI module
"""

import pytest
from typer.testing import CliRunner

from leedhunter.cli import app
from leedhunter import __version__


@pytest.fixture
def runner():
    """Create a CLI runner for testing"""
    return CliRunner()


class TestCLI:
    """Tests for main CLI commands"""

    def test_version_flag(self, runner):
        """Test --version flag"""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_version_short_flag(self, runner):
        """Test -v short flag for version"""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_help_command(self, runner):
        """Test --help flag"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "AI-powered prospect research engine" in result.output


class TestDoctorCommand:
    """Tests for doctor command"""

    def test_doctor_command_exists(self, runner):
        """Test that doctor command exists"""
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0
        assert "Check system health" in result.output

    def test_doctor_runs(self, runner):
        """Test that doctor command runs without crashing"""
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code in [0, 1]


class TestSearchCommand:
    """Tests for search command"""

    def test_search_command_exists(self, runner):
        """Test that search command exists"""
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0
        assert "Execute a search query" in result.output

    def test_search_requires_query(self, runner):
        """Test that search requires a query argument"""
        result = runner.invoke(app, ["search"])
        assert result.exit_code != 0

    def test_search_runs(self, runner):
        """Test that search command runs"""
        result = runner.invoke(app, ["search", "test query"])
        # Should run without crashing
        assert result.exit_code == 0 or "Searching" in result.output


class TestHuntCommand:
    """Tests for hunt command"""

    def test_hunt_command_exists(self, runner):
        """Test that hunt command exists"""
        result = runner.invoke(app, ["hunt", "--help"])
        assert result.exit_code == 0
        assert "Run a full research job" in result.output

    def test_hunt_requires_objective(self, runner):
        """Test that hunt requires an objective argument"""
        result = runner.invoke(app, ["hunt"])
        assert result.exit_code != 0

    def test_hunt_runs(self, runner):
        """Test that hunt command runs"""
        result = runner.invoke(app, ["hunt", "Find auto importers"])
        # Should run without crashing
        assert result.exit_code == 0 or "Starting research" in result.output


class TestScoreCommand:
    """Tests for score command"""

    def test_score_command_exists(self, runner):
        """Test that score command exists"""
        result = runner.invoke(app, ["score", "--help"])
        assert result.exit_code == 0
        assert "Score a lead" in result.output

    def test_score_requires_name(self, runner):
        """Test that score requires entity name"""
        result = runner.invoke(app, ["score"])
        assert result.exit_code != 0

    def test_score_runs(self, runner):
        """Test that score command runs"""
        result = runner.invoke(app, ["score", "Test Business"])
        # Should run without crashing
        assert result.exit_code == 0 or "Scoring" in result.output

    def test_score_with_options(self, runner):
        """Test score with options"""
        result = runner.invoke(app, [
            "score", "Test Business",
            "--phone", "--email", "--website",
            "--industry", "automotive",
            "--location", "mazandaran",
        ])
        # Should run without crashing
        assert result.exit_code == 0 or "Scoring" in result.output


class TestEntityCommand:
    """Tests for entity command"""

    def test_entity_command_exists(self, runner):
        """Test that entity command exists"""
        result = runner.invoke(app, ["entity", "--help"])
        assert result.exit_code == 0
        assert "Manage and inspect entities" in result.output


class TestExportCommand:
    """Tests for export command"""

    def test_export_command_exists(self, runner):
        """Test that export command exists"""
        result = runner.invoke(app, ["export", "--help"])
        assert result.exit_code == 0
        assert "Export leads and results" in result.output
