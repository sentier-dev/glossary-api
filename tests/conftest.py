"""Fixtures for dds_glossary tests."""

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy_utils import drop_database

from dds_glossary.database import init_engine
from dds_glossary.main import api_controller, app


@pytest.fixture(name="engine")
def _engine() -> Generator[Engine, None, None]:
    """Return the database engine."""
    engine = init_engine(drop_database_flag=True)
    yield engine
    drop_database(engine.url)


@pytest.fixture(name="client")
def _client(monkeypatch, engine) -> Generator[TestClient, None, None]:
    """Return the test client."""
    monkeypatch.setattr(api_controller, "engine", engine)

    with TestClient(app) as client:
        yield client
