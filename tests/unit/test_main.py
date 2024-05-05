"""Tests for dds_glossary.main module."""

from http import HTTPStatus


def test_get_concept_schemes_empty(client) -> None:
    """Test the /schemes endpoint with an empty database."""
    response = client.get("/schemes")
    assert response.json() == {"concept_schemes": []}
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "application/json"
