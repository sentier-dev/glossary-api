"""Core functions for the dds_glossary package."""

from typing import Optional

from .database import init_engine, save_concept_scheme_file
from .model import (
    CPCFile,
    DownloadableFile,
    GitHubFile,
    HSFile,
    NERCFile,
    OBOEFile,
    OOUMFile,
)

DEFAULT_DOWNLOAD_FILES: list[DownloadableFile] = [
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


class PipelinesController:
    """
    Controller for the pipelines in the dds_glossary package.

    Attributes:
        downloadable_files (list[DownloadableFile]): The files to download.
        timeout (int): The timeout for downloading the files.
    """

    def __init__(
        self,
        database_url: str,
        downloadable_files: Optional[list[DownloadableFile]] = None,
        timeout: int = 10,
    ):
        if not downloadable_files:
            downloadable_files = DEFAULT_DOWNLOAD_FILES

        self.downloadable_files = downloadable_files
        self.timeout = timeout
        self.engine = init_engine(database_url=database_url)

    def download_files(self) -> list[bytes]:
        """
        Downloads the files and returns their contents.

        Returns:
            list[bytes]: The contents of the downloaded files.
        """
        return [file.download(timeout=self.timeout) for file in self.downloadable_files]

    def save_files_to_database(self) -> None:
        """
        Saves the downloaded files to the database.

        Returns:
            None
        """
        for file in self.downloadable_files:
            save_concept_scheme_file(
                self.engine,
                concept_scheme_name=file.concept_scheme_name,
                concepts_names=file.concepts_names,
                relationship_tuples=file.relationship_tuples,
            )

    def run_pipelines(self) -> None:
        """
        Runs the pipelines for downloading and saving all glossary files.

        Returns:
            None
        """
        self.download_files()
        self.save_files_to_database()
