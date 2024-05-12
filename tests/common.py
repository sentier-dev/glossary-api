"""Common functions for tests."""

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from dds_glossary.model import (
    Concept,
    ConceptCollection,
    ConceptScheme,
    InCollection,
    InScheme,
    SemanticRelation,
    SemanticRelationType,
)


def add_concept_schemes(engine: Engine, num: int = 1) -> list[dict]:
    """Add concept schemes to the database."""
    with Session(engine) as session:
        concept_schemes = [
            ConceptScheme(
                iri=f"iri{i}",
                notation=f"notation{i}",
                scopeNote=f"scopeNote{i}",
                prefLabels={"en": f"prefLabel{i}"},
            )
            for i in range(num)
        ]
        session.add_all(concept_schemes)
        session.commit()
        return [concept_scheme.to_dict() for concept_scheme in concept_schemes]


def add_concepts(
    engine: Engine, entries: list[tuple[int, str]]
) -> tuple[list[dict], list[str]]:
    """Add concepts to the database."""
    with Session(engine) as session:
        concepts = [
            Concept(
                iri=f"iri{i}",
                identifier=f"identifier{i}",
                notation=f"notation{i}",
                prefLabels={"en": f"prefLabel{i}"},
                altLabels={"en": f"altLabel{i}"},
                scopeNotes={"en": f"scopeNote{i}"},
            )
            for i in range(len(entries))
        ]
        in_schemes = [
            InScheme(
                member_iri=concepts[i].iri,
                scheme_iri=entries[i][1],
            )
            for i in range(len(entries))
        ]
        session.add_all(concepts)
        session.add_all(in_schemes)
        session.commit()
        return (
            [concept.to_dict() for concept in concepts],
            [in_scheme.scheme_iri for in_scheme in in_schemes],
        )


def add_concept_collections(engine: Engine, entries: list[tuple[str, str]]) -> list[dict]:
    """Add concept collections to the database."""
    with Session(engine) as session:
        concept_collections = [
            ConceptCollection(
                iri=entry[0],
                notation="Collection Notation",
                prefLabels={"en": "Collection Pref Label"},
            )
            for entry in entries
        ]
        in_collections = [
            InCollection(
                member_iri=entry[1],
                collection_iri=entry[0],
            )
            for entry in entries
        ]
        session.add_all(concept_collections)
        session.add_all(in_collections)
        session.commit()
        return [concept_collection.to_dict() for concept_collection in concept_collections]


def add_relations(engine: Engine, entries: list[tuple[str, str]]) -> list[dict]:
    """Add semantic relations to the database."""
    with Session(engine) as session:
        relations = [
            SemanticRelation(
                type=SemanticRelationType.BROADER,
                source_concept_iri=entry[0],
                target_concept_iri=entry[1],
            )
            for entry in entries
        ]
        session.add_all(relations)
        session.commit()
        return [relation.to_dict() for relation in relations]
