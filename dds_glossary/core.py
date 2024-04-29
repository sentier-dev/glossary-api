"""Core functions for the dds_glossary package."""

from pathlib import Path
from typing import Optional

from .model import CPCFile, DownloadableFile, GitHubFile, NERCFile, OBOEFile

DOWNLOAD_FILES: list[DownloadableFile] = [
    # Harmonized System (HS)
    GitHubFile(
        user="datasets",
        repo="harmonized-system",
        branch="master",
        path="data/",
        name="harmonized-system",
        extension=".csv",
    ),
    # Unit Ontology
    GitHubFile(
        user="bio-ontology-research-group",
        repo="unit-ontology",
        branch="master",
        path="",
        name="uo",
        extension=".owl",
    ),
    NERCFile(name="nerc", extension=".rdf"),
    CPCFile(name="cpc", extension=".rdf"),
    OBOEFile(name="oboe", extension=".owl"),
]


def downloads(timeout: int = 10, ouput_directory: Optional[Path] = None) -> list[bytes]:
    """Downloads the files and returns their contents.

    Args:
        timeout (int): The number of seconds to wait for the server to send
            data before giving up. Defaults to 10.
        file_output_path (Optional[Path]): The path to save the files.
            Defaults to None.

    Returns:
        list[bytes]: The contents of the downloaded files.
    """
    return [
        file.download(timeout=timeout, file_output_path=ouput_directory)
        for file in DOWNLOAD_FILES
    ]
