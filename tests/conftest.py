"""Fixtures for dds_glossary tests."""

from typing import Generator

import pytest
from sqlalchemy import Engine
from sqlalchemy_utils import drop_database

from dds_glossary.database import init_engine


@pytest.fixture(name="engine")
def _engine() -> Generator[Engine, None, None]:
    """Return the database engine."""
    engine = init_engine(drop_database_flag=True)
    yield engine
    drop_database(engine.url)
