"""Tests for dds_glossary.main module."""

from http import HTTPStatus

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from dds_glossary import __version__
from dds_glossary.model import Dataset, FailedDataset
from dds_glossary.schema import InitDatasetsResponse


def test_version(client: TestClient) -> None:
    """Test the /version endpoint."""
    response = client.get("/version")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"version": __version__}


def test_init_datasets_missing_key(client: TestClient) -> None:
    """Test the /init_datasets endpoint with a missing API key."""
    response = client.post("/init_datasets")
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"detail": "Not authenticated"}


def test_init_datasets_invalid_key(client: TestClient) -> None:
    """Test the /init_datasets endpoint with an invalid API key."""
    response = client.post("/init_datasets", headers={"X-API-Key": "invalid"})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"detail": "Invalid API Key"}


def test_init_datasets_valid_key(client: TestClient, monkeypatch: MonkeyPatch) -> None:
    """Test the /init_datasets endpoint."""
    saved_datasets = [Dataset(name="saved.rdf", url="http://example.com/saved.rdf")]
    failed_datasets = [
        FailedDataset(
            name="failed.rdf",
            url="http://example.com/failed.rdf",
            error="error",
        )
    ]
    monkeypatch.setattr(
        "dds_glossary.services.GlossaryController.init_datasets",
        lambda *_, **__: InitDatasetsResponse(
            saved_datasets=saved_datasets,
            failed_datasets=failed_datasets,
        ),
    )
    api_key = "valid"
    monkeypatch.setenv("API_KEY", api_key)

    response = client.post("/init_datasets", headers={"X-API-Key": api_key})
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert (
        response.json()
        == InitDatasetsResponse(
            saved_datasets=saved_datasets, failed_datasets=failed_datasets
        ).model_dump()
    )


def test_get_concept_schemes_empty(client: TestClient) -> None:
    """Test the /schemes endpoint with an empty database."""
    response = client.get("/schemes")
    assert response.json() == []
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"


def test_get_concepts_not_found(client: TestClient) -> None:
    """Test the /concepts endpoint."""
    concept_scheme_iri = "iri"
    response = client.get(f"/concepts?concept_scheme_iri={concept_scheme_iri}")
    assert response.json() == {
        "detail": f"Concept scheme {concept_scheme_iri} not found."
    }
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.headers["content-type"] == "application/json"


def test_get_collection_not_found(client: TestClient) -> None:
    """Test the /collection endpoint."""
    collection_iri = "iri"
    response = client.get(f"/collection?collection_iri={collection_iri}")
    assert response.json() == {"detail": f"Collection {collection_iri} not found."}
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.headers["content-type"] == "application/json"


def test_get_concept(client: TestClient) -> None:
    """Test the /concept endpoint."""
    concept_iri = "iri"
    response = client.get(f"/concept?concept_iri={concept_iri}")
    assert response.json() == {"detail": f"Concept {concept_iri} not found."}
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.headers["content-type"] == "application/json"
