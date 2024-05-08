"""Integration test for a fresh start scenario."""

from http import HTTPStatus

from fastapi.testclient import TestClient

from dds_glossary.controllers import GlossaryController
from dds_glossary.main import controller

from .. import DIR_DATA


def test_fresh_start(client: TestClient) -> None:
    """Test the /fresh_start endpoint."""
    controller.data_dir = DIR_DATA
    saved_dataset_file = "sample.rdf"
    saved_database_url = "https://example.com/sample.rdf"
    failed_dataset_file = "failed_dataset.rdf"
    failed_database_url = ""
    GlossaryController.datasets = {
        saved_dataset_file: saved_database_url,
        failed_dataset_file: failed_database_url,
    }

    response = client.post("/init_datasets")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "saved_datasets": [
            {
                "dataset": saved_dataset_file,
                "dataset_url": saved_database_url,
            }
        ],
        "failed_datasets": [
            {
                "dataset": failed_dataset_file,
                "dataset_url": failed_database_url,
                "error": (
                    "Invalid URL '': No scheme supplied. " "Perhaps you meant https://?"
                ),
            }
        ],
    }

    response = client.get("/schemes?lang=sk")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "concept_schemes": [
            {
                "iri": "http://data.europa.eu/xsp/cn2024/cn2024",
                "notation": "CN 2024",
                "scopeNote": (
                    "http://publications.europa.eu/resource/oj/JOC_2019_119_R_0001"
                ),
                "prefLabel": "Kombinovaná Nomenklatúra, 2024 (KN 2024)",
            }
        ]
    }
