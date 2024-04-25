"""Tests for the core module."""

import json

from dds_glossary.core import get_show_voc_json_ld


def test_get_show_voc_json_ld(tmp_path) -> None:
    """Test the get_show_voc_json_ld function."""

    rdf_path = tmp_path / "data.rdf"
    json_path = tmp_path / "data.json"

    json_ld = get_show_voc_json_ld(
        rdf_output_path=rdf_path,
        json_output_path=json_path,
    )
    with open(json_path, "r", encoding="UTF-8") as json_file:
        json_path_dict = json.load(json_file)
    assert json_ld == json_path_dict
