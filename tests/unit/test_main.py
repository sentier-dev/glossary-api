"""Tests for dds_glossary.main module."""

from http import HTTPStatus

from dds_glossary.controllers import APIController


def test_main_get_concept_schemes_empty(client) -> None:
    """Test the /schemes endpoint."""
    response = client.get("/schemes")
    assert response.json() == {"concept_schemes": []}
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"


def test_main_get_concepts_for_scheme_no_concept_scheme_found(client) -> None:
    """Test the /schemes/{scheme_name} endpoint."""
    concept_scheme = "test-scheme"
    response = client.get(f"/schemes/{concept_scheme}")
    assert response.json() == {"error": f"Concept scheme not found: {concept_scheme}"}
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.headers["content-type"] == "application/json"


def test_main_get_concepts_for_scheme(monkeypatch, client) -> None:
    """Test the /schemes/{scheme_name} endpoint."""
    expected_json: dict[str, list] = {"concepts": []}
    monkeypatch.setattr(
        APIController,
        "get_concepts_for_scheme",
        lambda *_, **__: expected_json,
    )

    concept_scheme = "test-scheme"
    response = client.get(f"/schemes/{concept_scheme}")
    assert response.json() == expected_json
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"


def test_main_get_relationships_for_concept_no_concept_found(client) -> None:
    """Test the /concepts/{concept_name} endpoint."""
    concept = "test-concept"
    response = client.get(f"/concepts/{concept}")
    assert response.json() == {"error": f"Concept not found: {concept}"}
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.headers["content-type"] == "application/json"


def test_main_get_relationships_for_concept(monkeypatch, client) -> None:
    """Test the /concepts/{concept_name} endpoint."""
    expected_json: dict[str, list] = {"relationships": []}
    monkeypatch.setattr(
        APIController,
        "get_relationships_for_concept",
        lambda *_, **__: expected_json,
    )

    concept = "test-concept"
    response = client.get(f"/concepts/{concept}")
    assert response.json() == expected_json
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
