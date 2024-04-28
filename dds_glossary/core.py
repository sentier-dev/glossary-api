"""Core functions for the dds_glossary package."""

from os import getenv
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .errors import MissingAPIKeyError
from .model import GitHubFile, NERCMediaType
from .utils import get_file_from_github, get_file_from_url, get_file_path


def get_nerc_file(
    url: str = "https://vocab.nerc.ac.uk/collection/P06/current/",
    media_type: NERCMediaType = NERCMediaType("application/rdf+xml", ".rdf"),
    profile: str = "skos",
    output_directory: Optional[Path] = None,
    file_name: str = "nerc",
) -> bytes:
    """
    Fetches the Natural Environment Research Council (NERC) BODC-approved data
    storage units file from the specified URL with the given parameters.

    Args:
        url (str, optional): The URL of the NERC website. Defaults to
            "https://vocab.nerc.ac.uk/collection/P06/current/".
        media_type (NERCMediaType, optional): The media type of the NERC file.
            Defaults to NERCMediaType("application/rdf+xml", ".rdf").
        profile (str, optional): The profile of the NERC file. Defaults to
            "skos". For the full list of available profiles, visit:
            https://vocab.nerc.ac.uk/collection/P06/current/?_profile=alt
        output_directory (Path, optional): The output directory to
            save the NERC file. If not provided, the file will not be saved to
            disk. Defaults to None.
        file_name (str, optional): The name of the NERC file. Defaults to
            "nerc".

    Returns:
        bytes: The content of the fetched NERC file.

    """
    file_output_path = get_file_path(
        output_directory=output_directory,
        file_name=file_name,
        file_extension=media_type.file_extension,
    )

    return get_file_from_url(
        url=url,
        params={
            "_profile": profile,
            "_mediatype": media_type.url_param,
        },
        file_output_path=file_output_path,
    )


def get_oboe_file(
    url: str = "https://data.bioontology.org/ontologies/OBOE/submissions/4/download",
    api_key: Optional[str] = None,
    output_directory: Optional[Path] = None,
    file_name: str = "oboe",
    file_extension: str = ".owl",
) -> bytes:
    """
    Downloads the Extensible Observation Ontology (OBOE) file from the given
        URL using the provided API key.

    Args:
        url (str, optional): The URL of the oboe website. Defaults to
            "https://data.bioontology.org/ontologies/OBOE/submissions/4/download".
        api_key (str, optional): The API key for the oboe website. If not
            provided, the function will attempt to retrieve the API key from
            the environment variables. Defaults to None.
        output_directory (Path, optional): The directory to save the
            downloaded file. If not provided, the file will not be saved to
            disk. Defaults to None.
        file_name (str, optional): The name of the downloaded file. Defaults
            to "oboe".
        file_extension (str, optional): The extension of the downloaded file.
            Defaults to ".owl".

    Returns:
        bytes: The content of the downloaded OBOE file.

    Raises:
        MissingAPIKeyError: If the API key is not provided and is not found in
            the environment variables.
    """
    file_output_path = get_file_path(
        output_directory=output_directory,
        file_name=file_name,
        file_extension=file_extension,
    )

    if not api_key:
        load_dotenv()
        api_key = getenv("OBOE_API_KEY")
        if not api_key:
            raise MissingAPIKeyError(url)

    return get_file_from_url(
        url=url,
        params={"apikey": api_key},
        file_output_path=file_output_path,
    )


def get_unit_ontology_file(
    github_file: GitHubFile = GitHubFile(
        user="bio-ontology-research-group",
        repo="unit-ontology",
        branch="master",
        name="uo",
        extension=".owl",
    ),
    output_directory: Optional[Path] = None,
) -> bytes:
    """
    Retrieves the unit ontology file from a GitHub repository.

    Args:
        github_file (GitHubFile): The GitHub file details to retrieve.
        output_directory (Optional[Path]): The directory where the file will
            be saved. If None, the file will not be saved to the disk.

    Returns:
        bytes: The content of the downloaded unit ontology file.

    """
    file_output_path = get_file_path(
        output_directory=output_directory,
        file_name=github_file.name,
        file_extension=github_file.extension,
    )
    return get_file_from_github(
        github_file=github_file,
        file_output_path=file_output_path,
    )
