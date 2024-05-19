"""Main entry for the dds_glossary server."""

import argparse
from http import HTTPStatus
from os import getenv

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from . import __version__
from .controllers import GlossaryController
from .routes import router


def create_app() -> FastAPI:
    """Create the FastAPI application object
    Returns:
        FastAPI: the application object
    """

    SENTRY_DSN = getenv("SENTRY_DSN")

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
    app.state.controller = GlossaryController()
    app.state.templates = Jinja2Templates(directory="templates")
    app.include_router(router)
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DDS Glossary")
    parser.add_argument(
        "-r", dest="f_reload", action="store_true", help="enable auto-reloading"
    )
    args = parser.parse_args()
    uvicorn.run("dds_glossary.main:create_app", reload=args.f_reload, host="0.0.0.0")
