"""Fixtures for dds_glossary tests."""

from os import getenv
from typing import Generator, Optional

import pytest
from sqlalchemy_utils import database_exists, drop_database


@pytest.fixture
def database_url() -> Generator[Optional[str], None, None]:
    """Return the database URL."""
    url = getenv("DATABASE_URL")
    yield url
    if database_exists(url):
        drop_database(url)
