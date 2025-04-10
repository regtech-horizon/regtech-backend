from fastapi import APIRouter
from api.v1.routes.auth import auth
from api.v1.routes.company import company_router

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(auth)
api_version_one.include_router(company_router)