import json

from starlette.requests import Request
from starlette.responses import Response
from starlette.schemas import SchemaGenerator
from starlette.templating import Jinja2Templates

APP_NAME = "Async URL shortener"


def openapi_schema(request: Request) -> Response:
    schemas = SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": APP_NAME, "version": "1.0"}}
    )
    return schemas.OpenAPIResponse(request=request)


async def swaggerui(request: Request) -> Response:
    config = {
        "app_name": APP_NAME,
        "dom_id": "#swagger-ui",
        "url": "/_schema",
        "layout": "StandaloneLayout",
        "deepLinking": True,
    }

    fields = {
        # Some fields are used directly in template
        "base_url": "/static",
        "app_name": config.pop("app_name"),
        # Rest are just serialized into json string for inclusion in the .js file
        "config_json": json.dumps(config),
        "request": request,
    }

    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("index.html", fields)
