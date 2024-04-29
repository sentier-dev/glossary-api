"""Model classes for the dds_glossary package."""

from dataclasses import dataclass
from io import BytesIO
from os import getenv
from pathlib import Path
from typing import ClassVar, Optional
from zipfile import ZipFile

import requests
from dotenv import load_dotenv

from .errors import MissingAPIKeyError


@dataclass
class DownloadableFile:
    """
    Represents a downloadable file.

    Attributes:
        name (str): The name of the file.
        extension (str): The file extension.
    """

    name: str
    extension: str

    base_url: ClassVar[str] = ""

    @property
    def file_name(self) -> str:
        """Returns the name of the file.

        Returns:
            str: The name of the file.
        """
        return f"{self.name}{self.extension}"

    def get_url(self) -> str:
        """Returns the URL of the file to download.

        Returns:
            str: The URL of the file.
        """
        return self.__class__.base_url

    def get_params(self) -> dict:
        """Returns the parameters to be used in the request.

        Returns:
            dict: The parameters to be used in the request.
        """
        return {}

    def get_headers(self) -> dict:
        """Returns the headers to be used in the request.

        Returns:
            dict: The headers to be used in the request.
        """
        return {}

    def download(
        self,
        timeout: int = 10,
        file_output_path: Optional[Path] = None,
    ) -> bytes:
        """Retrieve a file from the given URL, save it to a file and return the
        file as bytes.

        Args:
            timeout (int): The number of seconds to wait for the server to send
                data before giving up. Defaults to 10.
            file_output_path (Optional[Path]): The path to save the file.
                Defaults to None.

        Returns:
            bytes: The file content as bytes.
        """
        response = requests.get(
            url=self.get_url(),
            params=self.get_params(),
            headers=self.get_headers(),
            timeout=timeout,
        )
        response.raise_for_status()
        file_bytes = response.content

        if response.headers["Content-Type"] == "application/zip":
            zip_bytes = BytesIO(response.content)
            with ZipFile(zip_bytes) as zipped_file:
                zip_file_name = zipped_file.namelist()[0]
                with zipped_file.open(zip_file_name) as file_handler:
                    file_bytes = file_handler.read()

        if file_output_path:
            file_path = file_output_path / self.file_name
            with open(file_path, "wb") as file_handler:
                file_handler.write(file_bytes)

        return file_bytes


@dataclass
class NERCFile(DownloadableFile):
    """Represents a file hosted on the Natural Environment Research Council
    (NERC) Vocabulary Server.

    Attributes:
        base_url (ClassVar[str]): The base URL for NERC files.
        media_type (NERCMediaType): The media type of the file.
        profile (str): The profile of the NERC file. Defaults to
            "skos". For the full list of available profiles, visit:
            https://vocab.nerc.ac.uk/collection/P06/current/?_profile=alt.
    """

    media_type: str = "application/rdf+xml"
    profile: str = "skos"

    base_url: ClassVar[str] = "https://vocab.nerc.ac.uk/collection/P06/current/"

    def get_params(self) -> dict:
        """Returns the parameters to be used in the request.

        Returns:
            dict: The parameters to be used in the request.
        """
        return {
            "_profile": self.profile,
            "_mediatype": self.media_type,
        }


@dataclass
class CPCFile(DownloadableFile):
    """Represents a file hosted on the FAO Central Product Classification (CPC)
    website.

    Attributes:
        base_url (ClassVar[str]): The base URL for CPC files.
        version (str): The version of the CPC file. Defaults to "2.1".
    """

    version: str = "2.1"

    base_url: ClassVar[str] = (
        "https://storage.googleapis.com/fao-datalab-caliper/Downloads/"
    )

    @property
    def file_suburl(self) -> str:
        """Returns the suburl of the file.

        Returns:
            str: The suburl of the file.
        """
        return (
            f"{self.name.upper()}v{self.version}/"
            f"{self.name.upper()}{self.version.replace('.', '')}"
            f"-core{self.extension}"
        )

    def get_url(self) -> str:
        """Returns the URL of the file to download.

        Returns:
            str: The URL of the file.
        """
        return f"{CPCFile.base_url}{self.file_suburl}"


@dataclass
class OBOEFile(DownloadableFile):
    """Represents a file hosted on the Extensible Observation Ontology
    (OBOE) website.

    Attributes:
        base_url (ClassVar[str]): The base URL for OBOE files.
        API_ENV_KEY (ClassVar[str]): The environment variable key for the OBOE
            API key.
    """

    base_url: ClassVar[str] = (
        "https://data.bioontology.org/ontologies/OBOE/submissions/4/download"
    )
    API_ENV_KEY: ClassVar[str] = "OBOE_API_KEY"

    def get_params(self) -> dict:
        """Returns the parameters to be used in the request.

        Returns:
            dict: The parameters to be used in the request.
        """
        load_dotenv()
        api_key = getenv(OBOEFile.API_ENV_KEY)
        if not api_key:
            raise MissingAPIKeyError(OBOEFile.base_url)
        return {"apikey": api_key}


@dataclass
class OOUMFile(DownloadableFile):
    """Represents a file hosted on the Ontology of Units of Measure (OOUM)
    website.

    Attributes:
        base_url (ClassVar[str]): The base URL for OOUM files.
    """

    base_url: ClassVar[str] = "http://www.ontology-of-units-of-measure.org/"

    def get_url(self) -> str:
        """Returns the URL of the file to download.

        Returns:
            str: The URL of the file.
        """
        return f"{OOUMFile.base_url}data/{self.file_name}"

    def get_headers(self) -> dict:
        """Returns the headers to be used in the request.

        Returns:
            dict: The headers to be used in the request.
        """
        return {"Accept": "text/html"}


@dataclass
class GitHubFile(DownloadableFile):
    """Represents a file hosted on GitHub.

    Attributes:
        base_url (ClassVar[str]): The base URL for GitHub files.
        user (str): The GitHub username.
        repo (str): The GitHub repository name.
        branch (str): The branch name.
        name (str): The file name.
        extension (str): The file extension.
    """

    user: str
    repo: str
    branch: str
    path: str

    base_url: ClassVar[str] = "https://raw.githubusercontent.com"

    def get_url(self) -> str:
        """Returns the URL of the file to download.

        Returns:
            str: The URL of the file.
        """
        return (
            f"{GitHubFile.base_url}/{self.user}/{self.repo}/"
            f"{self.branch}/{self.path}{self.name}"
            f"{self.extension}"
        )
