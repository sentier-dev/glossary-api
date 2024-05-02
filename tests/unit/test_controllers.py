"""Tests for dds_glossary.controllers module."""

from http import HTTPStatus
from json import loads

from dds_glossary.controllers import APIController


def test_api_controller_get_concept_schemes_empty(engine) -> None:
    """Test the APIController get_concept_schemes method."""
    controller = APIController(engine=engine)
    response = controller.get_concept_schemes()
    assert loads(response.body) == {"concept_schemes": []}
    assert response.status_code == HTTPStatus.OK
    assert response.media_type == "application/json"


def test_api_controller_get_concepts_for_scheme_not_found(engine) -> None:
    """Test the APIController get_concepts_for_scheme method."""
    scheme_name = "not_found"
    controller = APIController(engine=engine)
    response = controller.get_concepts_for_scheme(scheme_name)
    assert loads(response.body) == {"error": f"Concept scheme not found: {scheme_name}"}
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.media_type == "application/json"


def test_api_controller_get_relationships_for_concept_not_found(engine) -> None:
    """Test the APIController get_relationships_for_concept method."""
    concept_name = "not_found"
    controller = APIController(engine=engine)
    response = controller.get_relationships_for_concept(concept_name)
    assert loads(response.body) == {"error": f"Concept not found: {concept_name}"}
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.media_type == "application/json"
