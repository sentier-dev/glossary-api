"""Tests for dds_glossary.model module."""

from dds_glossary.model import Base, Concept, ConceptScheme, SemanticRelation


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


def test_base_get_in_language_list_language_exists(concept: Concept) -> None:
    """It should return the preferred label in the specified language."""
    assert Base.get_in_language(concept.altLabels, "sk") == [
        "-- Trupy a polovičky trupov"
    ]


def test_base_get_in_language_list_language_does_not_exist(concept: Concept) -> None:
    """It should return the preferred label in English if the specified language does
    not exist."""
    assert Base.get_in_language(concept.altLabels, "fr") == [
        "-- Carcases and half-carcases",
        "0203 21 -- Carcases and half-carcases",
    ]


def test_base_get_in_language_list_no_language_specified(concept: Concept) -> None:
    """It should return the preferred label in English if no language is specified."""
    assert Base.get_in_language(concept.altLabels) == [
        "-- Carcases and half-carcases",
        "0203 21 -- Carcases and half-carcases",
    ]


def test_base_get_in_language_list_no_language_specified_no_english(
    concept: Concept,
) -> None:
    """It should return an empty list if no language is specified and English does
    not exist."""
    concept.altLabels = {}
    assert Base.get_in_language_list(concept.altLabels) == []


def test_concept_scheme_to_dict(concept_scheme: ConceptScheme) -> None:
    """It should return a dictionary representation of the ConceptScheme instance."""
    assert concept_scheme.to_dict("sk") == {
        "iri": "http://data.europa.eu/xsp/cn2024/cn2024",
        "notation": "CN 2024",
        "scopeNote": "http://publications.europa.eu/resource/oj/JOC_2019_119_R_0001",
        "prefLabel": "Kombinovaná Nomenklatúra, 2024 (KN 2024)",
    }


def test_concept_to_dict(concept: Concept) -> None:
    """It should return a dictionary representation of the Concept instance."""
    assert concept.to_dict("sk") == {
        "iri": "http://data.europa.eu/xsp/cn2024/020321000080",
        "identifier": "020321000080",
        "notation": "0203 21",
        "prefLabel": "0203 21 -- Trupy a polovičky trupov",
        "altLabels": ["-- Trupy a polovičky trupov"],
        "scopeNote": "Frozen carcases and half-carcases of swine",
    }


def test_semantic_relation_to_dict(semantic_relation: SemanticRelation) -> None:
    """It should return a dictionary representation of the SemanticRelation instance."""
    assert semantic_relation.to_dict() == {
        "source_concept_iri": "http://data.europa.eu/xsp/cn2024/020321000080",
        "target_concept_iri": "http://data.europa.eu/xsp/cn2024/020321000010",
        "type": "broader",
    }
