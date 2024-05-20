"""Common functions for tests."""

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from dds_glossary.model import (
    Collection,
    Concept,
    ConceptScheme,
    Member,
    SemanticRelation,
    SemanticRelationType,
)


def add_concept_schemes(engine: Engine, num: int = 1) -> list[dict]:
    """Add concept schemes to the database."""
    with Session(engine) as session:
        concept_schemes = [
            ConceptScheme(
                iri=f"scheme_iri{i}",
                notation=f"notation{i}",
                scopeNote=f"scopeNote{i}",
                prefLabels={"en": f"prefLabel{i}"},
            )
            for i in range(num)
        ]
        session.add_all(concept_schemes)
        session.commit()
        return [concept_scheme.to_dict() for concept_scheme in concept_schemes]


def add_concepts(engine: Engine, concept_scheme_iris: list[str]) -> list[dict]:
    """Add concepts to the database."""
    with Session(engine, autoflush=False) as session:
        concepts = [
            Concept(
                iri=f"concept_iri{i}",
                identifier=f"identifier{i}",
                notation=f"notation{i}",
                prefLabels={"en": f"prefLabel{i}"},
                altLabels={"en": [f"altLabel{i}"]},
                scopeNotes={"en": f"scopeNote{i}"},
                concept_schemes=[
                    (
                        session.query(ConceptScheme)
                        .where(ConceptScheme.iri == concept_scheme_iris[i])
                        .one()
                    )
                ],
            )
            for i in range(len(concept_scheme_iris))
        ]
        session.add_all(concepts)
        session.commit()
        return [concept.to_dict() for concept in concepts]


def add_collections(engine: Engine, member_iri_lists: list[list[str]]) -> list[dict]:
    """Add collections to the database."""
    with Session(engine) as session:
        collections = [
            Collection(
                iri=f"collection_iri{i}",
                notation=f"notation{i}",
                prefLabels={"en": f"prefLabel{i}"},
                member_iris=member_iri_lists[i],
            )
            for i in range(len(member_iri_lists))
        ]
        session.add_all(collections)
        for collection in collections:
            collection.resolve_members_from_xml(session.query(Member).all())
        session.commit()
        return [collection.to_dict() for collection in collections]


def add_relations(engine: Engine, concept_iris: list[tuple[str, str]]) -> list[dict]:
    """Add semantic relations to the database."""
    with Session(engine) as session:
        relations = [
            SemanticRelation(
                type=SemanticRelationType.BROADER,
                source_concept_iri=source_iri,
                target_concept_iri=target_iri,
            )
            for source_iri, target_iri in concept_iris
        ]
        session.add_all(relations)
        session.commit()
        return [relation.to_dict() for relation in relations]
