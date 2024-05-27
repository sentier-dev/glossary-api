"""XML utilities for the dds_glossary package."""

from collections import defaultdict
from typing import Final

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
