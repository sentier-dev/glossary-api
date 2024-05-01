"""Core functions for the dds_glossary package."""

from .model import (
    CPCFile,
    DownloadableFile,
    GitHubFile,
    HSFile,
    NERCFile,
    OBOEFile,
    OOUMFile,
)

DOWNLOAD_FILES: list[DownloadableFile] = [
    # Unit Ontology (UO)
    GitHubFile(
        user="bio-ontology-research-group",
        repo="unit-ontology",
        branch="master",
        path="",
        name="uo",
        extension="owl",
    ),
    HSFile(name="harmonized-system", extension="csv"),
    NERCFile(name="nerc", extension="rdf"),
    CPCFile(name="cpc", extension="csv"),
    OBOEFile(name="oboe", extension="owl"),
    OOUMFile(name="Valerie-9", extension="ttl"),
    OOUMFile(name="FoodAllergies", extension="ttl"),
    OOUMFile(name="warenkennisbank", extension="ttl"),
    OOUMFile(name="FoodTaxonomy", extension="ttl"),
    OOUMFile(name="om-2", extension="ttl"),
    OOUMFile(name="om-1.8", extension="ttl"),
]


def download_files(timeout: int = 10) -> list[bytes]:
    """Downloads the files and returns their contents.

    Args:
        timeout (int): The number of seconds to wait for the server to send
            data before giving up. Defaults to 10.

    Returns:
        list[bytes]: The contents of the downloaded files.
    """
    return [file.download(timeout=timeout) for file in DOWNLOAD_FILES]
