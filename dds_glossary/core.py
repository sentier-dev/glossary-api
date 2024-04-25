"""Core functions for the dds_glossary package."""

import json
from typing import Optional

from .utils import get_rdf_data, rdf_to_json_ld


def get_show_voc_json_ld(
    rdf_url: str = "https://www.w3.org/TR/skos-reference/skos.rdf",
    rdf_output_path: Optional[str] = None,
    json_output_path: Optional[str] = None,
) -> dict:
    """Get the Show Vocabulary in JSON-LD format."""

    rdf_data = get_rdf_data(rdf_url, rdf_output_path=rdf_output_path)
    json_ld_data = rdf_to_json_ld(rdf_data)

    if json_output_path:
        with open(json_output_path, "w", encoding="UTF-8") as json_file:
            json.dump(json_ld_data, json_file)

    return json_ld_data
