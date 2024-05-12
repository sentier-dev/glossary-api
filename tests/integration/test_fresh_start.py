"""Integration test for a fresh start scenario."""

from http import HTTPStatus
from pathlib import Path

from fastapi.testclient import TestClient
from owlready2 import onto_path

from dds_glossary import __version__
from dds_glossary.controllers import GlossaryController
from dds_glossary.main import controller


def test_fresh_start(client: TestClient, dir_data: Path) -> None:
    """Test the /fresh_start endpoint."""
    controller.data_dir = dir_data
    onto_path.append(str(dir_data))
    saved_dataset_file = "sample.rdf"
    saved_database_url = "https://example.com/sample.rdf"
    failed_dataset_file = "failed_dataset.rdf"
    failed_database_url = ""
    GlossaryController.datasets = {
        saved_dataset_file: saved_database_url,
        failed_dataset_file: failed_database_url,
    }

    response = client.get("/version")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"version": __version__}

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
                "error": ("[Errno 2] No such file or directory: ''"),
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

    concept_scheme_iri = response.json()["concept_schemes"][0]["iri"]
    response = client.get(f"/concepts?concept_scheme_iri={concept_scheme_iri}&lang=sk")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "concepts": [
            {
                "iri": "http://data.europa.eu/xsp/cn2024/020321000080",
                "identifier": "020321000080",
                "notation": "0203 21",
                "prefLabel": "0203 21 -- Trupy a polovičky trupov",
                "altLabel": "-- Trupy a polovičky trupov",
                "scopeNote": "Frozen carcases and half-carcases of swine",
            },
            {
                "iri": "http://data.europa.eu/xsp/cn2024/020321000010",
                "identifier": "020321000010",
                "notation": "",
                "prefLabel": "- Mrazené",
                "altLabel": "- Frozen",
                "scopeNote": "",
            },
        ]
    }

    concept_dict = response.json()["concepts"][0]
    related_concept_dict = response.json()["concepts"][1]
    response = client.get(f"/concept?concept_iri={concept_dict['iri']}&lang=sk")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        **concept_dict,
        "inSchemes": [concept_scheme_iri],
        "relations": [
            {
                "source_concept_iri": concept_dict["iri"],
                "target_concept_iri": related_concept_dict["iri"],
                "type": "broader",
            }
        ],
    }
