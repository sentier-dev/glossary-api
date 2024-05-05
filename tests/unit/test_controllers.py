"""Tests for dds_glossary.controllers module."""

from http import HTTPStatus
from json import loads

from dds_glossary.controllers import GlossaryController


def test_api_controller_get_concept_schemes_empty(engine) -> None:
    """Test the APIController get_concept_schemes method."""
    controller = GlossaryController(engine=engine)
    response = controller.get_concept_schemes()
    assert loads(response.body) == {"concept_schemes": []}
    assert response.status_code == HTTPStatus.OK
    assert response.media_type == "application/json"
