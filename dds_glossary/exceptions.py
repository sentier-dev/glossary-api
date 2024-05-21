"""Exception classes for the dds_glossary package."""

from http import HTTPStatus

from fastapi import HTTPException


class DDSGlossaryException(HTTPException):
    """Base class for exceptions in the dds_glossary package."""


class EntityNotFound(DDSGlossaryException):
    """Exception raised when an entity is not found."""

    def __init__(self, entity_name: str, entity_iri: str) -> None:
        super().__init__(HTTPStatus.NOT_FOUND, f"{entity_name} {entity_iri} not found.")


class ConceptSchemeNotFoundException(EntityNotFound):
    """Exception raised when a concept scheme is not found."""

    def __init__(self, concept_scheme_iri: str) -> None:
        super().__init__("Concept scheme", concept_scheme_iri)


class ConceptNotFoundException(EntityNotFound):
    """Exception raised when a concept is not found."""

    def __init__(self, concept_iri: str) -> None:
        super().__init__("Concept", concept_iri)


class CollectionNotFoundException(EntityNotFound):
    """Exception raised when a collection is not found."""

    def __init__(self, collection_iri: str) -> None:
        super().__init__("Collection", collection_iri)
