"""Tests for dds_glossary.model module."""

from dds_glossary.model import (
    Concept,
    ConceptScheme,
    SemanticRelation,
    SemanticRelationType,
)


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


def test_concept_scheme_get_pref_label_language_exists(
    concept_scheme: ConceptScheme,
) -> None:
    """It should return the preferred label in the specified language."""
    assert (
        concept_scheme.get_pref_label("sk")
        == "Kombinovaná Nomenklatúra, 2024 (KN 2024)"
    )


def test_concept_scheme_get_pref_label_language_does_not_exist(
    concept_scheme: ConceptScheme,
) -> None:
    """It should return the preferred label in English if the specified language does
    not exist."""
    assert (
        concept_scheme.get_pref_label("fr") == "Combined Nomenclature, 2024 (CN 2024)"
    )


def test_concept_scheme_get_pref_label_no_language_specified(
    concept_scheme: ConceptScheme,
) -> None:
    """It should return the preferred label in English if no language is specified."""
    assert concept_scheme.get_pref_label() == "Combined Nomenclature, 2024 (CN 2024)"


def test_concept_scheme_get_pref_label_no_language_specified_no_english(
    concept_scheme: ConceptScheme,
) -> None:
    """It should return an empty string if no language is specified and English does
    not exist."""
    concept_scheme.prefLabels = {}
    assert concept_scheme.get_pref_label() == ""


def test_concept_scheme_to_dict(concept_scheme: ConceptScheme) -> None:
    """It should return a dictionary representation of the ConceptScheme instance."""
    assert concept_scheme.to_dict("sk") == {
        "iri": "http://data.europa.eu/xsp/cn2024/cn2024",
        "notation": "CN 2024",
        "scopeNote": "http://publications.europa.eu/resource/oj/JOC_2019_119_R_0001",
        "prefLabel": "Kombinovaná Nomenklatúra, 2024 (KN 2024)",
    }


def test_concept_from_xml_element(
    concept: Concept, concept_scheme: ConceptScheme
) -> None:
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
    assert concept.scheme_iri == concept_scheme.iri


def test_concept_get_pref_label_language_exists_concept(concept: Concept) -> None:
    """It should return the preferred label in the specified language."""
    assert concept.get_pref_label("sk") == "0203 21 -- Trupy a polovičky trupov"


def test_concept_get_pref_label_language_does_not_exist_concept(
    concept: Concept,
) -> None:
    """It should return the preferred label in English if the specified language does
    not exist."""
    assert concept.get_pref_label("fr") == "0203 21 -- Carcases and half-carcases"


def test_concept_get_pref_label_no_language_specified_concept(concept: Concept) -> None:
    """It should return the preferred label in English if no language is specified."""
    assert concept.get_pref_label() == "0203 21 -- Carcases and half-carcases"


def test_concept_get_pref_label_no_language_specified_no_english_concept(
    concept: Concept,
) -> None:
    """It should return an empty string if no language is specified and English does
    not exist."""
    concept.prefLabels = {}
    assert concept.get_pref_label() == ""


def test_concept_get_alt_label_language_exists_concept(concept: Concept) -> None:
    """It should return the alternative label in the specified language."""
    assert concept.get_alt_label("sk") == "-- Trupy a polovičky trupov"


def test_concept_get_alt_label_language_does_not_exist_concept(
    concept: Concept,
) -> None:
    """It should return the alternative label in English if the specified language does
    not exist."""
    assert concept.get_alt_label("fr") == "-- Carcases and half-carcases"


def test_concept_get_alt_label_no_language_specified_concept(concept: Concept) -> None:
    """It should return the alternative label in English if no language is specified."""
    assert concept.get_alt_label() == "-- Carcases and half-carcases"


def test_concept_get_alt_label_no_language_specified_no_english_concept(
    concept: Concept,
) -> None:
    """It should return an empty string if no language is specified and English does
    not exist."""
    concept.altLabels = {}
    assert concept.get_alt_label() == ""


def test_concept_get_scope_note_language_exists_concept(concept: Concept) -> None:
    """It should return the scope note in the specified language."""
    assert (
        concept.get_scope_note("fr")
        == "Carcasses ou demi-carcasses, de porcins, congelées"
    )


def test_concept_get_scope_note_language_does_not_exist_concept(
    concept: Concept,
) -> None:
    """It should return the scope note in English if the specified language does
    not exist."""
    assert concept.get_scope_note("mt") == "Frozen carcases and half-carcases of swine"


def test_concept_get_scope_note_no_language_specified_concept(concept: Concept) -> None:
    """It should return the scope note in English if no language is specified."""
    assert concept.get_scope_note() == "Frozen carcases and half-carcases of swine"


def test_concept_get_scope_note_no_language_specified_no_english_concept(
    concept: Concept,
) -> None:
    """It should return an empty string if no language is specified and English does
    not exist."""
    concept.scopeNotes = {}
    assert concept.get_scope_note() == ""


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
