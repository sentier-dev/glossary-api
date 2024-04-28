"""Tests for the core module."""

from http import HTTPStatus
from io import BytesIO
from zipfile import ZipFile

from requests import Response

from dds_glossary.utils import get_file_from_url, get_file_path


def test_get_file_path_output_directory_not_exists() -> None:
    """Test get_file_path when the output directory does not exist."""
    output_directory = None
    file_name = "file"
    file_extension = ".txt"

    file_path = get_file_path(
        output_directory=output_directory,
        file_name=file_name,
        file_extension=file_extension,
    )

    assert file_path is None


def test_get_file_path_output_directory_exists(tmpdir) -> None:
    """Test get_file_path when the output directory exists."""
    file_name = "file"
    file_extension = ".txt"

    file_path = get_file_path(
        output_directory=tmpdir,
        file_name=file_name,
        file_extension=file_extension,
    )

    assert file_path == tmpdir / f"{file_name}{file_extension}"


def test_get_file_from_url_not_zip(monkeypatch, tmp_path) -> None:
    """Test get_file_from_url when the file is not a zip file."""
    response = Response()
    response.status_code = HTTPStatus.OK
    response.headers["Content-Type"] = "text/plain"
    response._content = b"file content"  # pylint: disable=protected-access
    monkeypatch.setattr("requests.get", lambda *_, **__: response)

    url = "https://example.com/"
    file_output_path = tmp_path / "file.txt"

    content = get_file_from_url(
        url=url,
        params={},
        file_output_path=file_output_path,
    )

    assert content == response.content
    assert file_output_path.read_bytes() == response.content


def test_get_file_from_url_zip(monkeypatch, tmp_path) -> None:
    """Test get_file_from_url when the file is a zip file."""
    file_content = b"file content"
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("example.txt", file_content)
    zip_buffer.seek(0)
    zip_bytes = zip_buffer.getvalue()

    response = Response()
    response.status_code = HTTPStatus.OK
    response.headers["Content-Type"] = "application/zip"
    response._content = zip_bytes  # pylint: disable=protected-access
    monkeypatch.setattr("requests.get", lambda *_, **__: response)

    url = "https://example.com/file.zip"
    file_output_path = tmp_path / "file.zip"

    content = get_file_from_url(
        url=url,
        params={},
        file_output_path=file_output_path,
    )

    assert content == file_content
    assert file_output_path.read_bytes() == file_content
