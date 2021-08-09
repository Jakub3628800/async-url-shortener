import uvicorn
import asyncio
from shortener.factory import init_app

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    uvicorn.run(app, host="0.0.0.0", port=8000)
