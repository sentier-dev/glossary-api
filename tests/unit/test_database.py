"""Tests for dds_glossary.database module."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from dds_glossary.database import (
    Concept,
    ConceptScheme,
    Relationship,
    get_concept_schemes,
    get_concepts_for_scheme,
    get_relationships_for_concept,
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


def test_init_engine_env_var_not_found(monkeypatch) -> None:
    """Test the init_engine function."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError) as exc_info:
        init_engine()
    assert "DATABASE_URL" in str(exc_info.value)


def test_init_engine_database_not_exists_no_drop() -> None:
    """Test the init_engine function."""
    engine = init_engine(drop_database_flag=False)
    engine_init_checks(engine)


def test_init_engine_database_not_exists_drop() -> None:
    """Test the init_engine function."""
    engine = init_engine(drop_database_flag=True)
    engine_init_checks(engine)


def test_init_engine_database_exists_no_drop() -> None:
    """Test the init_engine function."""
    engine = init_engine(drop_database_flag=False)
    engine = init_engine(drop_database_flag=False)
    engine_init_checks(engine)


def test_init_engine_database_exists_drop() -> None:
    """Test the init_engine function."""
    engine = init_engine(drop_database_flag=False)
    engine = init_engine(drop_database_flag=True)
    engine_init_checks(engine)


def test_save_concept_scheme_file() -> None:
    """Test the save_concept_scheme_file function."""
    engine = init_engine(drop_database_flag=True)
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


def test_get_concept_schemes_empty(engine) -> None:
    """Test the get_concept_schemes function."""
    actual_concept_schemes = get_concept_schemes(engine)
    assert actual_concept_schemes == []


def test_get_concept_schemes(engine) -> None:
    """Test the get_concept_schemes function."""
    with Session(engine) as session:
        expected_concept_schemes = [
            ConceptScheme(name=f"concept_scheme_{i}") for i in range(3)
        ]
        session.add_all(expected_concept_schemes)
        session.commit()

        actual_concept_schemes = get_concept_schemes(engine)
        for expected, actual in zip(expected_concept_schemes, actual_concept_schemes):
            assert expected.id == actual.id
            assert expected.name == actual.name


def test_get_concepts_for_scheme_no_result_found(engine) -> None:
    """Test the get_concepts_for_scheme function."""
    scheme_name = "not_found"
    with pytest.raises(NoResultFound) as exc_info:
        get_concepts_for_scheme(engine, scheme_name)
        assert scheme_name in str(exc_info.value)


def test_get_concepts_for_scheme(engine) -> None:
    """Test the get_concepts_for_scheme function."""
    with Session(engine) as session:
        concept_scheme = ConceptScheme(name="test")
        session.add(concept_scheme)
        concepts = [
            Concept(name=f"concept_{i}", scheme_id=concept_scheme.id) for i in range(3)
        ]
        session.add_all(concepts)
        session.commit()

        actual_concepts = get_concepts_for_scheme(engine, concept_scheme.name)
        for expected, actual in zip(concepts, actual_concepts):
            assert expected.id == actual.id
            assert expected.name == actual.name
            assert expected.scheme_id == actual.scheme_id


def test_get_relationships_for_concept_no_result_found(engine) -> None:
    """Test the get_relationships_for_concept function."""
    concept_name = "not_found"
    with pytest.raises(NoResultFound) as exc_info:
        get_relationships_for_concept(engine, concept_name)
        assert concept_name in str(exc_info.value)


def test_get_relationships_for_concept_empty(engine) -> None:
    """Test the get_relationships_for_concept function."""
    with Session(engine) as session:
        concept_scheme = ConceptScheme(name="test")
        session.add(concept_scheme)
        concepts = [
            Concept(name=f"concept_{i}", scheme_id=concept_scheme.id) for i in range(3)
        ]
        session.add_all(concepts)
        session.commit()
        assert not get_relationships_for_concept(engine, concepts[0].name)


def test_get_relationships_for_concept(engine) -> None:
    """Test the get_relationships_for_concept function."""
    with Session(engine) as session:
        concept_scheme = ConceptScheme(name="test")
        session.add(concept_scheme)
        concepts = [
            Concept(name=f"concept_{i}", scheme_id=concept_scheme.id) for i in range(3)
        ]
        session.add_all(concepts)
        session.flush()
        relationships = [
            Relationship(
                source_concept_id=concepts[0].id,
                destination_concept_id=concepts[1].id,
                relationship_type="related",
            ),
            Relationship(
                source_concept_id=concepts[0].id,
                destination_concept_id=concepts[2].id,
                relationship_type="related",
            ),
            Relationship(
                source_concept_id=concepts[1].id,
                destination_concept_id=concepts[2].id,
                relationship_type="related",
            ),
        ]
        session.add_all(relationships)
        session.commit()

        actual_relationships = get_relationships_for_concept(engine, concepts[0].name)
        for expected, actual in zip(relationships, actual_relationships):
            assert expected.source_concept_id == actual.source_concept_id
            assert expected.destination_concept_id == actual.destination_concept_id
            assert expected.relationship_type == actual.relationship_type
