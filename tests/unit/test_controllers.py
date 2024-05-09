"""Tests for dds_glossary.controllers module."""

from pytest import MonkeyPatch
from pytest import raises as pytest_raises
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from dds_glossary.controllers import GlossaryController
from dds_glossary.model import (
    Concept,
    ConceptScheme,
    SemanticRelation,
    SemanticRelationType,
)

from .. import FILE_RDF


def _init_datasets(_monkeypatch: MonkeyPatch) -> None:
    _monkeypatch.setattr("dds_glossary.database.save_dataset", lambda *_, **__: None)
    _monkeypatch.setattr(
        GlossaryController, "parse_dataset", lambda *_, **__: ([], [], [])
    )


def test_glossary_controller_parse_dataset(controller: GlossaryController) -> None:
    """Test the GlossaryController parse_dataset method."""
    concept_scheme_iri = "http://data.europa.eu/xsp/cn2024/cn2024"
    concept1_iri = "http://data.europa.eu/xsp/cn2024/020321000080"
    concept2_iri = "http://data.europa.eu/xsp/cn2024/020321000010"
    dataset_path = FILE_RDF
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


def test_init_dataset_with_failed_datasets(
    controller: GlossaryController, monkeypatch: MonkeyPatch
) -> None:
    """Test the GlossaryController init_datasets method with an exception."""
    _init_datasets(monkeypatch)
    GlossaryController.datasets = {
        "sample.rdf": str(FILE_RDF),
        "test.rdf": "test.rdf",
    }

    saved_datasets, failed_datasets = controller.init_datasets()
    files = list(controller.data_dir.iterdir())

    assert len(files) == 1
    assert files[0].read_bytes() == FILE_RDF.read_bytes()
    assert saved_datasets == [{"dataset": "sample.rdf", "dataset_url": str(FILE_RDF)}]
    assert failed_datasets == [
        {
            "dataset": "test.rdf",
            "dataset_url": "test.rdf",
            "error": "[Errno 2] No such file or directory: 'test.rdf'",
        }
    ]


def test_get_concept_schemes(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concept_schemes method."""
    iri = "http://example.org/concept_scheme"
    with Session(controller.engine) as session:
        session.add(
            ConceptScheme(
                iri=iri,
                notation="notation",
                scopeNote="scopeNote",
                prefLabels={"en": "label"},
            )
        )
        session.commit()

    concept_schemes = controller.get_concept_schemes()
    assert len(concept_schemes) == 1
    assert concept_schemes[0]["iri"] == iri


def test_get_concepts(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concepts method."""
    concept_scheme_iri = "http://example.org/concept_scheme"
    concept_iri = "http://example.org/concept"
    with Session(controller.engine) as session:
        session.add(
            ConceptScheme(
                iri=concept_scheme_iri,
                notation="notation",
                scopeNote="scopeNote",
                prefLabels={"en": "label"},
            )
        )
        session.add(
            Concept(
                iri=concept_iri,
                identifier="identifier",
                notation="notation",
                prefLabels={"en": "label"},
                altLabels={"en": "label"},
                scopeNotes={"en": "scopeNote"},
                scheme_iri=concept_scheme_iri,
            )
        )
        session.commit()

    concepts = controller.get_concepts(concept_scheme_iri)
    assert len(concepts) == 1
    assert concepts[0]["iri"] == concept_iri
    assert concepts[0]["scheme_iri"] == concept_scheme_iri


def test_get_concept(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concept method."""
    concept_scheme_iri = "http://example.org/concept_scheme"
    source_concept_iri = "http://example.org/concept1"
    target_concept_iri = "http://example.org/concept2"
    with Session(controller.engine) as session:
        session.add(
            ConceptScheme(
                iri=concept_scheme_iri,
                notation="notation",
                scopeNote="scopeNote",
                prefLabels={"en": "label"},
            )
        )
        session.add(
            Concept(
                iri=source_concept_iri,
                identifier="identifier",
                notation="notation",
                prefLabels={"en": "label"},
                altLabels={"en": "label"},
                scopeNotes={"en": "scopeNote"},
                scheme_iri=concept_scheme_iri,
            )
        )
        session.add(
            Concept(
                iri=target_concept_iri,
                identifier="identifier",
                notation="notation",
                prefLabels={"en": "label"},
                altLabels={"en": "label"},
                scopeNotes={"en": "scopeNote"},
                scheme_iri=concept_scheme_iri,
            )
        )
        session.add(
            SemanticRelation(
                source_concept_iri=source_concept_iri,
                target_concept_iri=target_concept_iri,
                type=SemanticRelationType.RELATED,
            )
        )
        session.commit()

    concept = controller.get_concept(source_concept_iri)
    assert concept["iri"] == source_concept_iri
    assert concept["scheme_iri"] == concept_scheme_iri
    assert len(concept["relations"]) == 1
    assert concept["relations"][0]["source_concept_iri"] == source_concept_iri
    assert concept["relations"][0]["target_concept_iri"] == target_concept_iri
    assert concept["relations"][0]["type"] == "related"


def test_get_concept_not_found(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concept method with a concept not found."""
    concept_iri = "http://example.org/concept"
    with pytest_raises(NoResultFound):
        controller.get_concept(concept_iri)
