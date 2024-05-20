"""Tests for dds_glossary.services module."""

from http import HTTPStatus
from pathlib import Path

from fastapi import HTTPException
from pytest import MonkeyPatch
from pytest import raises as pytest_raises

from dds_glossary.model import Dataset, FailedDataset
from dds_glossary.schema import FullConeptResponse, RelationResponse
from dds_glossary.services import GlossaryController

from ..common import add_collections, add_concept_schemes, add_concepts, add_relations


def _init_datasets(_monkeypatch: MonkeyPatch) -> None:
    _monkeypatch.setattr("dds_glossary.database.save_dataset", lambda *_, **__: None)
    _monkeypatch.setattr(
        GlossaryController, "parse_dataset", lambda *_, **__: ([], [], [], [])
    )


def test_glossary_controller_parse_dataset(
    controller: GlossaryController,
    file_rdf: Path,
) -> None:
    """Test the GlossaryController parse_dataset method."""
    concept_scheme_iri = "http://data.europa.eu/xsp/cn2024/cn2024"
    concept1_iri = "http://data.europa.eu/xsp/cn2024/020321000080"
    concept2_iri = "http://data.europa.eu/xsp/cn2024/020321000010"
    collection1_iri = "https://example.org/collection1"
    collection2_iri = "https://example.org/collection2"
    concept_schemes, concepts, collections, semantic_relations = (
        controller.parse_dataset(dataset_path=file_rdf)
    )

    assert len(concept_schemes) == 1
    assert len(concepts) == 2
    assert len(collections) == 2
    assert len(semantic_relations) == 1
    assert concept_schemes[0].iri == concept_scheme_iri
    assert concepts[0].iri == concept1_iri
    assert concepts[1].iri == concept2_iri
    assert collections[0].iri == collection1_iri
    assert collections[1].iri == collection2_iri
    assert semantic_relations[0].source_concept_iri == concept1_iri
    assert semantic_relations[0].target_concept_iri == concept2_iri


def test_init_dataset_with_failed_datasets(
    controller: GlossaryController,
    monkeypatch: MonkeyPatch,
    file_rdf: Path,
) -> None:
    """Test the GlossaryController init_datasets method with an exception."""
    _init_datasets(monkeypatch)
    GlossaryController.datasets = [
        Dataset(name="sample.rdf", url=str(file_rdf)),
        Dataset(name="test.rdf", url="test.rdf"),
    ]

    response = controller.init_datasets()
    files = list(controller.data_dir.iterdir())

    e_schemes, e_concepts, e_collections, e_relations = controller.parse_dataset(
        file_rdf
    )
    a_schemes, a_concepts, a_collections, a_relations = controller.parse_dataset(
        files[0]
    )

    assert len(files) == 1
    assert e_schemes == a_schemes
    assert e_concepts == a_concepts
    assert e_collections == a_collections
    assert e_relations == a_relations
    assert response.failed_datasets == [
        FailedDataset(
            name="test.rdf",
            url="test.rdf",
            error="[Errno 2] No such file or directory: 'test.rdf'",
        )
    ]
    assert response.saved_datasets == [Dataset(name="sample.rdf", url=str(file_rdf))]


def test_get_concept_schemes(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concept_schemes method."""
    concept_scheme_dicts = add_concept_schemes(controller.engine, 1)

    concept_schemes = controller.get_concept_schemes()
    assert len(concept_schemes) == len(concept_scheme_dicts)
    assert concept_schemes[0].model_dump() == concept_scheme_dicts[0]


def test_get_concepts(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concepts method."""
    concept_scheme_dicts = add_concept_schemes(controller.engine, 1)
    concept_dicts = add_concepts(controller.engine, [concept_scheme_dicts[0]["iri"]])

    concepts = controller.get_concepts(concept_scheme_dicts[0]["iri"])
    assert len(concepts) == len(concept_dicts)
    assert concepts == concept_dicts


def test_get_concepts_not_found(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concepts method with a concept scheme
    not found."""
    concept_scheme_iri = "http://example.org/concept_scheme"
    with pytest_raises(HTTPException) as exc_info:
        controller.get_concepts(concept_scheme_iri)
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == f"Concept scheme {concept_scheme_iri} not found."


def test_get_collection(controller: GlossaryController) -> None:
    """Test the GlossaryController get_collection method."""
    concept_scheme_dicts = add_concept_schemes(controller.engine, 1)
    concept_dicts = add_concepts(
        controller.engine, [concept_scheme_dicts[0]["iri"]] * 3
    )
    member_iri_lists = [
        [
            concept_dicts[0]["iri"],
            concept_dicts[1]["iri"],
        ],
        ["collection_iri0"],
    ]
    collection_dicts = add_collections(controller.engine, member_iri_lists)
    collection_dicts[0]["members"] = [
        {
            "iri": concept_dicts[i]["iri"],
            "notation": concept_dicts[i]["notation"],
            "prefLabel": concept_dicts[i]["prefLabel"],
        }
        for i in range(2)
    ]

    collection = controller.get_collection(collection_dicts[0]["iri"])
    assert collection.model_dump() == collection_dicts[0]


def test_get_collection_not_found(controller: GlossaryController) -> None:
    """Test the GlossaryController get_collection method with a collection not found."""
    collection_iri = "http://example.org/collection"
    with pytest_raises(HTTPException) as exc_info:
        controller.get_collection(collection_iri)
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == f"Collection {collection_iri} not found."


def test_get_concept(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concept method."""
    concept_scheme_dicts = add_concept_schemes(controller.engine, 2)
    concept_dicts = add_concepts(
        controller.engine,
        [concept_scheme_dict["iri"] for concept_scheme_dict in concept_scheme_dicts],
    )
    relation_dicts = add_relations(
        controller.engine, [(concept_dicts[0]["iri"], concept_dicts[1]["iri"])]
    )
    expected_concept = FullConeptResponse(
        **concept_dicts[0],
        concept_schemes=[concept_scheme_dicts[0]["iri"]],
        relations=[RelationResponse(**relation_dicts[0])],
    )

    concept = controller.get_concept(concept_dicts[0]["iri"])
    assert concept == expected_concept


def test_get_concept_not_found(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concept method with a concept not found."""
    concept_iri = "http://example.org/concept"
    with pytest_raises(HTTPException) as exc_info:
        controller.get_concept(concept_iri)
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == f"Concept {concept_iri} not found."


def test_search_database(controller: GlossaryController) -> None:
    """Test the GlossaryController search_database method."""
    concept_scheme_dicts = add_concept_schemes(controller.engine, 1)
    scheme_iri = concept_scheme_dicts[0]["iri"]
    concept_dicts = add_concepts(controller.engine, [scheme_iri])

    search_results = controller.search_database(concept_dicts[0]["prefLabel"])
    assert len(search_results) == 1
    assert search_results[0].model_dump() == concept_dicts[0]
