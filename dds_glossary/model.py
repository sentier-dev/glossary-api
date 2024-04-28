"""Model classes for the dds_glossary package."""

from dataclasses import dataclass


@dataclass
class NERCMediaType:
    """Represents a media type used while dowloading NERC files.

    Attributes:
        url_param (str): The URL parameter for the media type.
        file_extension (str): The downloaded file extension.
    """

    url_param: str
    file_extension: str


@dataclass
class GitHubFile:
    """Represents a file hosted on GitHub.

    Attributes:
        user (str): The GitHub username.
        repo (str): The GitHub repository name.
        branch (str): The branch name.
        name (str): The file name.
        extension (str): The file extension.
    """

    user: str
    repo: str
    branch: str
    name: str
    extension: str
