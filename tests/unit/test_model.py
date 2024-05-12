"""Tests for dds_glossary.model module."""

from dds_glossary.model import (
    Base,
    Concept,
    ConceptCollection,
    ConceptScheme,
    InCollection,
    InScheme,
    SemanticRelation,
    SemanticRelationType,
)


def test_base_eq_true(concept_scheme: ConceptScheme) -> None:
    """It should return True if two Base instances are equal."""
    assert concept_scheme == ConceptScheme(
        iri="http://data.europa.eu/xsp/cn2024/cn2024",
        notation="CN 2024",
        scopeNote="http://publications.europa.eu/resource/oj/JOC_2019_119_R_0001",
        prefLabels={
            "en": "Combined Nomenclature, 2024 (CN 2024)",
            "sk": "Kombinovaná Nomenklatúra, 2024 (KN 2024)",
            "et": "Kombineeritud Nomenklatuur, 2024 (KN 2024)",
            "mt": "Nomenklatura Magħquda, 2024 (NM 2024)",
        },
    )


def test_base_eq_false(concept_scheme: ConceptScheme) -> None:
    """It should return False if two Base instances are not equal."""
    assert concept_scheme != ConceptScheme(
        iri="http://data.europa.eu/xsp/cn2024/cn2024",
        notation="CN 2023",
        scopeNote="http://publications.europa.eu/resource/oj/JOC_2019_119_R_0001",
        prefLabels={
            "en": "Combined Nomenclature, 2024 (CN 2024)",
            "sk": "Kombinovaná Nomenklatúra, 2024 (KN 2024)",
            "et": "Kombineeritud Nomenklatuur, 2024 (KN 2024)",
            "mt": "Nomenklatura Magħquda, 2024 (NM 2024)",
        },
    )


def test_base_get_in_language_language_exists(concept_scheme: ConceptScheme) -> None:
    """It should return the preferred label in the specified language."""
    assert (
        Base.get_in_language(concept_scheme.prefLabels, "sk")
        == "Kombinovaná Nomenklatúra, 2024 (KN 2024)"
    )


def test_base_get_in_language_language_does_not_exist(
    concept_scheme: ConceptScheme,
) -> None:
    """It should return the preferred label in English if the specified language does
    not exist."""
    assert (
        Base.get_in_language(concept_scheme.prefLabels, "fr")
        == "Combined Nomenclature, 2024 (CN 2024)"
    )


def test_base_get_in_language_no_language_specified(
    concept_scheme: ConceptScheme,
) -> None:
    """It should return the preferred label in English if no language is specified."""
    assert (
        Base.get_in_language(concept_scheme.prefLabels)
        == "Combined Nomenclature, 2024 (CN 2024)"
    )


def test_base_get_in_language_no_language_specified_no_english(
    concept_scheme: ConceptScheme,
) -> None:
    """It should return an empty string if no language is specified and English does
    not exist."""
    concept_scheme.prefLabels = {}
    assert Base.get_in_language(concept_scheme.prefLabels) == ""


def test_concept_scheme_from_xml_element(concept_scheme: ConceptScheme) -> None:
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


def test_concept_scheme_to_dict(concept_scheme: ConceptScheme) -> None:
    """It should return a dictionary representation of the ConceptScheme instance."""
    assert concept_scheme.to_dict("sk") == {
        "iri": "http://data.europa.eu/xsp/cn2024/cn2024",
        "notation": "CN 2024",
        "scopeNote": "http://publications.europa.eu/resource/oj/JOC_2019_119_R_0001",
        "prefLabel": "Kombinovaná Nomenklatúra, 2024 (KN 2024)",
    }


def test_concept_collection_from_xml_element(concept_collection: ConceptCollection) -> None:
    """It should return a ConceptCollection instance from an XML element."""
    assert concept_collection.iri == "https://unstats.un.org/classifications/CPC/v2.1/ag/expansion_only"
    assert concept_collection.notation == "expansion_only"
    assert concept_collection.prefLabels == {
        "en": "CPC 2.1 Expanded for Agriculture and Rural Statistics - Expansion terms ONLY"
    }


def test_concept_collection_to_dict(concept_collection: ConceptCollection) -> None:
    """It should return a dictionary representation of the ConceptCollection instance."""
    assert concept_collection.to_dict("en") == {
        "iri": "https://unstats.un.org/classifications/CPC/v2.1/ag/expansion_only",
        "notation": "expansion_only",
        "prefLabel": "CPC 2.1 Expanded for Agriculture and Rural Statistics - Expansion terms ONLY",
    }


def test_concept_from_xml_element(concept: Concept) -> None:
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
        "en": "-- Carcases and half-carcases",
        "sk": "-- Trupy a polovičky trupov",
        "et": "-- rümbad ja poolrümbad",
        "mt": "-- Karkassi u nofs karkassi",
    }
    assert concept.scopeNotes == {
        "en": "Frozen carcases and half-carcases of swine",
        "fr": "Carcasses ou demi-carcasses, de porcins, congelées",
        "de": "Tierkörper oder halbe Tierkörper, von Schweinen, gefroren",
        "es": "Canales o medias canales de porcinos, congeladas",
    }


def test_concept_to_dict(concept: Concept) -> None:
    """It should return a dictionary representation of the Concept instance."""
    assert concept.to_dict("sk") == {
        "iri": "http://data.europa.eu/xsp/cn2024/020321000080",
        "identifier": "020321000080",
        "notation": "0203 21",
        "prefLabel": "0203 21 -- Trupy a polovičky trupov",
        "altLabel": "-- Trupy a polovičky trupov",
        "scopeNote": "Frozen carcases and half-carcases of swine",
    }


def test_in_scheme_from_xml_element(in_scheme: InScheme) -> None:
    """It should return an InScheme instance from an XML element."""
    assert in_scheme.member_iri == "http://data.europa.eu/xsp/cn2024/020321000080"
    assert in_scheme.scheme_iri == "http://data.europa.eu/xsp/cn2024/cn2024"


def test_in_scheme_to_dict(in_scheme: InScheme) -> None:
    """It should return a dictionary representation of the InScheme instance."""
    assert in_scheme.to_dict() == {
        "member_iri": "http://data.europa.eu/xsp/cn2024/020321000080",
        "scheme_iri": "http://data.europa.eu/xsp/cn2024/cn2024",
    }


def test_in_collection_from_xml_element(in_collection: InCollection) -> None:
    """It should return an InCollection instance from an XML element."""
    assert in_collection.member_iri == "http://data.europa.eu/xsp/cn2024/020321000010"
    assert in_collection.collection_iri == "https://unstats.un.org/classifications/CPC/v2.1/ag/expansion_only"


def test_in_collection_to_dict(in_collection: InCollection) -> None:
    """It should return a dictionary representation of the InCollection instance."""
    assert in_collection.to_dict() == {
        "member_iri": "http://data.europa.eu/xsp/cn2024/020321000010",
        "collection_iri": "https://unstats.un.org/classifications/CPC/v2.1/ag/expansion_only",
    }


def test_semantic_relation_from_xml_element(
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


def test_semantic_relation_to_dict(semantic_relation: SemanticRelation) -> None:
    """It should return a dictionary representation of the SemanticRelation instance."""
    assert semantic_relation.to_dict() == {
        "source_concept_iri": "http://data.europa.eu/xsp/cn2024/020321000080",
        "target_concept_iri": "http://data.europa.eu/xsp/cn2024/020321000010",
        "type": "broader",
    }
