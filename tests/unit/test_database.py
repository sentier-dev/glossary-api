"""Tests for dds_glossary.database module."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from dds_glossary.database import get_concept_schemes, init_engine, save_dataset
from dds_glossary.model import (
    Concept,
    ConceptScheme,
    SemanticRelation,
    SemanticRelationType,
)


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
    assert inspector.has_table("semantic_relations")


def test_init_engine_env_var_not_found(monkeypatch) -> None:
    """Test the init_engine function when the DATABASE_URL environment variable is
    not found."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError) as exc_info:
        init_engine()
    assert "DATABASE_URL" in str(exc_info.value)


def test_init_engine_database_not_exists_no_drop() -> None:
    """Test the init_engine function when the database does not exist and
    drop_database_flag is False."""
    engine = init_engine(drop_database_flag=False)
    engine_init_checks(engine)


def test_init_engine_database_not_exists_drop() -> None:
    """Test the init_engine function when the database does not exist and
    drop_database_flag is True."""
    engine = init_engine(drop_database_flag=True)
    engine_init_checks(engine)


def test_init_engine_database_exists_no_drop() -> None:
    """Test the init_engine function when the database exists and
    drop_database_flag is False."""
    engine = init_engine(drop_database_flag=False)
    engine = init_engine(drop_database_flag=False)
    engine_init_checks(engine)


def test_init_engine_database_exists_drop() -> None:
    """Test the init_engine function when the database exists and
    drop_database_flag is True."""
    engine = init_engine(drop_database_flag=False)
    engine = init_engine(drop_database_flag=True)
    engine_init_checks(engine)


def test_save_dataset_with_no_data(engine: Engine) -> None:
    """Test the save_dataset function with empty data."""
    save_dataset(engine, [], [], [])
    with Session(engine) as session:
        assert session.query(ConceptScheme).count() == 0
        assert session.query(Concept).count() == 0
        assert session.query(SemanticRelation).count() == 0


def test_save_dataset_with_data(engine: Engine) -> None:
    """Test the save_dataset function with data."""
    concept_scheme_iri = "http://example.org/concept_scheme"
    concept1_iri = "http://example.org/concept1"
    concept2_iri = "http://example.org/concept2"
    concept_schemes = [
        ConceptScheme(
            iri=concept_scheme_iri,
            notation="Concept Scheme Notation",
            scopeNote="Concept Scheme Scope Note",
            prefLabels=[{"en": "Concept Scheme Pref Label"}],
        )
    ]
    concepts = [
        Concept(
            iri=concept1_iri,
            identifier="Concept1 Identifier",
            notation="Concept Notation",
            prefLabels=[{"en": "Concept1 Pref Label"}],
            altLabels=[{"en": "Concept1 Alt Label"}],
            scopeNotes=["Concept1 Scope Note"],
            scheme_iri=concept_schemes[0].iri,
        ),
        Concept(
            iri=concept2_iri,
            identifier="Concept2 Identifier",
            notation="Concept2 Notation",
            prefLabels=[{"en": "Concept2 Pref Label"}],
            altLabels=[{"en": "Concept2 Alt Label"}],
            scopeNotes=["Concept2 Scope Note"],
            scheme_iri=concept_schemes[0].iri,
        ),
    ]
    semantic_relations = [
        SemanticRelation(
            type=SemanticRelationType.BROADER,
            source_concept_iri=concepts[0].iri,
            target_concept_iri=concepts[1].iri,
        )
    ]
    save_dataset(engine, concept_schemes, concepts, semantic_relations)

    with Session(engine) as session:
        assert session.query(ConceptScheme).count() == 1
        assert session.query(Concept).count() == 2
        assert session.query(SemanticRelation).count() == 1
        assert session.query(ConceptScheme).one().iri == concept_scheme_iri
        assert session.query(Concept).all()[0].iri == concept1_iri
        assert session.query(SemanticRelation).one().source_concept_iri == concept1_iri
        assert session.query(SemanticRelation).one().target_concept_iri == concept2_iri


def test_get_concept_scheme(engine: Engine) -> None:
    """Test the get_concept_schemes."""
    iri = "http://example.org/concept_scheme"
    with Session(engine) as session:
        session.add(
            ConceptScheme(
                iri=iri,
                notation="notation",
                scopeNote="scopeNote",
                prefLabels={"en": "label"},
            )
        )
        session.commit()

    concept_schemes = get_concept_schemes(engine)
    assert len(concept_schemes) == 1
    assert concept_schemes[0].iri == iri
