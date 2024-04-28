"""Error classes for the dds_glossary package."""


class DDSGlossaryError(Exception):
    """Base class for dds_glossary errors."""


class MissingAPIKeyError(DDSGlossaryError):
    """Raised when the API key is missing."""

    def __init__(self, endpoint: str) -> None:
        super().__init__(f"The API key is missing for: {endpoint}.")
