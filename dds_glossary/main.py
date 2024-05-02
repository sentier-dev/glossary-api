"""Main entry for the dds_glossary server."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .controllers import APIController
from .database import init_engine

app = FastAPI()
engine = init_engine()
api_controller = APIController(engine)


@app.get("/schemes")
def get_concept_schemes() -> JSONResponse:
    """Get the concept schemes.

    Returns:
        JSONResponse: The concept schemes.
    """
    return api_controller.get_concept_schemes()


@app.get("/schemes/{scheme_name}")
def get_concepts_for_scheme(scheme_name: str) -> JSONResponse:
    """Get the concepts for a scheme.

    Args:
        scheme_name (str): The name of the scheme.

    Returns:
        JSONResponse: The concepts for the scheme.
    """
    return api_controller.get_concepts_for_scheme(concept_scheme_name=scheme_name)


@app.get("/concepts/{concept_name}")
def get_relationships_for_concept(concept_name: str) -> JSONResponse:
    """Get the relationships for a concept.

    Args:
        concept_name (str): The name of the concept.

    Returns:
        JSONResponse: The relationships for the concept.
    """
    return api_controller.get_relationships_for_concept(concept_name=concept_name)
