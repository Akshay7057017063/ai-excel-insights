from datetime import datetime, timezone
from fastapi import APIRouter
from app import __version__
from app.core.config import get_settings
from app.repositories.db import check_db_connection
from app.schemas.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])
settings = get_settings()


@router.get("", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Returns application health status, version, and external service availability."""
    db_connected = check_db_connection()
    ai_available = bool(settings.AI_API_KEY)
    payment_available = bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)

    overall_status = "healthy" if db_connected else "degraded"

    return HealthResponse(
        status=overall_status,
        version=__version__,
        mongodb_connected=db_connected,
        ai_available=ai_available,
        payment_available=payment_available,
        timestamp=datetime.now(timezone.utc),
    )
