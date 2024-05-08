"""Main entry for the dds_glossary server."""

from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .controllers import GlossaryController

app = FastAPI()
controller = GlossaryController()


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
