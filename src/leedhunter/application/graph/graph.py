"""
Entity Graph

This module implements the entity graph structure for managing entity relationships.

Business Entity
    ├── Website Identity
    ├── Instagram Identity
    ├── LinkedIn Identity
    ├── Phone Identity
    └── Email Identity

The graph supports:
- Adding entities with identities
- Finding entities by identity
- Merging entities
- Splitting entities (rarely used)
- Graph traversal
"""

from dataclasses import dataclass, field
from typing import Optional

from leedhunter.domain.models import (
    Entity,
    EntityIdentity,
    EntityIdentityType,
)
from leedhunter.domain.normalization import (
    normalize_domain,
    normalize_phone,
    normalize_email,
    normalize_username,
)


@dataclass
class GraphNode:
    """A node in the entity graph"""

    entity: Entity
    identity_keys: set[str] = field(default_factory=set)

    def __post_init__(self):
        """Calculate identity keys on creation"""
        self.identity_keys = self._calculate_keys()

    def _calculate_keys(self) -> set[str]:
        """Calculate normalized identity keys for this node"""
        keys = set()

        # Add domain key
        if self.entity.canonical_domain:
            keys.add(f"domain:{normalize_domain(self.entity.canonical_domain)}")

        # Add identity keys
        for identity in self.entity.identities:
            if identity.type == EntityIdentityType.WEBSITE:
                keys.add(f"domain:{normalize_domain(identity.value)}")
            elif identity.type == EntityIdentityType.EMAIL:
                keys.add(f"email:{normalize_email(identity.value)}")
            elif identity.type == EntityIdentityType.PHONE:
                normalized = normalize_phone(identity.value)
                if normalized:
                    keys.add(f"phone:{normalized}")
            elif identity.type == EntityIdentityType.INSTAGRAM:
                keys.add(f"instagram:{normalize_username(identity.value)}")
            elif identity.type == EntityIdentityType.LINKEDIN:
                keys.add(f"linkedin:{normalize_username(identity.value)}")

        return keys


@dataclass
class GraphEdge:
    """An edge in the entity graph (connects entities through shared identities)"""

    source_id: str
    target_id: str
    shared_keys: list[str]
    confidence: float


class EntityGraph:
    """
    Entity graph for managing entity relationships

    The graph maintains:
    - Nodes: Entities with their identities
    - Index: Fast lookup by identity key
    """

    def __init__(self):
        self._nodes: dict[str, GraphNode] = {}
        self._index: dict[str, set[str]] = {}  # identity_key -> entity_ids

    def add_entity(self, entity: Entity) -> None:
        """
        Add an entity to the graph

        Args:
            entity: Entity to add
        """
        if not entity.id:
            raise ValueError("Entity must have an ID")

        node = GraphNode(entity=entity)
        self._nodes[entity.id] = node

        # Update index
        for key in node.identity_keys:
            if key not in self._index:
                self._index[key] = set()
            self._index[key].add(entity.id)

    def remove_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Remove an entity from the graph

        Args:
            entity_id: ID of entity to remove

        Returns:
            Removed entity, or None if not found
        """
        node = self._nodes.get(entity_id)
        if not node:
            return None

        # Remove from index
        for key in node.identity_keys:
            if key in self._index:
                self._index[key].discard(entity_id)
                if not self._index[key]:
                    del self._index[key]

        # Remove node
        del self._nodes[entity_id]

        return node.entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID

        Args:
            entity_id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        node = self._nodes.get(entity_id)
        return node.entity if node else None

    def find_by_identity(
        self,
        identity_type: EntityIdentityType,
        value: str,
    ) -> Optional[Entity]:
        """
        Find an entity by identity

        Args:
            identity_type: Type of identity
            value: Identity value

        Returns:
            Entity if found, None otherwise
        """
        key = self._make_key(identity_type, value)
        entity_ids = self._index.get(key, set())

        if entity_ids:
            # Return first match
            entity_id = next(iter(entity_ids))
            return self.get_entity(entity_id)

        return None

    def find_all_by_identity(
        self,
        identity_type: EntityIdentityType,
        value: str,
    ) -> list[Entity]:
        """
        Find all entities by identity

        Args:
            identity_type: Type of identity
            value: Identity value

        Returns:
            List of matching entities
        """
        key = self._make_key(identity_type, value)
        entity_ids = self._index.get(key, set())

        return [
            self.get_entity(eid)
            for eid in entity_ids
            if self.get_entity(eid) is not None
        ]

    def add_identity(
        self,
        entity_id: str,
        identity: EntityIdentity,
    ) -> bool:
        """
        Add an identity to an entity

        Args:
            entity_id: Entity ID
            identity: Identity to add

        Returns:
            True if added successfully
        """
        node = self._nodes.get(entity_id)
        if not node:
            return False

        # Add identity to entity
        node.entity.identities.append(identity)

        # Update node keys
        new_keys = node._calculate_keys()
        new_key = self._make_key(identity.type, identity.value)

        if new_key not in node.identity_keys:
            node.identity_keys.add(new_key)

            # Update index
            if new_key not in self._index:
                self._index[new_key] = set()
            self._index[new_key].add(entity_id)

        return True

    def merge_entities(
        self,
        source_id: str,
        target_id: str,
    ) -> Optional[Entity]:
        """
        Merge source entity into target entity

        All identities from source are moved to target.
        Source entity is removed.

        Args:
            source_id: Source entity ID (will be removed)
            target_id: Target entity ID (will receive identities)

        Returns:
            Merged entity, or None if merge failed
        """
        source_node = self._nodes.get(source_id)
        target_node = self._nodes.get(target_id)

        if not source_node or not target_node:
            return None

        # Transfer identities
        for identity in source_node.entity.identities:
            # Check if identity already exists
            exists = any(
                i.type == identity.type and i.normalized_value == identity.normalized_value
                for i in target_node.entity.identities
            )
            if not exists:
                target_node.entity.identities.append(identity)

        # Remove source
        self.remove_entity(source_id)

        # Recalculate target keys
        target_node.identity_keys = target_node._calculate_keys()
        for key in target_node.identity_keys:
            if key not in self._index:
                self._index[key] = set()
            self._index[key].add(target_id)

        return target_node.entity

    def find_merge_candidates(self, entity_id: str) -> list[Entity]:
        """
        Find entities that could be merged with the given entity

        Args:
            entity_id: Entity ID to find candidates for

        Returns:
            List of potential merge candidates
        """
        node = self._nodes.get(entity_id)
        if not node:
            return []

        candidates = set()
        for key in node.identity_keys:
            entity_ids = self._index.get(key, set())
            for eid in entity_ids:
                if eid != entity_id:
                    candidates.add(eid)

        return [
            self.get_entity(eid)
            for eid in candidates
            if self.get_entity(eid) is not None
        ]

    def get_all_entities(self) -> list[Entity]:
        """
        Get all entities in the graph

        Returns:
            List of all entities
        """
        return [node.entity for node in self._nodes.values()]

    def get_entity_count(self) -> int:
        """
        Get number of entities in graph

        Returns:
            Entity count
        """
        return len(self._nodes)

    def get_identity_count(self) -> int:
        """
        Get total number of identities in graph

        Returns:
            Total identity count
        """
        return sum(len(node.entity.identities) for node in self._nodes.values())

    def _make_key(
        self,
        identity_type: EntityIdentityType,
        value: str,
    ) -> str:
        """Make an index key from identity type and value"""
        if identity_type == EntityIdentityType.WEBSITE:
            return f"domain:{normalize_domain(value)}"
        elif identity_type == EntityIdentityType.EMAIL:
            return f"email:{normalize_email(value)}"
        elif identity_type == EntityIdentityType.PHONE:
            normalized = normalize_phone(value)
            return f"phone:{normalized}" if normalized else f"phone:{value}"
        elif identity_type == EntityIdentityType.INSTAGRAM:
            return f"instagram:{normalize_username(value)}"
        elif identity_type == EntityIdentityType.LINKEDIN:
            return f"linkedin:{normalize_username(value)}"
        else:
            return f"{identity_type.value}:{value.lower()}"
