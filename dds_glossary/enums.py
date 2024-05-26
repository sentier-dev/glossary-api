"""Enum classes for the dds_glossary package."""

from enum import Enum


class MemberType(Enum):
    """
    Enum class for the types of collection members.

    Attributes:
        CONCEPT (str): The concept type.
        COLLECTION (str): The collection type.
    """

    COLLECTION_MEMBER: str = "collection_member"
    CONCEPT: str = "concept"
    COLLECTION: str = "collection"


class SemanticRelationType(Enum):
    """
    Enum class for the types of semantic relations.

    Attributes:
        BROADER (str): The broader semantic relation.
        NARROWER (str): The narrower semantic relation.
        RELATED (str): The related semantic relation.
        BROADER_TRANSITIVE (str): The transitive broader semantic relation
        NARROWER_TRANSITIVE (str): The transitive narrower semantic relation.
    """

    BROADER: str = "broader"
    NARROWER: str = "narrower"
    RELATED: str = "related"
    BROADER_TRANSITIVE: str = "broaderTransitive"
    NARROWER_TRANSITIVE: str = "narrowerTransitive"
