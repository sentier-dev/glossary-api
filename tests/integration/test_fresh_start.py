"""Integration test for a fresh start scenario."""

from http import HTTPStatus
from os import getenv as os_getenv
from pathlib import Path
from typing import Any, Mapping

from fastapi.testclient import TestClient

from dds_glossary import __version__
from dds_glossary.schema import (
    CollectionResponse,
    ConceptSchemeResponse,
    Dataset,
    EntityResponse,
    FailedDataset,
    InitDatasetsResponse,
    VersionResponse,
)
from dds_glossary.services import GlossaryController


def test_fresh_start(client: TestClient, dir_data: Path) -> None:
    """Test the /fresh_start endpoint."""
    saved_dataset = Dataset(
        name="sample.rdf",
        url=str(dir_data / "sample.rdf"),
    )
    failed_dataset = FailedDataset(
        name="failed_dataset.rdf",
        url="",
        error="[Errno 2] No such file or directory: ''",
    )
    GlossaryController.datasets = [saved_dataset, failed_dataset]

    response = client.get("/latest/version")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == VersionResponse(version=__version__).model_dump()

    api_key = os_getenv("API_KEY", "")
    headers: Mapping[str, str] = {"X-API-Key": api_key}
    response = client.post("/latest/init_datasets", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert (
        response.json()
        == InitDatasetsResponse(
            saved_datasets=[saved_dataset],
            failed_datasets=[failed_dataset],
        ).model_dump()
    )

    response = client.get("/latest/schemes?lang=sk")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == [
        ConceptSchemeResponse(
            iri="http://data.europa.eu/xsp/cn2024/cn2024",
            notation="CN 2024",
            scopeNote=("http://publications.europa.eu/resource/oj/JOC_2019_119_R_0001"),
            prefLabel="Kombinovaná Nomenklatúra, 2024 (KN 2024)",
        ).model_dump()
    ]

    scheme_iris = [scheme["iri"] for scheme in response.json()]
    member_dicts: list[dict[str, Any]] = [
        {
            "iri": "http://data.europa.eu/xsp/cn2024/020321000080",
            "identifier": "020321000080",
            "notation": "0203 21",
            "prefLabel": "0203 21 -- Trupy a polovičky trupov",
            "altLabels": ["-- Trupy a polovičky trupov"],
            "scopeNote": "Frozen carcases and half-carcases of swine",
        },
        {
            "iri": "http://data.europa.eu/xsp/cn2024/020321000010",
            "identifier": "020321000010",
            "notation": "",
            "prefLabel": "- Mrazené",
            "altLabels": ["- Frozen"],
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
    response = client.get(
        f"/latest/concepts?concept_scheme_iri={scheme_iris[0]}&lang=sk"
    )
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"concepts": member_dicts}

    related_concept_dict = response.json()["concepts"][1]
    response = client.get(
        f"/latest/concept?concept_iri={member_dicts[0]['iri']}&lang=sk"
    )
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
    response = client.get(f"/latest/collection?collection_iri={collection_iri}&lang=sk")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert (
        response.json()
        == CollectionResponse(
            iri=collection_iri,
            notation="Collection1Notation",
            prefLabel="Collection1PrefLabel",
            members=[
                EntityResponse(**member_dicts[0]),
                EntityResponse(**member_dicts[3]),
            ],
        ).model_dump()
    )
