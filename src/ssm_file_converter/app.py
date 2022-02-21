from fastapi import FastAPI

from ssm_file_converter.apis import api_router
from ssm_file_converter.config import settings


def include_router(app):
    app.include_router(api_router)


def start_application():
    app = FastAPI(
        title=settings.project_name,
        version=settings.project_version
    )
    include_router(app)
    return app


app = start_application()
