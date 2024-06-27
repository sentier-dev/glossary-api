"""Fixtures for dds_glossary tests."""

from pathlib import Path
from typing import Generator

from defusedxml.lxml import parse as parse_xml
from fastapi.testclient import TestClient
from owlready2 import onto_path
from pytest import MonkeyPatch, fixture
from sqlalchemy.engine import Engine
from sqlalchemy_utils import database_exists, drop_database

import dds_glossary.services
from dds_glossary import __version__
from dds_glossary.database import init_engine
from dds_glossary.main import create_app
from dds_glossary.model import (
    Collection,
    Concept,
    ConceptScheme,
    InCollection,
    InScheme,
    SemanticRelation,
)
from dds_glossary.schema import VersionResponse
from dds_glossary.services import GlossaryController
from dds_glossary.xml import (
    collection_from_xml,
    concept_from_xml,
    concept_scheme_from_xml,
    in_collection_from_xml,
    in_scheme_from_xml,
    semantic_relations_from_xml,
)


@fixture(name="dir_data")
def _dir_data() -> Path:
    return Path(__file__).parent / "data"


@fixture(name="file_rdf")
def _file_rdf(dir_data: Path) -> Path:
    return dir_data / "sample.rdf"


@fixture(name="root_element")
def _root_element(file_rdf: Path):
    tree = parse_xml(file_rdf)
    return tree.getroot()


@fixture(name="concept_scheme")
def _concept_scheme(
    root_element,  # pylint: disable=redefined-outer-name
) -> ConceptScheme:
    return concept_scheme_from_xml(
        root_element.find("core:ConceptScheme", namespaces=root_element.nsmap)
    )


@fixture(name="collection")
def _collection(
    root_element,  # pylint: disable=redefined-outer-name
    concept_scheme: ConceptScheme,  # pylint: disable=redefined-outer-name
) -> Collection:
    return collection_from_xml(
        root_element.find("core:Collection", namespaces=root_element.nsmap)
    )


@fixture(name="concept")
def _concept(
    root_element,  # pylint: disable=redefined-outer-name
    concept_scheme: ConceptScheme,  # pylint: disable=redefined-outer-name
) -> Concept:
    return concept_from_xml(
        root_element.find("core:Concept", namespaces=root_element.nsmap)
    )


@fixture(name="semantic_relation")
def _semantic_relation(
    root_element,  # pylint: disable=redefined-outer-name
) -> SemanticRelation:
    return semantic_relations_from_xml(
        root_element.find("core:Concept", namespaces=root_element.nsmap)
    )[0]


@fixture(name="in_scheme")
def _in_scheme(
    root_element,  # pylint: disable=redefined-outer-name
) -> InScheme:
    return in_scheme_from_xml(
        root_element.find("core:Concept", namespaces=root_element.nsmap)
    )[0]


@fixture(name="in_collection")
def _in_collection(
    root_element,  # pylint: disable=redefined-outer-name
) -> InCollection:
    return in_collection_from_xml(
        root_element.find("core:Collection", namespaces=root_element.nsmap)
    )[0]


@fixture(name="version_response")
def _version_response() -> VersionResponse:
    return VersionResponse(version=__version__)


def _clean_database(_engine: Engine) -> None:
    if database_exists(_engine.url):
        drop_database(_engine.url)


@fixture(name="engine")
def _engine() -> Generator[Engine, None, None]:
    engine = init_engine(drop_database_flag=True)
    yield engine
    _clean_database(engine)


@fixture(name="controller")
def _controller(tmp_path: Path) -> Generator[GlossaryController, None, None]:
    controller = GlossaryController(data_dir_path=tmp_path)
    yield controller
    _clean_database(controller.engine)


@fixture(name="client")
def _client(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> Generator[TestClient, None, None]:
    engine = init_engine(drop_database_flag=True)
    monkeypatch.setattr(
        dds_glossary.services,
        "get_controller",
        lambda: GlossaryController(
            data_dir_path=tmp_path,
            engine=engine,
        ),
    )
    app = create_app()
    onto_path.append(str(tmp_path))
    with TestClient(app) as client:
        yield client
    _clean_database(engine)
