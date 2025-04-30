from fastapi import APIRouter
from api.v1.routes.auth import auth
from api.v1.routes.company import company_router
from api.v1.routes.user import user_router
from api.v1.routes.dashboard import dashboard_router
from api.v1.routes.notification import router as notification_router
# from api.v1.routes.user import user_router

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(auth)
api_version_one.include_router(company_router)
api_version_one.include_router(user_router)
api_version_one.include_router(dashboard_router)
api_version_one.include_router(notification_router)
# api_version_one.include_router(user_router)