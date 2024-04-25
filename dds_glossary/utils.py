"""Utility functions for the dds_glossary package."""

import json
from typing import Optional

import rdflib
import requests


def rdf_to_json_ld(
    rdf_data: bytes,
    rdf_format: str = "application/rdf+xml",
    serializer_name: str = "json-ld",
) -> dict:
    """Convert RDF data to JSON-LD."""

    graph = rdflib.Graph()
    graph.parse(data=rdf_data, format=rdf_format)
    jsonld_data = graph.serialize(format=serializer_name)
    return json.loads(jsonld_data)


def get_rdf_data(
    url: str,
    timeout: int = 10,
    rdf_output_path: Optional[str] = None,
) -> bytes:
    """Get RDF data from a URL."""

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    if rdf_output_path:
        with open(rdf_output_path, "wb") as rdf_file:
            rdf_file.write(response.content)

    return response.content
