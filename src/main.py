from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.router import router

app = FastAPI(title="Exchange Service")
app.include_router(router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
