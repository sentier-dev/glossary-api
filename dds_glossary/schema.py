"""Schema classes for the dds_glossary package."""

from pydantic import BaseModel, Field

from . import __version__
from .model import Dataset, FailedDataset


class VersionResponse(BaseModel):
    """
    Response model for the version endpoint.

    Attributes:
        version (str): The version of the server.
    """

    version: str = __version__


class InitDatasetsResponse(BaseModel):
    """
    Response model for the init_datasets endpoint.

    Attributes:
        saved_datasets (list[Dataset]): The datasets that were saved.
        failed_datasets (list[FailedDataset]): The datasets that failed to save.
    """

    saved_datasets: list[Dataset] = Field(default_factory=list)
    failed_datasets: list[FailedDataset] = Field(default_factory=list)


class EntityResponse(BaseModel):
    """
    Base response model for the ConceptScheme, Collection and Concept models.

    Attributes:
        iri (str): The IRI of the concept scheme.
        notation (str): The notation of the concept scheme.
        scopeNote (str): The scope note of the concept scheme.
        prefLabel (str): The preferred label of the concept scheme.
    """

    iri: str
    notation: str
    prefLabel: str


class ConceptSchemeResponse(EntityResponse):
    """
    Response model for the ConceptScheme model.

    Attributes:
        scopeNote (str): The scope note of the concept scheme.
    """

    scopeNote: str


class RelationResponse(BaseModel):
    """
    Response model for the SemanticRelation model.

    Attributes:
        type (str): The type of the relation.
        source_concept_iri (str): The IRI of the source concept.
        target_concept_iri (str): The IRI of the target concept.
    """

    type: str
    source_concept_iri: str
    target_concept_iri: str


class ConceptResponse(EntityResponse):
    """
    Response model for the Concept model.

    Attributes:
        identifier (str): The identifier of the concept.
        scopeNote (str): The scope note of the concept.
        altLabels (list[str[]): The alternative labels of the concept.
    """

    identifier: str
    scopeNote: str
    altLabels: list[str]


class FullConceptSchemeResponse(ConceptSchemeResponse):
    """
    Response model for the ConceptScheme model with collections and concepts.

    Attributes:
        collections (list[EntityResponse]): The collections.
        concepts (list[ConceptResponse]): The concepts.
    """

    collections: list[EntityResponse]
    concepts: list[ConceptResponse]


class CollectionResponse(EntityResponse):
    """
    Response model for the Collection model with members.

    Attributes:
        collections (list[EntityResponse]): The collections.
        concepts (list[ConceptResponse]): The concepts.
    """

    collections: list[EntityResponse]
    concepts: list[ConceptResponse]


class FullConceptResponse(ConceptResponse):
    """
    Response model for the Concept model with concept schemes and relations.

    Attributes:
        concept_schemes (list[str]): The IRIs of the concept schemes.
        relations (list[RelationResponse]): The relations.
    """

    concept_schemes: list[str]
    relations: list[RelationResponse]
