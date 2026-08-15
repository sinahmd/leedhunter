"""
Tests for export functionality
"""

import csv
import json
from io import StringIO

from leedhunter.application.export.exporter import (
    ExportFormat,
    ExportOptions,
    ExportService,
)
from leedhunter.domain.models import (
    Entity,
    EntityIdentity,
    EntityIdentityType,
    Evidence,
    Lead,
    LeadStatus,
    Opportunity,
    Signal,
    SignalType,
)


class TestExportFormat:
    """Tests for ExportFormat"""

    def test_format_values(self):
        """Test format enum values"""
        assert ExportFormat.JSON == "json"
        assert ExportFormat.CSV == "csv"


class TestExportOptions:
    """Tests for ExportOptions"""

    def test_default_options(self):
        """Test default export options"""
        options = ExportOptions()
        assert options.format == ExportFormat.JSON
        assert options.include_evidence is False


class TestExportService:
    """Tests for ExportService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = ExportService()

    def _create_sample_lead(self) -> Lead:
        """Create a sample lead for testing"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            canonical_domain="example.com",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="+98 912 123 4567",
                    normalized_value="09121234567",
                    source="test",
                    source_url="https://test.com",
                ),
                EntityIdentity(
                    type=EntityIdentityType.EMAIL,
                    value="test@example.com",
                    normalized_value="test@example.com",
                    source="test",
                    source_url="https://test.com",
                ),
            ],
            metadata={"industry": "automotive"},
        )

        return Lead(
            entity=entity,
            signals=[
                Signal(
                    entity_id="entity_1",
                    signal_type=SignalType.EXPANSION,
                    description="Expanding",
                    confidence=0.8,
                ),
            ],
            opportunities=[
                Opportunity(
                    entity_id="entity_1",
                    description="Partnership",
                    relevance_score=0.7,
                ),
            ],
            evidence=[
                Evidence(
                    entity_id="entity_1",
                    claim="Has website",
                    value="example.com",
                    source="google",
                    source_url="https://google.com",
                    confidence=0.9,
                ),
            ],
            score=75.0,
            status=LeadStatus.QUALIFIED,
            qualification_reasons=["Strong signals"],
        )

    def test_export_json(self):
        """Test JSON export"""
        lead = self._create_sample_lead()
        options = ExportOptions(format=ExportFormat.JSON)

        result = self.service.export_leads([lead], options)

        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["name"] == "Test Business"
        assert data[0]["score"] == 75.0

    def test_export_json_with_signals(self):
        """Test JSON export with signals"""
        lead = self._create_sample_lead()
        options = ExportOptions(format=ExportFormat.JSON, include_signals=True)

        result = self.service.export_leads([lead], options)

        data = json.loads(result)
        assert "signals" in data[0]
        assert len(data[0]["signals"]) == 1

    def test_export_json_with_opportunities(self):
        """Test JSON export with opportunities"""
        lead = self._create_sample_lead()
        options = ExportOptions(format=ExportFormat.JSON, include_opportunities=True)

        result = self.service.export_leads([lead], options)

        data = json.loads(result)
        assert "opportunities" in data[0]
        assert len(data[0]["opportunities"]) == 1

    def test_export_csv(self):
        """Test CSV export"""
        lead = self._create_sample_lead()
        options = ExportOptions(format=ExportFormat.CSV)

        result = self.service.export_leads([lead], options)

        reader = csv.reader(StringIO(result))
        rows = list(reader)
        assert len(rows) == 2  # Header + 1 row
        assert rows[0][0] == "entity_id"
        assert rows[1][1] == "Test Business"

    def test_export_filter_by_status(self):
        """Test filtering by status"""
        lead = self._create_sample_lead()
        options = ExportOptions(
            format=ExportFormat.JSON,
            status_filter=LeadStatus.QUALIFIED,
        )

        result = self.service.export_leads([lead], options)

        data = json.loads(result)
        assert len(data) == 1

    def test_export_filter_by_score(self):
        """Test filtering by score"""
        lead = self._create_sample_lead()
        options = ExportOptions(
            format=ExportFormat.JSON,
            min_score=80.0,
        )

        result = self.service.export_leads([lead], options)

        data = json.loads(result)
        assert len(data) == 0  # Score is 75, less than 80

    def test_export_persian_content(self):
        """Test exporting Persian content"""
        entity = Entity(
            id="entity_1",
            canonical_name="شرکت تست",
            identities=[],
        )
        lead = Lead(
            entity=entity,
            score=50.0,
            status=LeadStatus.NEW,
        )

        options = ExportOptions(format=ExportFormat.JSON)
        result = self.service.export_leads([lead], options)

        assert "شرکت تست" in result

    def test_export_entities_json(self):
        """Test exporting entities as JSON"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            canonical_domain="example.com",
        )

        options = ExportOptions(format=ExportFormat.JSON)
        result = self.service.export_entities([entity], options)

        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["name"] == "Test Business"

    def test_export_entities_csv(self):
        """Test exporting entities as CSV"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            canonical_domain="example.com",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="+98 912 123 4567",
                    normalized_value="09121234567",
                    source="test",
                    source_url="https://test.com",
                ),
            ],
        )

        options = ExportOptions(format=ExportFormat.CSV)
        result = self.service.export_entities([entity], options)

        reader = csv.reader(StringIO(result))
        rows = list(reader)
        assert len(rows) == 2  # Header + 1 row
