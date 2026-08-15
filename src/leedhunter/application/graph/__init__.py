"""
Entity Graph module

This module implements the entity graph for managing entity relationships.
An entity may have many identities (website, Instagram, LinkedIn, phone, email).
"""

from leedhunter.application.graph.graph import (
    EntityGraph,
    GraphEdge,
    GraphNode,
)

__all__ = [
    "EntityGraph",
    "GraphNode",
    "GraphEdge",
]
