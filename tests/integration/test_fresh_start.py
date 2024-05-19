"""Integration test for a fresh start scenario."""

from http import HTTPStatus
from os import getenv as os_getenv
from pathlib import Path
from typing import Mapping

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

    api_key = os_getenv("API_KEY", "")
    headers: Mapping[str, str] = {"X-API-Key": api_key}
    response = client.post("/init_datasets", headers=headers)
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
    scheme_iris = [scheme["iri"] for scheme in response.json()["concept_schemes"]]

    member_dicts = [
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
        {
            "iri": "https://example.org/collection1",
            "notation": "Collection1Notation",
            "prefLabel": "Collection1PrefLabel",
        },
        {
            "iri": "https://example.org/collection2",
            "notation": "Collection2Notation",
            "prefLabel": "Collection2PrefLabel",
        },
    ]
    response = client.get(f"/concepts?concept_scheme_iri={scheme_iris[0]}&lang=sk")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"concepts": member_dicts}

    related_concept_dict = response.json()["concepts"][1]
    response = client.get(f"/concept?concept_iri={member_dicts[0]['iri']}&lang=sk")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        **member_dicts[0],
        "concept_schemes": [scheme_iris[0]],
        "relations": [
            {
                "source_concept_iri": member_dicts[0]["iri"],
                "target_concept_iri": related_concept_dict["iri"],
                "type": "broader",
            }
        ],
    }

    collection_iri = "https://example.org/collection1"
    response = client.get(f"/collection?collection_iri={collection_iri}&lang=sk")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "iri": collection_iri,
        "notation": "Collection1Notation",
        "prefLabel": "Collection1PrefLabel",
        "members": [
            member_dicts[0],
            member_dicts[3],
        ],
    }
