"""Utility functions for the dds_glossary package."""

from io import BytesIO
from pathlib import Path
from typing import Optional, Union
from zipfile import ZipFile

import requests

from .model import GitHubFile


def get_file_path(
    output_directory: Optional[Path],
    file_name: str,
    file_extension: str,
) -> Optional[Path]:
    """
    Returns the file path by concatenating the output directory, file name
        and file extension.

    Args:
        output_directory (Path): The directory where the file will be saved.
        file_name (str): The name of the file.
        file_extension (str): The extension of the file.

    Returns:
        Optional[Path]: The file path as a Path object, or None if the output
            directory is not provided.
    """
    if not output_directory:
        return None

    return output_directory / f"{file_name}{file_extension}"


def get_file_from_url(
    url: str,
    params: Optional[dict[str, str]] = None,
    timeout: int = 10,
    file_output_path: Optional[Union[str, Path]] = None,
) -> bytes:
    """
    Retrieve a file from the given URL, save it to a file and return the file
    as bytes.

    Args:
        url (str): The URL of the file to retrieve.
        params (dict[str, str]): The parameters to include in the request.
        timeout (int, optional): The timeout value for the request in seconds.
            Defaults to 10.
        file_output_path (str, optional): The path to save the file. If not
            provided, the file will not be saved to the disk.

    Returns:
        bytes: The file content as bytes.

    Raises:
        requests.HTTPError: If the request to the URL fails.
        KeyError: If the 'Content-Type' header is missing from the response.
        zipfile.BadZipFile: If the response content is a ZIP file, but it is
            invalid.

    """
    if not params:
        params = {}

    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    file_bytes = response.content

    if response.headers["Content-Type"] == "application/zip":
        zip_bytes = BytesIO(response.content)
        with ZipFile(zip_bytes) as zipped_file:
            with zipped_file.open(zipped_file.namelist()[0]) as file_handler:
                file_bytes = file_handler.read()

    if file_output_path:
        with open(file_output_path, "wb") as file_handler:
            file_handler.write(file_bytes)

    return file_bytes


def get_file_from_github(
    github_file: GitHubFile,
    file_output_path: Optional[Path] = None,
    base_url: str = "https://raw.githubusercontent.com",
) -> bytes:
    """
    Retrieve a file from GitHub raw content and return the file as bytes.

    Args:
        github_file (GitHubFile): The GitHub file details to retrieve.
        file_output_path (str, optional): The path to save the file. If not
            provided, the file will not be saved to the disk.
        base_url (str, optional): The base URL of the GitHub raw content API.

    Returns:
        bytes: The file content as bytes.
    """
    url = (
        f"{base_url}/{github_file.user}/{github_file.repo}/"
        f"{github_file.branch}/{github_file.name}{github_file.extension}"
    )
    return get_file_from_url(url, file_output_path=file_output_path)
