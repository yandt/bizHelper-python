import time

from fastapi import FastAPI, Request, status
from starlette.middleware.gzip import GZipMiddleware


def register_middleware(app: FastAPI) -> None:

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time * 1000)
        return response
