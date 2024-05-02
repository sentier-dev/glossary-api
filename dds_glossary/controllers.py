"""Controller classes for the dds_glossary package."""

from http import HTTPStatus
from typing import Optional

from fastapi.responses import JSONResponse
from sqlalchemy import Engine
from sqlalchemy.exc import NoResultFound

from .database import (
    get_concept_schemes,
    get_concepts_for_scheme,
    get_relationships_for_concept,
    save_concept_scheme_file,
)
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
        engine (Engine): The SQLAlchemy engine.
        downloadable_files (list[DownloadableFile]): The files to download.
        timeout (int): The timeout for downloading the files.
    """

    def __init__(
        self,
        engine: Engine,
        downloadable_files: Optional[list[DownloadableFile]] = None,
        timeout: int = 10,
    ):
        if not downloadable_files:
            downloadable_files = DEFAULT_DOWNLOAD_FILES

        self.downloadable_files = downloadable_files
        self.timeout = timeout
        self.engine = engine

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


class APIController:
    """
    Controller for the API in the dds_glossary package.

    Attributes:
        engine (Engine): The SQLAlchemy engine.
    """

    def __init__(self, engine: Engine):
        self.engine = engine

    def get_concept_schemes(self) -> JSONResponse:
        """
        Returns the concept schemes.

        Returns:
            JSONResponse: The concept schemes.
        """
        return JSONResponse(
            content={"concept_schemes": get_concept_schemes(self.engine)},
            media_type="application/json",
            status_code=HTTPStatus.OK,
        )

    def get_concepts_for_scheme(self, concept_scheme_name: str) -> JSONResponse:
        """
        Returns the concepts for a concept scheme name.

        Args:
            concept_scheme_name (str): The name of the concept scheme.

        Returns:
            JSONResponse: The concepts.
        """
        try:
            return JSONResponse(
                content={
                    "concepts": get_concepts_for_scheme(
                        self.engine, concept_scheme_name
                    )
                },
                media_type="application/json",
                status_code=HTTPStatus.OK,
            )
        except NoResultFound:
            return JSONResponse(
                content={"error": f"Concept scheme not found: {concept_scheme_name}"},
                media_type="application/json",
                status_code=HTTPStatus.NOT_FOUND,
            )

    def get_relationships_for_concept(self, concept_name: str) -> JSONResponse:
        """
        Returns the relationships for a concept name.

        Args:
            concept_name (str): The name of the concept.

        Returns:
            JSONResponse: The relationships."""
        try:
            return JSONResponse(
                content={
                    "relationships": get_relationships_for_concept(
                        self.engine, concept_name
                    )
                },
                media_type="application/json",
                status_code=HTTPStatus.OK,
            )
        except NoResultFound:
            return JSONResponse(
                content={"error": f"Concept not found: {concept_name}"},
                media_type="application/json",
                status_code=HTTPStatus.NOT_FOUND,
            )
