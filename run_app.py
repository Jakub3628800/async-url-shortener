import os

import uvicorn

from shortener.factory import app

if __name__ == "__main__":
    port = os.getenv("APPLICATION_PORT", 8000)
    uvicorn.run(app, host="127.0.0.0", port=port, loop="uvloop")
