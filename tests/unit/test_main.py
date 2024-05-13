"""Tests for dds_glossary.main module."""

from http import HTTPStatus

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from dds_glossary import __version__


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
    saved_datasets = [
        {"dataset": "saved.rdf", "dataset_url": "http://example.com/saved.rdf"}
    ]
    failed_datasets = [
        {"dataset": "failed.rdf", "dataset_url": "http://example.com/failed.rdf"}
    ]
    monkeypatch.setattr(
        "dds_glossary.controllers.GlossaryController.init_datasets",
        lambda *_, **__: (saved_datasets, failed_datasets),
    )
    api_key = "valid"
    monkeypatch.setenv("API_KEY", api_key)

    response = client.post("/init_datasets", headers={"X-API-Key": api_key})
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "saved_datasets": saved_datasets,
        "failed_datasets": failed_datasets,
    }


def test_get_concept_schemes_empty(client: TestClient) -> None:
    """Test the /schemes endpoint with an empty database."""
    response = client.get("/schemes")
    assert response.json() == {"concept_schemes": []}
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"


def test_get_concepts(client: TestClient) -> None:
    """Test the /concepts endpoint."""
    response = client.get("/concepts?concept_scheme_iri=iri")
    assert response.json() == {"concepts": []}
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"


def test_get_concept(client: TestClient) -> None:
    """Test the /concept endpoint."""
    concept_iri = "iri"
    response = client.get(f"/concept?concept_iri={concept_iri}")
    assert response.json() == {"detail": f"Concept {concept_iri} not found."}
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.headers["content-type"] == "application/json"
