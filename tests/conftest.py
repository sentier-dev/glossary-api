"""Fixtures for dds_glossary tests."""

from os import getenv
from typing import Generator, Optional

import pytest
from sqlalchemy import Engine
from sqlalchemy_utils import database_exists, drop_database

from dds_glossary.database import init_engine


@pytest.fixture(name="database_url")
def _database_url() -> Generator[Optional[str], None, None]:
    """Return the database URL."""
    url = getenv("DATABASE_URL")
    yield url
    if database_exists(url):
        drop_database(url)


@pytest.fixture(name="engine")
def _engine(database_url: str) -> Generator[Engine, None, None]:
    """Return the database engine."""
    engine = init_engine(database_url, drop_database_flag=True)
    yield engine
    drop_database(database_url)
    engine.dispose()
