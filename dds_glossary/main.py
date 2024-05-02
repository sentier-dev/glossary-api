"""Main entry for the dds_glossary server."""

from os import getenv
from typing import Union

from fastapi import FastAPI

from .controllers import APIController, PipelinesController
from .database import Concept, ConceptScheme, Relationship

database_url = getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable not set.")

app = FastAPI()
controller = APIController(database_url=database_url)
pipelines_controller = PipelinesController(database_url=database_url)


@app.get("/run_pipelines")
def run_pipelines() -> dict:
    """Run the pipelines.

    Returns:
        dict: The message that the pipelines ran successfully.
    """
    pipelines_controller.run_pipelines()
    return {"message": "Pipelines run successfully."}


@app.get("/schemes")
def get_concept_schemes() -> dict[str, list[ConceptScheme]]:
    """Get the concept schemes.

    Returns:
        dict[str, list[ConceptScheme]]: The concept schemes.
    """
    return controller.get_concept_schemes()


@app.get("/schemes/{scheme_name}")
def get_concepts_for_scheme(scheme_name: str) -> dict[str, Union[list[Concept], str]]:
    """Get the concepts for a scheme.

    Args:
        scheme_name (str): The name of the scheme.

    Returns:
        dict[str, Union[list[Concept], str]]: The concepts for the scheme.
            Or an error message if the scheme is not found.
    """
    return controller.get_concepts_for_scheme(concept_scheme_name=scheme_name)


@app.get("/concepts/{concept_name}")
def get_relationships_for_concept(
    concept_name: str,
) -> dict[str, Union[list[Relationship], str]]:
    """Get the relationships for a concept.

    Args:
        concept_name (str): The name of the concept.

    Returns:
        dict[str, Union[list[Relationship], str]]: The relationships for the concept.
            Or an error message if the concept is not found.
    """
    return controller.get_relationships_for_concept(concept_name=concept_name)
