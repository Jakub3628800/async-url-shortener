from starlette.schemas import SchemaGenerator
from starlette.templating import Jinja2Templates
import json


schemas = SchemaGenerator({"openapi": "3.0.0", "info": {"title": "Starlette URL shortener", "version": "1.0"}})
templates = Jinja2Templates(directory="templates")


def openapi_schema(request):
    return schemas.OpenAPIResponse(request=request)


async def swaggerui(request):

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
    return templates.TemplateResponse("index.html", fields)
