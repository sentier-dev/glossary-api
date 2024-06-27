"""Tests for dds_glossary.xml module."""

from pathlib import Path

from dds_glossary.enums import SemanticRelationType
from dds_glossary.model import (
    Collection,
    Concept,
    ConceptScheme,
    InCollection,
    InScheme,
    SemanticRelation,
)
from dds_glossary.xml import parse_dataset


def test_concept_scheme_from_xml(concept_scheme: ConceptScheme) -> None:
    """It should return a ConceptScheme instance from an XML element."""
    assert concept_scheme.iri == "http://data.europa.eu/xsp/cn2024/cn2024"
    assert concept_scheme.notation == "CN 2024"
    assert (
        concept_scheme.scopeNote
        == "http://publications.europa.eu/resource/oj/JOC_2019_119_R_0001"
    )
    assert concept_scheme.prefLabels == {
        "en": "Combined Nomenclature, 2024 (CN 2024)",
        "sk": "Kombinovaná Nomenklatúra, 2024 (KN 2024)",
        "et": "Kombineeritud Nomenklatuur, 2024 (KN 2024)",
        "mt": "Nomenklatura Magħquda, 2024 (NM 2024)",
    }


def test_collection_from_xml(collection: Collection) -> None:
    """It should return a Collection instance from an XML element."""
    assert collection.iri == "https://example.org/collection1"
    assert collection.notation == "Collection1Notation"
    assert collection.prefLabels == {
        "en": "Collection1PrefLabel",
    }


def test_concept_from_xml(concept: Concept) -> None:
    """It should return a Concept instance from an XML element."""
    assert concept.iri == "http://data.europa.eu/xsp/cn2024/020321000080"
    assert concept.identifier == "020321000080"
    assert concept.notation == "0203 21"
    assert concept.prefLabels == {
        "en": "0203 21 -- Carcases and half-carcases",
        "sk": "0203 21 -- Trupy a polovičky trupov",
        "et": "0203 21 -- rümbad ja poolrümbad",
        "mt": "0203 21 -- Karkassi u nofs karkassi",
    }
    assert concept.altLabels == {
        "en": [
            "-- Carcases and half-carcases",
            "0203 21 -- Carcases and half-carcases",
        ],
        "sk": ["-- Trupy a polovičky trupov"],
        "et": ["-- rümbad ja poolrümbad"],
        "mt": ["-- Karkassi u nofs karkassi"],
    }
    assert concept.scopeNotes == {
        "en": "Frozen carcases and half-carcases of swine",
        "fr": "Carcasses ou demi-carcasses, de porcins, congelées",
        "de": "Tierkörper oder halbe Tierkörper, von Schweinen, gefroren",
        "es": "Canales o medias canales de porcinos, congeladas",
    }


def test_semantic_relations_from_xml(
    semantic_relation: SemanticRelation,
) -> None:
    """It should return a SemanticRelation instance from an XML element."""
    assert (
        semantic_relation.source_concept_iri
        == "http://data.europa.eu/xsp/cn2024/020321000080"
    )
    assert (
        semantic_relation.target_concept_iri
        == "http://data.europa.eu/xsp/cn2024/020321000010"
    )
    assert semantic_relation.type == SemanticRelationType.BROADER


def test_in_scheme_from_xml(in_scheme: InScheme) -> None:
    """It should return an InScheme instance from an XML element."""
    assert in_scheme.member_iri == "http://data.europa.eu/xsp/cn2024/020321000080"
    assert in_scheme.scheme_iri == "http://data.europa.eu/xsp/cn2024/cn2024"


def test_in_collection_from_xml(in_collection: InCollection) -> None:
    """It should return an InCollection instance from an XML element."""
    assert in_collection.collection_iri == "https://example.org/collection1"
    assert in_collection.member_iri == "http://data.europa.eu/xsp/cn2024/020321000080"


def test_glossary_controller_parse_dataset(file_rdf: Path) -> None:
    """Test the GlossaryController parse_dataset method."""
    concept_scheme_iri = "http://data.europa.eu/xsp/cn2024/cn2024"
    concept1_iri = "http://data.europa.eu/xsp/cn2024/020321000080"
    concept2_iri = "http://data.europa.eu/xsp/cn2024/020321000010"
    collection1_iri = "https://example.org/collection1"
    collection2_iri = "https://example.org/collection2"
    parsed_dataset = parse_dataset(dataset_path=file_rdf)

    assert len(parsed_dataset.concept_schemes) == 1
    assert len(parsed_dataset.concepts) == 2
    assert len(parsed_dataset.collections) == 2
    assert len(parsed_dataset.semantic_relations) == 1
    assert len(parsed_dataset.in_schemes) == 4
    assert len(parsed_dataset.in_collections) == 2
    assert parsed_dataset.concept_schemes[0].iri == concept_scheme_iri
    assert parsed_dataset.concepts[0].iri == concept1_iri
    assert parsed_dataset.concepts[1].iri == concept2_iri
    assert parsed_dataset.collections[0].iri == collection1_iri
    assert parsed_dataset.collections[1].iri == collection2_iri
    assert parsed_dataset.semantic_relations[0].source_concept_iri == concept1_iri
    assert parsed_dataset.semantic_relations[0].target_concept_iri == concept2_iri
    assert parsed_dataset.in_schemes[0].member_iri == collection1_iri
    assert parsed_dataset.in_schemes[0].scheme_iri == concept_scheme_iri
    assert parsed_dataset.in_schemes[2].member_iri == concept1_iri
    assert parsed_dataset.in_schemes[2].scheme_iri == concept_scheme_iri
    assert parsed_dataset.in_collections[0].collection_iri == collection1_iri
    assert parsed_dataset.in_collections[0].member_iri == concept1_iri
    assert parsed_dataset.in_collections[1].collection_iri == collection1_iri
    assert parsed_dataset.in_collections[1].member_iri == collection2_iri
