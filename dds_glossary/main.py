"""Main entry for the dds_glossary server."""

import argparse
from os import getenv as os_getenv

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from .controllers import GlossaryController
from .routes import router


def create_app() -> FastAPI:
    """Create the FastAPI application object
    Returns:
        FastAPI: the application object
    """
    sentry_sdk.init(
        dsn=os_getenv("SENTRY_DSN"),
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
        "-r",
        dest="f_reload",
        action="store_true",
        help="enable auto-reloading",
        default=False,
    )
    args = parser.parse_args()
    uvicorn.run(
        "dds_glossary.main:create_app",
        reload=args.f_reload,
        host=os_getenv("HOST_IP", "127.0.0.1"),
    )
