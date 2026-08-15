"""
Export Service

This module exports leads and results in JSON and CSV formats.
"""

import csv
import json
from dataclasses import dataclass
from enum import Enum
from io import StringIO

from leedhunter.domain.models import (
    Entity,
    EntityIdentityType,
    Lead,
    LeadStatus,
)


class ExportFormat(str, Enum):
    """Export formats"""

    JSON = "json"
    CSV = "csv"


@dataclass
class ExportOptions:
    """Options for export"""

    format: ExportFormat = ExportFormat.JSON
    include_evidence: bool = False
    include_signals: bool = False
    include_opportunities: bool = False
    status_filter: LeadStatus | None = None
    min_score: float | None = None
    fields: list[str] | None = None


class ExportService:
    """
    Exports leads and results.

    Supports:
    - JSON format
    - CSV format
    - Field selection
    - Filtering by status and score
    """

    def export_leads(
        self,
        leads: list[Lead],
        options: ExportOptions,
    ) -> str:
        """
        Export leads

        Args:
            leads: List of leads to export
            options: Export options

        Returns:
            Exported data as string
        """
        # Apply filters
        filtered_leads = self._filter_leads(leads, options)

        # Convert to export format
        if options.format == ExportFormat.JSON:
            return self._export_json(filtered_leads, options)
        elif options.format == ExportFormat.CSV:
            return self._export_csv(filtered_leads, options)
        else:
            raise ValueError(f"Unsupported format: {options.format}")

    def export_entities(
        self,
        entities: list[Entity],
        options: ExportOptions,
    ) -> str:
        """
        Export entities

        Args:
            entities: List of entities to export
            options: Export options

        Returns:
            Exported data as string
        """
        if options.format == ExportFormat.JSON:
            return self._export_entities_json(entities, options)
        elif options.format == ExportFormat.CSV:
            return self._export_entities_csv(entities, options)
        else:
            raise ValueError(f"Unsupported format: {options.format}")

    def _filter_leads(
        self,
        leads: list[Lead],
        options: ExportOptions,
    ) -> list[Lead]:
        """Apply filters to leads"""
        filtered = leads

        if options.status_filter:
            filtered = [lead for lead in filtered if lead.status == options.status_filter]

        if options.min_score is not None:
            filtered = [lead for lead in filtered if lead.score >= options.min_score]

        return filtered

    def _export_json(
        self,
        leads: list[Lead],
        options: ExportOptions,
    ) -> str:
        """Export leads as JSON"""
        data = []
        for lead in leads:
            lead_data = {
                "entity_id": lead.entity.id,
                "name": lead.entity.canonical_name,
                "domain": lead.entity.canonical_domain,
                "score": lead.score,
                "status": lead.status.value,
                "identities": [
                    {
                        "type": i.type.value,
                        "value": i.value,
                    }
                    for i in lead.entity.identities
                ],
                "metadata": lead.entity.metadata,
            }

            if options.include_signals:
                lead_data["signals"] = [
                    {
                        "type": s.signal_type.value,
                        "description": s.description,
                        "confidence": s.confidence,
                    }
                    for s in lead.signals
                ]

            if options.include_opportunities:
                lead_data["opportunities"] = [
                    {
                        "description": o.description,
                        "relevance_score": o.relevance_score,
                    }
                    for o in lead.opportunities
                ]

            if options.include_evidence:
                lead_data["evidence"] = [
                    {
                        "claim": e.claim,
                        "value": e.value,
                        "source": e.source,
                        "confidence": e.confidence,
                    }
                    for e in lead.evidence
                ]

            if lead.qualification_reasons:
                lead_data["qualification_reasons"] = lead.qualification_reasons

            data.append(lead_data)

        return json.dumps(data, indent=2, ensure_ascii=False)

    def _export_csv(
        self,
        leads: list[Lead],
        options: ExportOptions,
    ) -> str:
        """Export leads as CSV"""
        output = StringIO()
        writer = csv.writer(output)

        # Header
        headers = [
            "entity_id",
            "name",
            "domain",
            "score",
            "status",
            "phone",
            "email",
            "instagram",
            "linkedin",
        ]
        writer.writerow(headers)

        # Rows
        for lead in leads:
            phone = self._get_identity_value(lead.entity, EntityIdentityType.PHONE)
            email = self._get_identity_value(lead.entity, EntityIdentityType.EMAIL)
            instagram = self._get_identity_value(lead.entity, EntityIdentityType.INSTAGRAM)
            linkedin = self._get_identity_value(lead.entity, EntityIdentityType.LINKEDIN)

            writer.writerow(
                [
                    lead.entity.id,
                    lead.entity.canonical_name,
                    lead.entity.canonical_domain or "",
                    f"{lead.score:.1f}",
                    lead.status.value,
                    phone or "",
                    email or "",
                    instagram or "",
                    linkedin or "",
                ]
            )

        return output.getvalue()

    def _export_entities_json(
        self,
        entities: list[Entity],
        options: ExportOptions,
    ) -> str:
        """Export entities as JSON"""
        data = []
        for entity in entities:
            entity_data = {
                "id": entity.id,
                "name": entity.canonical_name,
                "domain": entity.canonical_domain,
                "identities": [
                    {
                        "type": i.type.value,
                        "value": i.value,
                    }
                    for i in entity.identities
                ],
                "metadata": entity.metadata,
            }
            data.append(entity_data)

        return json.dumps(data, indent=2, ensure_ascii=False)

    def _export_entities_csv(
        self,
        entities: list[Entity],
        options: ExportOptions,
    ) -> str:
        """Export entities as CSV"""
        output = StringIO()
        writer = csv.writer(output)

        # Header
        headers = [
            "id",
            "name",
            "domain",
            "phone",
            "email",
            "instagram",
            "linkedin",
        ]
        writer.writerow(headers)

        # Rows
        for entity in entities:
            phone = self._get_identity_value(entity, EntityIdentityType.PHONE)
            email = self._get_identity_value(entity, EntityIdentityType.EMAIL)
            instagram = self._get_identity_value(entity, EntityIdentityType.INSTAGRAM)
            linkedin = self._get_identity_value(entity, EntityIdentityType.LINKEDIN)

            writer.writerow(
                [
                    entity.id,
                    entity.canonical_name,
                    entity.canonical_domain or "",
                    phone or "",
                    email or "",
                    instagram or "",
                    linkedin or "",
                ]
            )

        return output.getvalue()

    def _get_identity_value(
        self,
        entity: Entity,
        identity_type: EntityIdentityType,
    ) -> str | None:
        """Get first identity value of a type"""
        for identity in entity.identities:
            if identity.type == identity_type:
                return identity.value
        return None
