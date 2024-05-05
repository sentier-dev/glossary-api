"""Tests for dds_glossary.database module."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from dds_glossary.database import init_engine


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
