import os
from typing import Union

import uvicorn

from shortener.factory import app

if __name__ == "__main__":
    port: Union[str, int] = os.getenv("APPLICATION_PORT", 8000)
    uvicorn.run(app, host="0.0.0.0", port=int(port), loop="uvloop")
