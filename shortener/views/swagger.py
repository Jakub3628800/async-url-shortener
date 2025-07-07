import json

from starlette.requests import Request
from starlette.responses import Response
from starlette.schemas import SchemaGenerator
from starlette.templating import Jinja2Templates
from starlette.templating import _TemplateResponse as TemplateResponse

APP_NAME = "Async URL shortener"


def openapi_schema(request: Request) -> Response:
    schemas = SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": APP_NAME, "version": "1.0"}}
    )
    return schemas.OpenAPIResponse(request=request)


async def swaggerui(request: Request) -> TemplateResponse:
    config = {
        "app_name": APP_NAME,
        "dom_id": "#swagger-ui",
        "url": "/_schema",
        "layout": "StandaloneLayout",
        "deepLinking": True,
    }

    fields = {
        "base_url": "/static",
        "app_name": config.pop("app_name"),
        "config_json": json.dumps(config),
        "request": request,
    }

    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("index.html", fields)
