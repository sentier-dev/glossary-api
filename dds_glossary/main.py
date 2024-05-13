"""Main entry for the dds_glossary server."""

from http import HTTPStatus

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from . import __version__
from .auth import get_api_key
from .controllers import GlossaryController

app = FastAPI()
controller = GlossaryController()


@app.get("/version")
def get_version() -> JSONResponse:
    """Get the version of the server.

    Returns:
        JSONResponse: The version of the server.
    """
    return JSONResponse(
        content={
            "version": __version__,
        },
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )


@app.post("/init_datasets")
def init_datasets(
    _api_key: dict = Depends(get_api_key),
    reload: bool = False,
) -> JSONResponse:
    """Initialize the datasets.

    Returns:
        JSONResponse: The status of the init request.
    """
    saved_datasets, failed_datasets = controller.init_datasets(reload=reload)
    return JSONResponse(
        content={
            "saved_datasets": saved_datasets,
            "failed_datasets": failed_datasets,
        },
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )


@app.get("/schemes")
def get_concept_schemes(lang: str = "en") -> JSONResponse:
    """
    Returns all the saved concept schemes.

    Returns:
        JSONResponse: The concept schemes.
    """
    return JSONResponse(
        content={
            "concept_schemes": controller.get_concept_schemes(lang=lang),
        },
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )


@app.get("/concepts")
def get_concepts(concept_scheme_iri: str, lang: str = "en") -> JSONResponse:
    """
    Returns all the saved concepts for a concept scheme.

    Returns:
        JSONResponse: The concepts.
    """
    return JSONResponse(
        content={
            "concepts": controller.get_concepts(concept_scheme_iri, lang=lang),
        },
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )


@app.get("/concept")
def get_concept(concept_iri: str, lang: str = "en") -> JSONResponse:
    """
    Returns a concept.

    Returns:
        JSONResponse: The concept.
    """
    return JSONResponse(
        content=controller.get_concept(concept_iri, lang=lang),
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )
