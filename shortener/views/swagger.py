import json

from starlette.requests import Request
from starlette.schemas import SchemaGenerator
from starlette.templating import Jinja2Templates


def openapi_schema(request: Request):
    schemas = SchemaGenerator({"openapi": "3.0.0", "info": {"title": "Starlette URL shortener", "version": "1.0"}})
    return schemas.OpenAPIResponse(request=request)


async def swaggerui(request: Request):

    config = {
        "app_name": "Starlette URL shortener",
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
