import uvicorn
from fastapi.staticfiles import StaticFiles
import uvicorn, os
from fastapi import  Request
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware  # required by google oauth

from api.utils.json_response import JsonResponseDict
from api.v1.routes import api_version_one
from api.utils.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function"""

    yield


app = FastAPI(
    lifespan=lifespan,
    title="Regtceh",
    description="A simple API for Regtech",
    version="1.0.0",
)




import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get absolute path
TEMPLATE_DIR = os.path.join(BASE_DIR, "api/core/dependencies/email/templates")

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]


app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_version_one)


@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return JsonResponseDict(
        message="Welcome to API", status_code=status.HTTP_200_OK, data={"URL": ""}
    )




STATIC_DIR = "static/profile_images"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
