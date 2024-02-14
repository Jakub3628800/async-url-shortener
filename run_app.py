import os

import uvicorn

from shortener.factory import app
from shortener_fastapi.main import app as app_fastapi  # noqa: F401

if __name__ == "__main__":
    port = os.getenv("APPLICATION_PORT", 8000)
    uvicorn.run(app, host="0.0.0.0", port=port, loop="uvloop")
