import uvicorn
from fastapi.staticfiles import StaticFiles
import uvicorn, os
from fastapi import  Query, Request, WebSocket
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware  # required by google oauth

from api.utils.json_response import JsonResponseDict
from api.v1.routes import api_version_one
from api.utils.settings import settings
from api.v1.routes.flutterwave_webhook import router as webhook_router
from api.v1.routes.company import public_router as company_public

from api.v1.services.notification import websocket_endpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function"""

    yield


app = FastAPI(
    lifespan=lifespan,
    title="Regtech",
    description="A simple API for Regtech",
    version="1.0.0",
)




import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get absolute path
TEMPLATE_DIR = os.path.join(BASE_DIR, "api/core/dependencies/email/templates")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(api_version_one)
app.include_router(webhook_router)
app.include_router(company_public)

@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...)
):
    await websocket_endpoint(websocket, user_id, token)

@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return JsonResponseDict(
        message="Welcome to API", status_code=status.HTTP_200_OK, data={"URL": ""}
    )


from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(router)


STATIC_DIR = "static/profile_images"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
