"""Routes for the dds_glossary server."""

from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_versioning import version
from starlette.templating import Jinja2Templates, _TemplateResponse

from .auth import get_api_key
from .schema import (
    CollectionResponse,
    ConceptResponse,
    ConceptSchemeResponse,
    FullConeptResponse,
    InitDatasetsResponse,
    VersionResponse,
)
from .services import GlossaryController, get_controller, get_templates

router_versioned = APIRouter()
router_non_versioned = APIRouter()


@router_non_versioned.get("/")
def home(
    request: Request,
    controller: GlossaryController = Depends(get_controller),
    templates: Jinja2Templates = Depends(get_templates),
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
        controller (GlossaryController): The glossary controller.
        templates (Jinja2Templates): The Jinja2 templates.
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


@router_versioned.get("/status")
@version(0, 1)
def status() -> RedirectResponse:
    """Redirect to the status page."""
    return RedirectResponse(url="https://sentier.instatus.com/")


@router_versioned.get("/search")
@version(0, 1)
def search(
    search_term: str,
    controller: GlossaryController = Depends(get_controller),
    lang: str = "en",
) -> list[ConceptResponse]:
    """Search concepts according to given expression.
    Note: This will be removed once #35 (Add elasticsearch) is closed.

    Args:
        search_term (str): The search term to filter the concepts.
        controller (GlossaryController): The glossary controller.
        lang (str): The language to use for searching concepts. Defaults to "en".

    Returns:
        list[ConceptResponse]: The search results, if any.
    """
    return controller.search_database(search_term, lang=lang)


@router_versioned.get("/version")
@version(0, 1)
def get_version() -> VersionResponse:
    """Get the version of the server.

    Returns:
        VersionResponse: The version of the server.
    """
    return VersionResponse()


@router_versioned.post("/init_datasets")
@version(0, 1)
def init_datasets(
    controller: GlossaryController = Depends(get_controller),
    _api_key: dict = Depends(get_api_key),
    reload: bool = False,
) -> InitDatasetsResponse:
    """Initialize the datasets.

    Args:
        controller (GlossaryController): The glossary controller.
        _api_key (dict): The API key.
        reload (bool): Flag to reload the datasets. Defaults to False.

    Returns:
        InitDatasetsResponse: The response.
    """
    return controller.init_datasets(reload=reload)


@router_versioned.get("/schemes")
@version(0, 1)
def get_concept_schemes(
    controller: GlossaryController = Depends(get_controller),
    lang: str = "en",
) -> list[ConceptSchemeResponse]:
    """
    Returns all the saved concept schemes.

    Args:
        controller (GlossaryController): The glossary controller.
        lang (str): The language. Defaults to "en".

    Returns:
        list[ConceptSchemeResponse]: The concept schemes.
    """
    return controller.get_concept_schemes(lang=lang)


@router_versioned.get("/concepts")
@version(0, 1)
def get_concepts(
    concept_scheme_iri: str,
    controller: GlossaryController = Depends(get_controller),
    lang: str = "en",
) -> JSONResponse:
    """
    Returns all the saved concepts for a concept scheme.

    Args:
        concept_scheme_iri (str): The concept scheme IRI.
        controller (GlossaryController): The glossary controller.
        lang (str): The language. Defaults to "en".

    Returns:
        JSONResponse: The concepts.
    """
    return JSONResponse(
        content={"concepts": controller.get_concepts(concept_scheme_iri, lang=lang)},
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )


@router_versioned.get("/collection")
@version(0, 1)
def get_collection(
    collection_iri: str,
    controller: GlossaryController = Depends(get_controller),
    lang: str = "en",
) -> CollectionResponse:
    """
    Returns a collection.
    Args:
        collection_iri (str): The collection IRI.
        controller (GlossaryController): The glossary controller.
        lang (str): The language. Defaults to "en".
    Returns:
        JSONResponse: The collection.
    """
    return controller.get_collection(collection_iri, lang=lang)


@router_versioned.get("/concept")
@version(0, 1)
def get_concept(
    concept_iri: str,
    controller: GlossaryController = Depends(get_controller),
    lang: str = "en",
) -> FullConeptResponse:
    """
    Returns a concept.

    Args:
        concept_iri (str): The concept IRI.
        lang (str): The language. Defaults to "en".

    Returns:
        FullConeptResponse: The concept with concept scheme and relations.
    """
    return controller.get_concept(concept_iri, lang=lang)
