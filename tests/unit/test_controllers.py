"""Tests for dds_glossary.controllers module."""

from dds_glossary.controllers import APIController


def test_api_controller_get_concept_schemes_empty(database_url) -> None:
    """Test the APIController get_concept_schemes method."""
    controller = APIController(database_url=database_url)
    assert controller.get_concept_schemes() == {"concept_schemes": []}


def test_api_controller_get_concepts_for_scheme_not_found(database_url) -> None:
    """Test the APIController get_concepts_for_scheme method."""
    controller = APIController(database_url=database_url)
    assert controller.get_concepts_for_scheme("not_found") == {
        "error": "Concept scheme not found: not_found"
    }


def test_api_controller_get_relationships_for_concept_not_found(database_url) -> None:
    """Test the APIController get_relationships_for_concept method."""
    controller = APIController(database_url=database_url)
    assert controller.get_relationships_for_concept("not_found") == {
        "error": "Concept not found: not_found"
    }
