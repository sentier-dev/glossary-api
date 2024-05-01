"""Tests for dds_glossary.model module."""

from http import HTTPStatus
from io import BytesIO
from zipfile import ZipFile

import pytest
from pandas import DataFrame
from requests import Response

from dds_glossary.errors import MissingAPIKeyError
from dds_glossary.model import (
    CPCFile,
    DownloadableFile,
    GitHubFile,
    HSFile,
    NERCFile,
    OBOEFile,
    OOUMFile,
    RelationshipTuple,
)


def test_downloadable_file_file_name() -> None:
    """Test the file_name property."""
    file_name = "file"
    file_extension = "txt"
    downloadable_file = DownloadableFile(
        name=file_name,
        extension=file_extension,
    )
    assert downloadable_file.file_name == f"{file_name}.{file_extension}"


def test_downloadable_file_file_path(tmp_path) -> None:
    """Test the file_path property."""
    file_name = "file"
    file_extension = "txt"
    downloadable_file = DownloadableFile(
        name=file_name,
        extension=file_extension,
        output_dir=tmp_path,
    )
    assert (
        str(downloadable_file.file_path) == f"{tmp_path}/{file_name}.{file_extension}"
    )


def test_downloadable_file_concept_scheme_name() -> None:
    """Test the concept_scheme_name property."""
    downloadable_file = DownloadableFile(
        name="file",
        extension="txt",
    )
    assert downloadable_file.concept_scheme_name == downloadable_file.name


def test_downloadable_file_concepts_names() -> None:
    """Test the concepts_names property."""
    downloadable_file = DownloadableFile(
        name="file",
        extension="txt",
    )
    assert not downloadable_file.concepts_names


def test_downloadable_file_relationship_tuples() -> None:
    """Test the relationship_tuples property."""
    downloadable_file = DownloadableFile(
        name="file",
        extension="txt",
    )
    assert not downloadable_file.relationship_tuples


def test_downloadable_file_get_url() -> None:
    """Test the get_url method."""
    downloadable_file = DownloadableFile(
        name="file",
        extension="txt",
    )
    assert downloadable_file.get_url() == ""


def test_downloadable_file_get_params() -> None:
    """Test the get_params method."""
    downloadable_file = DownloadableFile(
        name="file",
        extension="txt",
    )
    assert not downloadable_file.get_params()


def test_downloadable_file_get_headers() -> None:
    """Test the get_headers method."""
    downloadable_file = DownloadableFile(
        name="file",
        extension="txt",
    )
    assert not downloadable_file.get_headers()


def test_downloadable_file_download_not_zip(monkeypatch, tmp_path) -> None:
    """Test get_file_from_url when the file is not a zip file."""
    response = Response()
    response.status_code = HTTPStatus.OK
    response.headers["Content-Type"] = "text/plain"
    response._content = b"file content"  # pylint: disable=protected-access
    monkeypatch.setattr("requests.get", lambda *_, **__: response)
    monkeypatch.setattr(DownloadableFile, "get_url", lambda _: "")

    file_name = "file"
    file_extension = "txt"
    content = DownloadableFile(
        name=file_name,
        extension=file_extension,
        output_dir=tmp_path,
    ).download()

    file_output_path = tmp_path / f"{file_name}.{file_extension}"
    assert content == response.content
    assert file_output_path.read_bytes() == response.content


def test_downloadable_file_download_zip(monkeypatch, tmp_path) -> None:
    """Test get_file_from_url when the file is a zip file."""
    file_content = b"file content"
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("exampletxt", file_content)
    zip_buffer.seek(0)
    zip_bytes = zip_buffer.getvalue()

    response = Response()
    response.status_code = HTTPStatus.OK
    response.headers["Content-Type"] = "application/zip"
    response._content = zip_bytes  # pylint: disable=protected-access
    monkeypatch.setattr("requests.get", lambda *_, **__: response)
    monkeypatch.setattr(DownloadableFile, "get_url", lambda _: "")

    file_name = "file"
    file_extension = ".zip"
    content = DownloadableFile(
        name=file_name,
        extension=file_extension,
        output_dir=tmp_path,
    ).download()

    file_output_path = tmp_path / f"{file_name}.{file_extension}"
    assert content == file_content
    assert file_output_path.read_bytes() == file_content


def test_nerc_file_get_params() -> None:
    """Test the get_params method."""
    profile = "profile"
    media_type = "media_type"
    nerc_file = NERCFile(
        name="file",
        extension="txt",
        profile=profile,
        media_type=media_type,
    )
    assert nerc_file.get_params() == {
        "_profile": profile,
        "_mediatype": media_type,
    }


def test_cpc_file_file_suburl() -> None:
    """Test the file_suburl property."""
    cpc_file = CPCFile(
        name="file",
        extension="txt",
    )
    assert cpc_file.file_suburl == "FILEv2.1/FILE21-core.txt"


def test_cpc_file_get_url() -> None:
    """Test the get_url method."""
    cpc_file = CPCFile(
        name="file",
        extension="txt",
    )
    assert cpc_file.get_url() == (f"{CPCFile.base_url}{cpc_file.file_suburl}")


def test_oboe_file_params_api_key_exists(monkeypatch) -> None:
    """Test the get_params method."""
    monkeypatch.setenv("OBOE_API_KEY", "api_key")
    oboe_file = OBOEFile(
        name="file",
        extension="txt",
    )
    assert oboe_file.get_params() == {"apikey": "api_key"}


def test_oboe_file_params_api_key_not_exists(monkeypatch) -> None:
    """Test the get_params method."""
    monkeypatch.setenv("OBOE_API_KEY", "")
    oboe_file = OBOEFile(
        name="file",
        extension="txt",
    )
    with pytest.raises(MissingAPIKeyError):
        oboe_file.get_params()


def test_ooum_file_get_url() -> None:
    """Test the get_url method."""
    ooum_file = OOUMFile(
        name="file",
        extension="txt",
    )
    assert ooum_file.get_url() == (
        "http://www.ontology-of-units-of-measure.org/data/file.txt"
    )


def test_ooum_file_get_headers() -> None:
    """Test the get_headers method."""
    ooum_file = OOUMFile(
        name="file",
        extension="txt",
    )
    assert ooum_file.get_headers() == {"Accept": "text/html"}


def test_github_file_get_url() -> None:
    """Test the get_url method."""
    github_file = GitHubFile(
        name="file",
        extension="txt",
        user="user",
        repo="repo",
        branch="branch",
        path="path/",
    )

    assert github_file.get_url() == (
        "https://raw.githubusercontent.com/user/repo/branch/path/file.txt"
    )


def test_hs_file_concepts_namespace(monkeypatch, tmp_path) -> None:
    """Test the concepts_namespace property."""
    concepts_names = ["concept1", "concept2", "concept3"]
    data_file_path = tmp_path / "concepts.csv"
    data = DataFrame({"description": concepts_names})
    data.to_csv(data_file_path, index=False)
    monkeypatch.setattr(HSFile, "file_path", data_file_path)

    hs_file = HSFile(
        name="file",
        extension="txt",
    )
    assert hs_file.concepts_names == concepts_names


def test_hs_file_relationship_tuples(monkeypatch, tmp_path) -> None:
    """Test the relationship_tuples property."""
    descriptions = ["description1", "description2", "description3"]
    hscodes = ["01", "0101", "010121"]
    parents = ["", "01", "0101"]
    data_file_path = tmp_path / "relationships.csv"
    data = DataFrame(
        {"description": descriptions, "hscode": hscodes, "parent": parents}
    )
    data.to_csv(data_file_path, index=False)
    monkeypatch.setattr(HSFile, "file_path", data_file_path)

    hs_file = HSFile(
        name="file",
        extension="txt",
    )
    assert hs_file.relationship_tuples == [
        RelationshipTuple("description2", "description1", "broader"),
        RelationshipTuple("description3", "description2", "broader"),
    ]
