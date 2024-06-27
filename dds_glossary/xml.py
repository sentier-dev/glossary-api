"""XML utilities for the dds_glossary package."""

from collections import defaultdict
from pathlib import Path
from typing import Final

from defusedxml.lxml import parse as parse_xml

from .enums import SemanticRelationType
from .model import (
    Collection,
    Concept,
    ConceptScheme,
    InCollection,
    InScheme,
    ParsedDataset,
    SemanticRelation,
)

XML_NAMESPACE: Final[str] = "{http://www.w3.org/XML/1998/namespace}"


def get_element_attribute(element, attribute: str, default_value: str = "") -> str:
    """
    Get an attribute from the XML element if it exists, else return default_value.

    Args:
        element (ElementBase): The XML element to parse.
        attribute (str): The attribute to search for.
        default_value (str): The default value to return if the attribute does not
            exist.

    Returns:
        str: The attribute value if it exists, else the default value.
    """
    attribute = element.get(f"{{{element.nsmap['rdf']}}}{attribute}")
    return attribute if attribute is not None else default_value


def get_sub_element_attributes(
    element,
    tag: str,
    attribute: str,
    default_value: str = "",
) -> list[str]:
    """
    Get the attributes of the sub elements.

    Args:
        element (ElementBase): The XML element to parse.
        tag (str): The tag to search for.
        attribute (str): The attribute to get.

    Returns:
        list: The attributes.
    """
    return [
        get_element_attribute(sub_element, attribute, default_value)
        for sub_element in element.findall(tag, namespaces=element.nsmap)
    ]


def get_sub_element_as_str(element, tag: str, default_value: str = "") -> str:
    """
    Get a sub element text from the XML element if tag exists, else return
    default_value.

    Args:
        element (ElementBase): The XML element to parse.
        tag (str): The tag to search for.
        default_value (str): The default value to return if the tag does not exist.

    Returns:
        str: The sub element text if the tag exists, else the default value.
    """
    sub_element = element.find(tag, namespaces=element.nsmap)
    return sub_element.text if sub_element is not None else default_value


def get_sub_elements_as_dict(element, tag: str) -> dict[str, str]:
    """
    Get the sub elements as a dictionary.

    Args:
        element (ElementBase): The XML element to parse.
        tag (str): The tag to search for.

    Returns:
        dict: The labels.
    """
    return {
        sub_element.get(f"{XML_NAMESPACE}lang"): sub_element.text
        for sub_element in element.findall(tag, namespaces=element.nsmap)
    }


def get_sub_elements_as_dict_of_lists(element, tag: str) -> dict[str, list[str]]:
    """
    Get the sub elements as a dictionary of lists.

    Args:
        element (ElementBase): The XML element to parse.
        tag (str): The tag to search for.

    Returns:
        dict: The alternative labels.
    """
    sub_element_dict = defaultdict(list)
    for sub_element in element.findall(tag, namespaces=element.nsmap):
        sub_element_dict[sub_element.get(f"{XML_NAMESPACE}lang")].append(
            sub_element.text
        )
    return sub_element_dict


def concept_scheme_from_xml(element) -> ConceptScheme:
    """
    Create a ConceptScheme object from the XML element.

    Args:
        element (ElementBase): The XML element to parse.

    Returns:
        ConceptScheme: The concept scheme.
    """
    return ConceptScheme(
        iri=get_element_attribute(element, "about"),
        notation=get_sub_element_as_str(element, "core:notation"),
        scopeNote=get_sub_element_as_str(element, "core:scopeNote"),
        prefLabels=get_sub_elements_as_dict(element, "core:prefLabel"),
    )


def collection_from_xml(element) -> Collection:
    """
    Return a Collection instance from an XML element.

    Args:
        element (ElementBase): The XML element to parse.

    Returns:
        Collection: The parsed Collection instance.
    """
    return Collection(
        iri=get_element_attribute(element, "about"),
        notation=get_sub_element_as_str(element, "core:notation"),
        prefLabels=get_sub_elements_as_dict(element, "core:prefLabel"),
    )


def concept_from_xml(element) -> Concept:
    """
    Return a Concept instance from an XML element.

    Args:
        element (ElementBase): The XML element to parse.
        concept_schemes (ConceptScheme): The concept schemes to which the concept
            belongs.

    Returns:
        Concept: The parsed Concept instance.
    """
    return Concept(
        iri=get_element_attribute(element, "about"),
        identifier=get_sub_element_as_str(element, "x_1.1:identifier"),
        notation=get_sub_element_as_str(element, "core:notation"),
        prefLabels=get_sub_elements_as_dict(element, "core:prefLabel"),
        altLabels=get_sub_elements_as_dict_of_lists(element, "core:altLabel"),
        scopeNotes=get_sub_elements_as_dict(element, "core:scopeNote"),
    )


def semantic_relations_from_xml(element) -> list["SemanticRelation"]:
    """
    Return a list of SemanticRelation instances from an XML element.

    Args:
        element (ElementBase): The XML element to parse.

    Returns:
        list[SemanticRelation]: The parsed list of SemanticRelation instances.
    """
    relations: dict[SemanticRelationType, list[str]] = {}
    for relation_type in SemanticRelationType:
        relations[relation_type] = get_sub_element_attributes(
            element, f"core:{relation_type.value}", "resource"
        )
    return [
        SemanticRelation(
            type=relation_type,
            source_concept_iri=get_element_attribute(element, "about"),
            target_concept_iri=target_concept_iri,
        )
        for relation_type, target_concept_iris in relations.items()
        for target_concept_iri in target_concept_iris
    ]


def in_scheme_from_xml(element) -> list[InScheme]:
    """
    Return a list of InScheme instances from an XML element.

    Args:
        element (ElementBase): The XML element to parse.

    Returns:
        list[InScheme]: The parsed list of InScheme instances.
    """
    concept_iri = get_element_attribute(element, "about")
    scheme_iris = get_sub_element_attributes(element, "core:inScheme", "resource")
    return [
        InScheme(member_iri=concept_iri, scheme_iri=scheme_iri)
        for scheme_iri in scheme_iris
    ]


def in_collection_from_xml(element) -> list[InCollection]:
    """
    Return a list of InCollection instances from an XML element.

    Args:
        element (ElementBase): The XML element to parse.

    Returns:
        list[InCollection]: The parsed list of InCollection instances.
    """
    collection_iri = get_element_attribute(element, "about")
    member_iris = get_sub_element_attributes(element, "core:member", "resource")
    return [
        InCollection(collection_iri=collection_iri, member_iri=member_iri)
        for member_iri in member_iris
    ]


def parse_dataset(dataset_path: Path) -> ParsedDataset:
    """
    Parse a dataset.

    Args:
        dataset_path (Path): The dataset path.

    Returns:
        tuple[list[ConceptScheme], list[Concept], list[Collection],
            list[SemanticRelation]]: The concept schemes, concepts, collections,
            and semantic relations.
    """
    root = parse_xml(dataset_path).getroot()
    concept_scheme_elements = root.findall("core:ConceptScheme", root.nsmap)
    collection_elements = root.findall("core:Collection", root.nsmap)
    concept_elements = root.findall("core:Concept", root.nsmap)
    concept_schemes = [
        concept_scheme_from_xml(concept_scheme_element)
        for concept_scheme_element in concept_scheme_elements
    ]
    concepts = [
        concept_from_xml(concept_element) for concept_element in concept_elements
    ]
    collections = [
        collection_from_xml(collection_element)
        for collection_element in collection_elements
    ]
    semantic_relations: list[SemanticRelation] = []
    for concept_element in concept_elements:
        semantic_relations.extend(semantic_relations_from_xml(concept_element))
    member_elements = collection_elements + concept_elements
    in_schemes: list[InScheme] = []
    for member_element in member_elements:
        in_schemes.extend(in_scheme_from_xml(member_element))
    in_collections: list[InCollection] = []
    for member_element in member_elements:
        in_collections.extend(in_collection_from_xml(member_element))
    return ParsedDataset(
        concept_schemes=concept_schemes,
        concepts=concepts,
        collections=collections,
        semantic_relations=semantic_relations,
        in_schemes=in_schemes,
        in_collections=in_collections,
    )
