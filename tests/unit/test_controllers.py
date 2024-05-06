"""Tests for dds_glossary.controllers module."""

from http import HTTPStatus
from json import loads

from sqlalchemy.engine import Engine

from dds_glossary.controllers import GlossaryController

from .. import FILE_RDF


def test_glossary_controller_parse_dataset(engine: Engine) -> None:
    """Test the GlossaryController parse_dataset method."""
    concept_scheme_iri = "http://data.europa.eu/xsp/cn2024/cn2024"
    concept1_iri = "http://data.europa.eu/xsp/cn2024/020321000080"
    concept2_iri = "http://data.europa.eu/xsp/cn2024/020321000010"
    dataset_path = FILE_RDF
    controller = GlossaryController(engine=engine)
    concept_schemes, concepts, semantic_relations = controller.parse_dataset(
        dataset_path=dataset_path
    )

    assert len(concept_schemes) == 1
    assert len(concepts) == 2
    assert len(semantic_relations) == 1
    assert concept_schemes[0].iri == concept_scheme_iri
    assert concepts[0].iri == concept1_iri
    assert concepts[1].iri == concept2_iri
    assert semantic_relations[0].source_concept_iri == concept1_iri
    assert semantic_relations[0].target_concept_iri == concept2_iri


def test_glossary_controller_get_concept_schemes_empty(engine: Engine) -> None:
    """Test the APIController get_concept_schemes method."""
    controller = GlossaryController(engine=engine)
    response = controller.get_concept_schemes()
    assert loads(response.body) == {"concept_schemes": []}
    assert response.status_code == HTTPStatus.OK
    assert response.media_type == "application/json"
