"""Tests for dds_glossary.controllers module."""

from http import HTTPStatus
from pathlib import Path

from pytest import MonkeyPatch
from requests import Response
from sqlalchemy.engine import Engine

from dds_glossary.controllers import GlossaryController

from .. import FILE_RDF


def _init_datasets(_monkeypatch: MonkeyPatch) -> Response:
    response = Response()
    response.status_code = HTTPStatus.OK
    with open(FILE_RDF, "rb") as file:
        response._content = file.read()  # pylint: disable=protected-access
    _monkeypatch.setattr("dds_glossary.database.save_dataset", lambda *_, **__: None)
    _monkeypatch.setattr(
        "dds_glossary.controllers.get_request", lambda *_, **__: response
    )
    _monkeypatch.setattr(
        GlossaryController, "parse_dataset", lambda *_, **__: ([], [], [])
    )
    return response


def test_glossary_controller_parse_dataset(engine: Engine) -> None:
    """Test the GlossaryController parse_dataset method."""
    concept_scheme_iri = "http://data.europa.eu/xsp/cn2024/cn2024"
    concept1_iri = "http://data.europa.eu/xsp/cn2024/020321000080"
    concept2_iri = "http://data.europa.eu/xsp/cn2024/020321000010"
    dataset_path = FILE_RDF
    controller = GlossaryController(engine=engine)
    concept_schemes, concepts, semantic_relations = controller.parse_dataset(
        dataset_path=dataset_path
    )

    assert len(concept_schemes) == 1
    assert len(concepts) == 2
    assert len(semantic_relations) == 1
    assert concept_schemes[0].iri == concept_scheme_iri
    assert concepts[0].iri == concept1_iri
    assert concepts[1].iri == concept2_iri
    assert semantic_relations[0].source_concept_iri == concept1_iri
    assert semantic_relations[0].target_concept_iri == concept2_iri


def test_init_dataset_with_failed_datasets(
    engine: Engine, monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Test the GlossaryController init_datasets method with an exception."""
    get_request = Response()
    get_request.status_code = HTTPStatus.NOT_FOUND
    monkeypatch.setattr(
        "dds_glossary.controllers.get_request", lambda *_, **__: get_request
    )

    controller = GlossaryController(engine=engine, data_dir_path=str(tmp_path))
    saved_datasets, failed_datasets = controller.init_datasets()
    datasets = list(controller.datasets.items())

    assert not saved_datasets
    assert failed_datasets == [
        {
            "dataset": dataset_file,
            "dataset_url": dataset_url,
            "status_code": str(HTTPStatus.NOT_FOUND),
            "response_text": "",
        }
        for dataset_file, dataset_url in datasets
    ]


def test_init_datasets_no_reload_no_existing(
    engine: Engine, monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Test the GlossaryController init_datasets method without reload without
    existing files."""
    get_response = _init_datasets(monkeypatch)

    controller = GlossaryController(engine=engine, data_dir_path=tmp_path)
    saved_datasets, failed_datasets = controller.init_datasets()
    files = list(tmp_path.iterdir())
    datasets = list(controller.datasets.items())

    assert len(files) == 2
    assert files[0].read_bytes() == get_response.content
    assert files[1].read_bytes() == get_response.content
    assert saved_datasets == [
        {"dataset": dataset_file, "dataset_url": dataset_url}
        for dataset_file, dataset_url in datasets
    ]
    assert not failed_datasets


def test_init_datasets_no_reload_existing(
    engine: Engine, monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Test the GlossaryController init_datasets method without reload with
    existing files."""
    get_response = _init_datasets(monkeypatch)
    datasets = {"test.rdf": "http://example.com/test.rdf"}
    old_file = tmp_path / "test.rdf"
    old_file.write_bytes(get_response.content)
    GlossaryController.datasets = datasets

    controller = GlossaryController(engine=engine, data_dir_path=tmp_path)
    saved_datasets, failed_datasets = controller.init_datasets()
    files = list(tmp_path.iterdir())

    assert len(files) == 1
    assert files[0].read_bytes() == get_response.content
    assert saved_datasets == [
        {"dataset": dataset_file, "dataset_url": dataset_url}
        for dataset_file, dataset_url in datasets.items()
    ]
    assert not failed_datasets


def test_init_datasets_reload_existing(
    engine: Engine, monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Test the GlossaryController init_datasets method with reload with
    existing files."""
    get_response = _init_datasets(monkeypatch)
    datasets = {"test.rdf": "http://example.com/test.rdf"}
    old_file = tmp_path / "test.rdf"
    old_file.write_bytes(b"")
    GlossaryController.datasets = datasets

    controller = GlossaryController(engine=engine, data_dir_path=tmp_path)
    saved_datasets, failed_datasets = controller.init_datasets(reload=True)
    files = list(tmp_path.iterdir())

    assert len(files) == 1
    assert files[0].read_bytes() == get_response.content
    assert saved_datasets == [
        {"dataset": dataset_file, "dataset_url": dataset_url}
        for dataset_file, dataset_url in datasets.items()
    ]
    assert not failed_datasets
