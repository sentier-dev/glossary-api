"""Main entry for the dds_glossary server."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .controllers import GlossaryController
from .database import init_engine

app = FastAPI()
engine = init_engine()
controller = GlossaryController(engine)


@app.get("/schemes")
def get_concept_schemes() -> JSONResponse:
    """Get the concept schemes.

    Returns:
        JSONResponse: The concept schemes.
    """
    return controller.get_concept_schemes()
