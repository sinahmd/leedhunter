"""
Domain services for LeedHunter

These services implement core business logic that doesn't belong in the models.
They are pure domain logic with no infrastructure dependencies.
"""

from leedhunter.domain.models import (
    Candidate,
    Entity,
    EntityIdentityType,
    Lead,
    LeadStatus,
    SignalType,
)


class EntityResolutionService:
    """
    Service for entity resolution and matching

    Implements the entity resolution pipeline:
    exact matching → deterministic matching → fuzzy matching → semantic matching

    FALSE MERGE IS MORE DANGEROUS THAN FALSE SPLIT
    When uncertain, prefer POSSIBLE_MATCH or NEW_ENTITY over unsafe merge.
    """

    def resolve_candidate(
        self,
        candidate: Candidate,
        existing_entities: list[Entity],
    ) -> tuple[str, Entity | None]:
        """
        Resolve a candidate against existing entities

        Returns:
            Tuple of (decision, matched_entity)
            decision: "MATCH", "POSSIBLE_MATCH", or "NEW_ENTITY"
        """
        # Step 1: Exact matching
        exact_match = self._exact_match(candidate, existing_entities)
        if exact_match:
            return ("MATCH", exact_match)

        # Step 2: Deterministic matching
        deterministic_match = self._deterministic_match(candidate, existing_entities)
        if deterministic_match:
            return ("MATCH", deterministic_match)

        # Step 3: Fuzzy matching
        fuzzy_match = self._fuzzy_match(candidate, existing_entities)
        if fuzzy_match:
            # Check if it's an exact name match (should be treated as MATCH)
            if candidate.observed_name:
                similarity = self._calculate_name_similarity(
                    candidate.observed_name,
                    fuzzy_match.canonical_name,
                )
                if similarity >= 1.0:
                    return ("MATCH", fuzzy_match)
            return ("POSSIBLE_MATCH", fuzzy_match)

        # Step 4: No match found
        return ("NEW_ENTITY", None)

    def _exact_match(
        self,
        candidate: Candidate,
        existing_entities: list[Entity],
    ) -> Entity | None:
        """
        Exact matching based on identifiers

        Matches:
        - Exact domain
        - Exact email
        - Exact phone
        - Exact username on same platform
        """
        for entity in existing_entities:
            # Match by domain
            if candidate.observed_domain and entity.canonical_domain:
                if candidate.observed_domain.lower() == entity.canonical_domain.lower():
                    return entity

            # Match by email
            if candidate.observed_email:
                for identity in entity.identities:
                    if (
                        identity.type == EntityIdentityType.EMAIL
                        and identity.normalized_value.lower() == candidate.observed_email.lower()
                    ):
                        return entity

            # Match by phone
            if candidate.observed_phone:
                normalized_phone = self._normalize_phone(candidate.observed_phone)
                for identity in entity.identities:
                    if (
                        identity.type == EntityIdentityType.PHONE
                        and self._normalize_phone(identity.normalized_value) == normalized_phone
                    ):
                        return entity

            # Match by username on same platform
            if candidate.observed_username:
                platform = candidate.metadata.get("platform", "")
                for identity in entity.identities:
                    if (
                        identity.type == self._platform_to_identity_type(platform)
                        and identity.normalized_value.lower() == candidate.observed_username.lower()
                    ):
                        return entity

        return None

    def _deterministic_match(
        self,
        candidate: Candidate,
        existing_entities: list[Entity],
    ) -> Entity | None:
        """
        Deterministic matching based on normalized identifiers

        Matches:
        - Normalized domain (removing www., http://, etc.)
        - Normalized phone (removing spaces, dashes, country codes)
        """
        for entity in existing_entities:
            # Match by normalized domain
            if candidate.observed_domain and entity.canonical_domain:
                norm_candidate_domain = self._normalize_domain(candidate.observed_domain)
                norm_entity_domain = self._normalize_domain(entity.canonical_domain)
                if norm_candidate_domain == norm_entity_domain:
                    return entity

        return None

    def _fuzzy_match(
        self,
        candidate: Candidate,
        existing_entities: list[Entity],
    ) -> Entity | None:
        """
        Fuzzy matching based on name similarity

        This is conservative - only returns matches with very high similarity
        to avoid false merges.

        NEVER merge two businesses merely because their names are similar.
        """
        if not candidate.observed_name:
            return None

        for entity in existing_entities:
            similarity = self._calculate_name_similarity(
                candidate.observed_name,
                entity.canonical_name,
            )
            # Very conservative threshold to avoid false merges
            if similarity >= 0.95:
                return entity

        return None

    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain for comparison"""
        domain = domain.lower().strip()
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        # Remove trailing slash
        domain = domain.rstrip("/")
        return domain

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison"""
        # Remove all non-digit characters
        digits = "".join(c for c in phone if c.isdigit())
        # Handle Iranian phone numbers
        if digits.startswith("98") and len(digits) > 10:
            digits = "0" + digits[2:]
        elif digits.startswith("0098") and len(digits) > 12:
            digits = "0" + digits[4:]
        return digits

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names

        Uses simple character-based similarity for now.
        In production, this should use more sophisticated algorithms.
        """
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()

        if name1 == name2:
            return 1.0

        # Simple Jaccard similarity on character bigrams
        bigrams1 = set(name1[i : i + 2] for i in range(len(name1) - 1))
        bigrams2 = set(name2[i : i + 2] for i in range(len(name2) - 1))

        if not bigrams1 or not bigrams2:
            return 0.0

        intersection = bigrams1 & bigrams2
        union = bigrams1 | bigrams2

        return len(intersection) / len(union)

    def _platform_to_identity_type(self, platform: str) -> EntityIdentityType:
        """Convert platform string to EntityIdentityType"""
        platform_map = {
            "instagram": EntityIdentityType.INSTAGRAM,
            "linkedin": EntityIdentityType.LINKEDIN,
            "website": EntityIdentityType.WEBSITE,
            "google": EntityIdentityType.GOOGLE_PROFILE,
        }
        return platform_map.get(platform.lower(), EntityIdentityType.WEBSITE)

    def explain_match(
        self,
        candidate: Candidate,
        entity: Entity,
        decision: str,
    ) -> dict:
        """
        Generate structured explanation for entity match

        This is required for debugging and future human review.
        """
        matched = []
        conflicts = []

        # Check what matched
        if candidate.observed_domain and entity.canonical_domain:
            if candidate.observed_domain.lower() == entity.canonical_domain.lower():
                matched.append("exact domain")
            elif self._normalize_domain(candidate.observed_domain) == self._normalize_domain(
                entity.canonical_domain
            ):
                matched.append("normalized domain")

        if candidate.observed_email:
            for identity in entity.identities:
                if (
                    identity.type == EntityIdentityType.EMAIL
                    and identity.normalized_value.lower() == candidate.observed_email.lower()
                ):
                    matched.append("exact email")

        if candidate.observed_username:
            for identity in entity.identities:
                if identity.normalized_value.lower() == candidate.observed_username.lower():
                    matched.append(f"same {identity.type.value} username")

        if candidate.observed_phone:
            normalized_candidate_phone = self._normalize_phone(candidate.observed_phone)
            for identity in entity.identities:
                if (
                    identity.type == EntityIdentityType.PHONE
                    and self._normalize_phone(identity.normalized_value)
                    == normalized_candidate_phone
                ):
                    matched.append("same phone")

        # Calculate score
        score = min(100, len(matched) * 30)

        return {
            "decision": decision,
            "score": score,
            "matched": matched,
            "conflicts": conflicts,
        }


class ScoringService:
    """
    Service for scoring leads

    Scoring must be deterministic and explainable.
    Do NOT ask an LLM to give a score - calculate from explicit factors.
    """

    def calculate_score(self, lead: Lead) -> float:
        """
        Calculate lead score from explicit factors

        Factors:
        - ICP Fit (0-25 points)
        - Opportunity (0-25 points)
        - Signals (0-25 points)
        - Contactability (0-25 points)
        """
        icp_score = self._calculate_icp_fit(lead)
        opportunity_score = self._calculate_opportunity(lead)
        signal_score = self._calculate_signals(lead)
        contactability_score = self._calculate_contactability(lead)

        total_score = icp_score + opportunity_score + signal_score + contactability_score

        return min(100.0, max(0.0, total_score))

    def _calculate_icp_fit(self, lead: Lead) -> float:
        """
        Calculate ICP (Ideal Customer Profile) fit score

        Based on:
        - Industry match
        - Location match
        - Business type
        """
        score = 0.0
        metadata = lead.entity.metadata

        # Industry match
        if "industry" in metadata:
            score += 10.0

        # Location match
        if "location" in metadata:
            score += 10.0

        # Business type indicators
        if any(identity.type == EntityIdentityType.WEBSITE for identity in lead.entity.identities):
            score += 5.0

        return min(25.0, score)

    def _calculate_opportunity(self, lead: Lead) -> float:
        """
        Calculate opportunity score

        Based on:
        - Number of opportunities
        - Relevance of opportunities
        """
        if not lead.opportunities:
            return 0.0

        # Average relevance score
        avg_relevance = sum(o.relevance_score for o in lead.opportunities) / len(lead.opportunities)

        # Number of opportunities (capped at 5)
        opportunity_count = min(5, len(lead.opportunities))

        return min(25.0, avg_relevance * 15.0 + opportunity_count * 2.0)

    def _calculate_signals(self, lead: Lead) -> float:
        """
        Calculate signals score

        Based on:
        - Number of signals
        - Signal confidence
        - Signal types
        """
        if not lead.signals:
            return 0.0

        # Average confidence
        avg_confidence = sum(s.confidence for s in lead.signals) / len(lead.signals)

        # Number of unique signal types
        signal_types = set(s.signal_type for s in lead.signals)

        # Bonus for expansion signals
        expansion_bonus = 5.0 if SignalType.EXPANSION in signal_types else 0.0

        return min(25.0, avg_confidence * 10.0 + len(signal_types) * 3.0 + expansion_bonus)

    def _calculate_contactability(self, lead: Lead) -> float:
        """
        Calculate contactability score

        Based on:
        - Has phone number
        - Has email
        - Has social media presence
        """
        score = 0.0

        for identity in lead.entity.identities:
            if (
                identity.type == EntityIdentityType.PHONE
                or identity.type == EntityIdentityType.EMAIL
            ):
                score += 10.0
            elif (
                identity.type == EntityIdentityType.INSTAGRAM
                or identity.type == EntityIdentityType.LINKEDIN
            ):
                score += 3.0

        return min(25.0, score)

    def explain_score(self, lead: Lead) -> dict:
        """
        Generate structured explanation for lead score

        This is required for debugging and transparency.
        """
        icp_score = self._calculate_icp_fit(lead)
        opportunity_score = self._calculate_opportunity(lead)
        signal_score = self._calculate_signals(lead)
        contactability_score = self._calculate_contactability(lead)

        return {
            "total_score": self.calculate_score(lead),
            "factors": {
                "icp_fit": icp_score,
                "opportunity": opportunity_score,
                "signals": signal_score,
                "contactability": contactability_score,
            },
            "evidence_count": lead.get_evidence_count(),
            "signal_count": lead.get_signal_count(),
            "opportunity_count": lead.get_opportunity_count(),
        }


class QualificationService:
    """
    Service for qualifying leads

    Determines if a lead should be qualified, disqualified, or kept as new.
    """

    def qualify_lead(self, lead: Lead, min_score: float = 60.0) -> Lead:
        """
        Qualify a lead based on score and other factors

        Returns updated lead with qualification status and reasons.
        """
        reasons = []
        status = LeadStatus.NEW

        # Check score threshold
        if lead.score >= min_score:
            reasons.append(f"Score {lead.score:.1f} meets minimum threshold {min_score}")
            status = LeadStatus.QUALIFIED
        else:
            reasons.append(f"Score {lead.score:.1f} below minimum threshold {min_score}")
            status = LeadStatus.DISQUALIFIED

        # Check for contact information
        if lead.has_contact_info():
            reasons.append("Has contact information")
        else:
            reasons.append("Missing contact information")

        # Check for evidence
        if lead.get_evidence_count() > 0:
            reasons.append(f"Has {lead.get_evidence_count()} evidence items")

        # Check for signals
        if lead.get_signal_count() > 0:
            reasons.append(f"Has {lead.get_signal_count()} signals")

        # Update lead
        lead.status = status
        lead.qualification_reasons = reasons

        return lead

    def is_qualifiable(self, lead: Lead, min_score: float = 60.0) -> bool:
        """
        Check if a lead can be qualified

        A lead is qualifiable if:
        1. Score meets minimum threshold
        2. Has at least one identity
        3. Has at least one signal or opportunity
        """
        return (
            lead.score >= min_score
            and len(lead.entity.identities) > 0
            and (lead.get_signal_count() > 0 or lead.get_opportunity_count() > 0)
        )
