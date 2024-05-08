"""Main entry for the dds_glossary server."""

from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .controllers import GlossaryController
from .database import get_concept_schemes as _get_concept_schemes
from .database import init_engine

app = FastAPI()
engine = init_engine()
controller = GlossaryController(engine)


@app.post("/init_datasets")
def init_datasets() -> JSONResponse:
    """Initialize the datasets.

    Returns:
        JSONResponse: The status of the init request.
    """
    saved_datasets, failed_datasets = controller.init_datasets()
    return JSONResponse(
        content={
            "saved_datasets": saved_datasets,
            "failed_datasets": failed_datasets,
        },
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )


@app.get("/schemes")
def get_concept_schemes() -> JSONResponse:
    """
    Returns all the saved concept schemes.

    Returns:
        JSONResponse: {
            "concept_schemes": list[ConceptScheme]: The concept schemes.
        }
    """
    return JSONResponse(
        content={"concept_schemes": _get_concept_schemes(engine)},
        media_type="application/json",
        status_code=HTTPStatus.OK,
    )
