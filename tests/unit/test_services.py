"""Tests for dds_glossary.services module."""

from http import HTTPStatus
from pathlib import Path

from pytest import raises as pytest_raises

from dds_glossary.exceptions import (
    CollectionNotFoundException,
    ConceptNotFoundException,
    ConceptSchemeNotFoundException,
)
from dds_glossary.model import Dataset, FailedDataset
from dds_glossary.schema import (
    CollectionResponse,
    ConceptResponse,
    EntityResponse,
    FullConceptResponse,
    FullConceptSchemeResponse,
    RelationResponse,
)
from dds_glossary.services import GlossaryController
from dds_glossary.xml import parse_dataset

from ..common import add_collections, add_concept_schemes, add_concepts, add_relations


def test_init_dataset_with_failed_datasets(
    controller: GlossaryController,
    file_rdf: Path,
) -> None:
    """Test the GlossaryController init_datasets method with an exception."""
    GlossaryController.datasets = [
        Dataset(name="sample.rdf", url=str(file_rdf)),
        Dataset(name="test.rdf", url="test.rdf"),
    ]

    response = controller.init_datasets()
    files = list(controller.data_dir.iterdir())

    exp_parsed_dataset = parse_dataset(file_rdf)
    act_parsed_dataset = parse_dataset(files[0])

    assert len(files) == 1
    assert exp_parsed_dataset.concept_schemes == act_parsed_dataset.concept_schemes
    assert exp_parsed_dataset.concepts == act_parsed_dataset.concepts
    assert exp_parsed_dataset.collections == act_parsed_dataset.collections
    assert (
        exp_parsed_dataset.semantic_relations == act_parsed_dataset.semantic_relations
    )
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


def test_get_concept_scheme(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concept_scheme method."""
    concept_scheme_dicts = add_concept_schemes(controller.engine, 1)
    concept_dicts = add_concepts(controller.engine, [concept_scheme_dicts[0]["iri"]])
    collections_dicts = add_collections(
        controller.engine,
        [concept_scheme_dicts[0]["iri"]] * 2,
        [[concept_dicts[0]["iri"]], ["collection_iri0"]],
    )
    expected_concept_scheme = FullConceptSchemeResponse(
        **concept_scheme_dicts[0],
        concepts=[ConceptResponse(**concept_dict) for concept_dict in concept_dicts],
        collections=[
            EntityResponse(**collections_dict) for collections_dict in collections_dicts
        ],
    )

    concept_scheme = controller.get_concept_scheme(concept_scheme_dicts[0]["iri"])
    assert concept_scheme == expected_concept_scheme


def test_get_concept_scheme_not_found(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concept_scheme method with a concept scheme
    not found."""
    concept_scheme_iri = "http://example.org/concept_scheme"
    with pytest_raises(ConceptSchemeNotFoundException) as exc_info:
        controller.get_concept_scheme(concept_scheme_iri)
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == f"Concept scheme {concept_scheme_iri} not found."


def test_get_collections(controller: GlossaryController) -> None:
    """Test the GlossaryController get_collections method."""
    concept_scheme_dicts = add_concept_schemes(controller.engine, 1)
    collection_dicts = add_collections(
        controller.engine,
        [concept_scheme_dicts[0]["iri"]] * 2,
        [[], []],
    )
    expected_collections = [
        EntityResponse(**collection_dict) for collection_dict in collection_dicts
    ]

    collections = controller.get_collections(concept_scheme_dicts[0]["iri"])
    assert collections == expected_collections


def test_get_collection(controller: GlossaryController) -> None:
    """Test the GlossaryController get_collection method."""
    concept_scheme_dicts = add_concept_schemes(controller.engine, 1)
    concept_dicts = add_concepts(
        controller.engine, [concept_scheme_dicts[0]["iri"]] * 3
    )
    collection_dicts = add_collections(
        controller.engine,
        [concept_scheme_dicts[0]["iri"]],
        [[concept_dicts[0]["iri"], concept_dicts[1]["iri"]]],
    )
    expected_collection = CollectionResponse(
        **collection_dicts[0],
        concepts=[
            ConceptResponse(**concept_dict) for concept_dict in concept_dicts[:2]
        ],
        collections=[],
    )

    collection = controller.get_collection(collection_dicts[0]["iri"])
    assert collection == expected_collection


def test_get_collection_not_found(controller: GlossaryController) -> None:
    """Test the GlossaryController get_collection method with a collection not found."""
    collection_iri = "http://example.org/collection"
    with pytest_raises(CollectionNotFoundException) as exc_info:
        controller.get_collection(collection_iri)
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == f"Collection {collection_iri} not found."


def test_get_concepts(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concepts method."""
    concept_scheme_dicts = add_concept_schemes(controller.engine, 1)
    concept_dicts = add_concepts(
        controller.engine, [concept_scheme_dicts[0]["iri"]] * 2
    )
    expected_concepts = [
        ConceptResponse(**concept_dict) for concept_dict in concept_dicts
    ]

    concepts = controller.get_concepts(concept_scheme_dicts[0]["iri"])
    assert concepts == expected_concepts


def test_get_concepts_not_found(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concepts method with a concept scheme
    not found."""
    concept_scheme_iri = "http://example.org/concept_scheme"
    with pytest_raises(ConceptSchemeNotFoundException) as exc_info:
        controller.get_concepts(concept_scheme_iri)
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == f"Concept scheme {concept_scheme_iri} not found."


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
    expected_concept = FullConceptResponse(
        **concept_dicts[0],
        concept_schemes=[concept_scheme_dicts[0]["iri"]],
        relations=[RelationResponse(**relation_dicts[0])],
    )

    concept = controller.get_concept(concept_dicts[0]["iri"])
    assert concept == expected_concept


def test_get_concept_not_found(controller: GlossaryController) -> None:
    """Test the GlossaryController get_concept method with a concept not found."""
    concept_iri = "http://example.org/concept"
    with pytest_raises(ConceptNotFoundException) as exc_info:
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
