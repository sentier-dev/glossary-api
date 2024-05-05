"""Controller classes for the dds_glossary package."""

from http import HTTPStatus

from fastapi.responses import JSONResponse

from .database import Engine, get_concept_schemes


class GlossaryController:  # pylint: disable=too-few-public-methods
    """
    Controller for the glossary.

    Attributes:
        engine (Engine): The database engine.
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
