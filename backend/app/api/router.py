from fastapi import APIRouter
from app.api.routes.analysis import router as analysis_router
from app.api.routes.auth import router as auth_router
from app.api.routes.billing import router as billing_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.reports import router as reports_router
from app.api.routes.uploads import router as uploads_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(uploads_router)
api_router.include_router(analysis_router)
api_router.include_router(reports_router)
api_router.include_router(chat_router)
api_router.include_router(billing_router)
