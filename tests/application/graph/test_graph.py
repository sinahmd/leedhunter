"""
Tests for entity graph
"""

from leedhunter.application.graph.graph import EntityGraph, GraphNode
from leedhunter.domain.models import (
    Entity,
    EntityIdentity,
    EntityIdentityType,
)


def create_entity(
    entity_id: str,
    name: str,
    domain: str = None,
    identities: list = None,
) -> Entity:
    """Helper to create test entity"""
    return Entity(
        id=entity_id,
        canonical_name=name,
        canonical_domain=domain,
        identities=identities or [],
    )


def create_identity(
    identity_type: EntityIdentityType,
    value: str,
) -> EntityIdentity:
    """Helper to create test identity"""
    return EntityIdentity(
        type=identity_type,
        value=value,
        normalized_value=value,
        source="test",
        source_url="https://test.com",
    )


class TestGraphNode:
    """Tests for GraphNode"""

    def test_create_node(self):
        """Test creating a GraphNode"""
        entity = create_entity("1", "Test", domain="example.com")
        node = GraphNode(entity=entity)

        assert node.entity == entity
        assert len(node.identity_keys) > 0

    def test_calculate_keys_domain(self):
        """Test key calculation for domain"""
        entity = create_entity("1", "Test", domain="example.com")
        node = GraphNode(entity=entity)

        assert "domain:example.com" in node.identity_keys

    def test_calculate_keys_identities(self):
        """Test key calculation for identities"""
        entity = create_entity(
            "1",
            "Test",
            identities=[
                create_identity(EntityIdentityType.EMAIL, "test@example.com"),
                create_identity(EntityIdentityType.PHONE, "09121234567"),
            ],
        )
        node = GraphNode(entity=entity)

        assert "email:test@example.com" in node.identity_keys
        assert "phone:09121234567" in node.identity_keys


class TestEntityGraph:
    """Tests for EntityGraph"""

    def setup_method(self):
        """Set up test fixtures"""
        self.graph = EntityGraph()

    def test_add_entity(self):
        """Test adding an entity"""
        entity = create_entity("1", "Test", domain="example.com")
        self.graph.add_entity(entity)

        assert self.graph.get_entity_count() == 1
        assert self.graph.get_entity("1") == entity

    def test_remove_entity(self):
        """Test removing an entity"""
        entity = create_entity("1", "Test", domain="example.com")
        self.graph.add_entity(entity)
        removed = self.graph.remove_entity("1")

        assert removed == entity
        assert self.graph.get_entity_count() == 0

    def test_find_by_domain(self):
        """Test finding entity by domain"""
        entity = create_entity("1", "Test", domain="example.com")
        self.graph.add_entity(entity)

        found = self.graph.find_by_identity(
            EntityIdentityType.WEBSITE,
            "example.com",
        )

        assert found == entity

    def test_find_by_email(self):
        """Test finding entity by email"""
        entity = create_entity(
            "1",
            "Test",
            identities=[create_identity(EntityIdentityType.EMAIL, "test@example.com")],
        )
        self.graph.add_entity(entity)

        found = self.graph.find_by_identity(
            EntityIdentityType.EMAIL,
            "test@example.com",
        )

        assert found == entity

    def test_find_by_phone(self):
        """Test finding entity by phone"""
        entity = create_entity(
            "1",
            "Test",
            identities=[create_identity(EntityIdentityType.PHONE, "09121234567")],
        )
        self.graph.add_entity(entity)

        found = self.graph.find_by_identity(
            EntityIdentityType.PHONE,
            "09121234567",
        )

        assert found == entity

    def test_find_not_found(self):
        """Test when entity not found"""
        entity = create_entity("1", "Test", domain="example.com")
        self.graph.add_entity(entity)

        found = self.graph.find_by_identity(
            EntityIdentityType.WEBSITE,
            "other.com",
        )

        assert found is None

    def test_add_identity(self):
        """Test adding an identity to an entity"""
        entity = create_entity("1", "Test", domain="example.com")
        self.graph.add_entity(entity)

        new_identity = create_identity(EntityIdentityType.EMAIL, "test@example.com")
        result = self.graph.add_identity("1", new_identity)

        assert result is True
        assert len(self.graph.get_entity("1").identities) == 1

    def test_add_identity_not_found(self):
        """Test adding identity to non-existent entity"""
        new_identity = create_identity(EntityIdentityType.EMAIL, "test@example.com")
        result = self.graph.add_identity("nonexistent", new_identity)

        assert result is False

    def test_merge_entities(self):
        """Test merging entities"""
        entity1 = create_entity(
            "1",
            "Test 1",
            identities=[create_identity(EntityIdentityType.EMAIL, "test@example.com")],
        )
        entity2 = create_entity(
            "2",
            "Test 2",
            identities=[create_identity(EntityIdentityType.PHONE, "09121234567")],
        )

        self.graph.add_entity(entity1)
        self.graph.add_entity(entity2)

        merged = self.graph.merge_entities("1", "2")

        assert merged is not None
        assert merged.id == "2"
        assert len(merged.identities) == 2
        assert self.graph.get_entity_count() == 1

    def test_merge_entities_with_duplicate(self):
        """Test merging entities with duplicate identities"""
        entity1 = create_entity(
            "1",
            "Test 1",
            identities=[create_identity(EntityIdentityType.EMAIL, "test@example.com")],
        )
        entity2 = create_entity(
            "2",
            "Test 2",
            identities=[
                create_identity(EntityIdentityType.EMAIL, "test@example.com"),
                create_identity(EntityIdentityType.PHONE, "09121234567"),
            ],
        )

        self.graph.add_entity(entity1)
        self.graph.add_entity(entity2)

        merged = self.graph.merge_entities("1", "2")

        assert merged is not None
        assert len(merged.identities) == 2  # No duplicate email

    def test_find_merge_candidates(self):
        """Test finding merge candidates"""
        entity1 = create_entity(
            "1",
            "Test 1",
            identities=[create_identity(EntityIdentityType.EMAIL, "test@example.com")],
        )
        entity2 = create_entity(
            "2",
            "Test 2",
            identities=[create_identity(EntityIdentityType.EMAIL, "test@example.com")],
        )

        self.graph.add_entity(entity1)
        self.graph.add_entity(entity2)

        candidates = self.graph.find_merge_candidates("1")

        assert len(candidates) == 1
        assert candidates[0].id == "2"

    def test_get_all_entities(self):
        """Test getting all entities"""
        entity1 = create_entity("1", "Test 1")
        entity2 = create_entity("2", "Test 2")

        self.graph.add_entity(entity1)
        self.graph.add_entity(entity2)

        entities = self.graph.get_all_entities()

        assert len(entities) == 2

    def test_get_identity_count(self):
        """Test getting identity count"""
        entity = create_entity(
            "1",
            "Test",
            identities=[
                create_identity(EntityIdentityType.EMAIL, "test@example.com"),
                create_identity(EntityIdentityType.PHONE, "09121234567"),
            ],
        )
        self.graph.add_entity(entity)

        assert self.graph.get_identity_count() == 2

    def test_persian_domain(self):
        """Test with Persian domain"""
        entity = create_entity("1", "Test", domain="مثال.com")
        self.graph.add_entity(entity)

        found = self.graph.find_by_identity(
            EntityIdentityType.WEBSITE,
            "مثال.com",
        )

        assert found == entity
