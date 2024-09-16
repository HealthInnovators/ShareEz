import os

from fastapi.openapi.utils import get_openapi

VERSION = os.getenv("VERSION", None)
COMMIT_SHA = os.getenv("COMMIT_SHA", None)

ShareEz_DESCRIPTION = """
See the full [docs here](https://ShareEz.readthedocs.io/en/latest/)
"""

ShareEz_TAGS = [
    {
        "name": "Datasets",
        "description": "Manage dataset upload and querying.",
    },
    {
        "name": "Schema",
        "description": "Manage schema generation and upload.",
    },
    {
        "name": "Client",
        "description": "Manage clients.",
    },
    {
        "name": "User",
        "description": "Manage users.",
    },
    {
        "name": "Permissions",
        "description": "Manage permissions.",
    },
    {
        "name": "Protected Domains",
        "description": "Manage protected domains",
    },
    {
        "name": "Status",
        "description": "Shows current status of application, version and commit sha.",
    },
    {
        "name": "Info",
        "description": "Shows the project information including description and contact links.",
    },
]


def custom_openapi_docs_generator(app):
    def custom_openapi_docs():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="ShareEz",
            version=VERSION if VERSION is not None else "DEV",
            description=ShareEz_DESCRIPTION,
            routes=app.routes,
            tags=ShareEz_TAGS,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi_docs
