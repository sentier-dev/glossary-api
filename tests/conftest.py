"""Fixtures for dds_glossary tests."""

from typing import Generator

from defusedxml.lxml import parse as parse_xml
from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy.engine import Engine
from sqlalchemy_utils import drop_database

from dds_glossary.database import init_engine
from dds_glossary.main import app, controller
from dds_glossary.model import Concept, ConceptScheme, SemanticRelation

from . import FILE_RDF


@fixture(name="root_element")
def _root_element():
    tree = parse_xml(FILE_RDF)
    return tree.getroot()


@fixture(name="concept_scheme")
def _concept_scheme(
    root_element,  # pylint: disable=redefined-outer-name
) -> ConceptScheme:
    return ConceptScheme.from_xml_element(
        root_element.find("core:ConceptScheme", namespaces=root_element.nsmap)
    )


@fixture(name="concept")
def _concept(
    root_element,  # pylint: disable=redefined-outer-name
) -> Concept:
    return Concept.from_xml_element(
        root_element.find("core:Concept", namespaces=root_element.nsmap)
    )


@fixture(name="semantic_relation")
def _semantic_relation(
    root_element,  # pylint: disable=redefined-outer-name
) -> SemanticRelation:
    return SemanticRelation.from_xml_element(
        root_element.find("core:Concept", namespaces=root_element.nsmap)
    )[0]


@fixture(name="engine")
def _engine() -> Generator[Engine, None, None]:
    engine = init_engine(drop_database_flag=True)
    yield engine
    drop_database(engine.url)


@fixture(name="client")
def _client(
    monkeypatch,
    engine,  # pylint: disable=redefined-outer-name
) -> Generator[TestClient, None, None]:
    monkeypatch.setattr(controller, "engine", engine)

    with TestClient(app) as client:
        yield client
