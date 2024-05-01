"""Tests for dds_glossary.database module."""

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from dds_glossary.database import (
    Concept,
    ConceptScheme,
    Relationship,
    init_engine,
    save_concept_scheme_file,
)
from dds_glossary.model import RelationshipTuple


def engine_init_checks(engine: Engine) -> None:
    """Check the engine initialization.

    Args:
        engine (Engine): The database engine.

    Returns:
        None
    """
    assert engine is not None

    inspector = inspect(engine)
    assert inspector.has_table("concept_schemes")
    assert inspector.has_table("concepts")
    assert inspector.has_table("relationships")


def test_init_engine_database_not_exists_no_drop(database_url) -> None:
    """Test the init_engine function."""
    engine = init_engine(database_url, drop_database_flag=False)
    engine_init_checks(engine)


def test_init_engine_database_not_exists_drop(database_url) -> None:
    """Test the init_engine function."""
    engine = init_engine(database_url, drop_database_flag=True)
    engine_init_checks(engine)


def test_init_engine_database_exists_no_drop(database_url) -> None:
    """Test the init_engine function."""
    engine = init_engine(database_url, drop_database_flag=False)
    engine = init_engine(database_url, drop_database_flag=False)
    engine_init_checks(engine)


def test_init_engine_database_exists_drop(database_url) -> None:
    """Test the init_engine function."""
    engine = init_engine(database_url, drop_database_flag=False)
    engine = init_engine(database_url, drop_database_flag=True)
    engine_init_checks(engine)


def test_save_concept_scheme_file(database_url) -> None:
    """Test the save_concept_scheme_file function."""
    engine = init_engine(database_url, drop_database_flag=True)
    concept_scheme_name = "test"
    concepts_names = ["a", "b", "c"]
    relationship_tuples = [
        RelationshipTuple("a", "b", "related"),
        RelationshipTuple("a", "c", "related"),
        RelationshipTuple("b", "c", "related"),
    ]
    save_concept_scheme_file(
        engine,
        concept_scheme_name,
        concepts_names,
        relationship_tuples,
    )

    with Session(engine) as session:
        concept_schemes = session.query(ConceptScheme).all()
        assert len(concept_schemes) == 1
        assert concept_schemes[0].name == concept_scheme_name

        concepts = session.query(Concept).all()
        assert len(concepts) == 3
        assert {concept.name for concept in concepts} == set(concepts_names)

        relationships = session.query(Relationship).all()
        assert len(relationships) == 3
        assert {
            (
                relationship.source_concept_id,
                relationship.destination_concept_id,
                relationship.relationship_type,
            )
            for relationship in relationships
        } == {
            (1, 2, "related"),
            (1, 3, "related"),
            (2, 3, "related"),
        }
