"""Main entry for the dds_glossary server."""
from os import getenv

from http import HTTPStatus

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import sentry_sdk
from starlette.templating import _TemplateResponse

from . import __version__
from .auth import get_api_key
from .controllers import GlossaryController


SENTRY_DSN=getenv("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = FastAPI()
controller = GlossaryController()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(
    request: Request,
    search_term: str = "",
    concept_scheme_iri: str = "",
    lang: str = "en",
) -> _TemplateResponse:
    """Get the home page.
    If a `search_term` term is provided, it will filter the concepts by the search term.
    If a `concept_scheme_iri` is provided, it will filter the concepts by the concept
    scheme.

    Args:
        request (Request): The request.
        search_term (str): The search term to filter the concepts. Defaults to "".
        concept_scheme_iri (str): The concept scheme IRI to filter the concepts.
            Defaults to "".
        lang (str): The language to use for searching concepts. Defaults to "en".

    Returns:
        _TemplateResponse: The home page with search results if any.
    """
    if concept_scheme_iri:
        concepts = controller.get_concepts(concept_scheme_iri, lang=lang)
    else:
        concepts = controller.search_database(search_term, lang=lang)

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "schemes": controller.get_concept_schemes(lang=lang),
            "concepts": concepts,
        },
    )


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

    Args:
        _api_key (dict): The API key.
        reload (bool): Flag to reload the datasets. Defaults to False.

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

    Args:
        lang (str): The language. Defaults to "en".

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

    Args:
        concept_scheme_iri (str): The concept scheme IRI.
        lang (str): The language. Defaults to "en".

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


@app.get("/collection")
def get_collection(collection_iri: str, lang: str = "en") -> JSONResponse:
    """
    Returns a collection.

    Args:
        collection_iri (str): The collection IRI.
        lang (str): The language. Defaults to "en".

    Returns:
        JSONResponse: The collection.
    """
    return JSONResponse(
        content=controller.get_collection(collection_iri, lang=lang),
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )


@app.get("/concept")
def get_concept(concept_iri: str, lang: str = "en") -> JSONResponse:
    """
    Returns a concept.

    Args:
        concept_iri (str): The concept IRI.
        lang (str): The language. Defaults to "en".

    Returns:
        JSONResponse: The concept.
    """
    return JSONResponse(
        content=controller.get_concept(concept_iri, lang=lang),
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )
