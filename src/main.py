from fastapi import FastAPI

from src.router import router

app = FastAPI(title="Exchange Service")
app.include_router(router)
