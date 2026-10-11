from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from app.core.logging import logger
from app.core.security import get_current_user
from app.repositories.db import get_db
from app.schemas.schemas import CheckoutRequest, CheckoutResponse, PlanOut, StandardResponse, SubscriptionOut, VerifyPaymentRequest
from app.services.payment_service import PLAN_PRICING, PaymentService

router = APIRouter(tags=["Billing & Subscriptions"])
payment_service = PaymentService()


@router.get("/billing/plans", response_model=List[PlanOut])
def get_plans() -> List[PlanOut]:
    """Lists available subscription plans and their feature allowances."""
    plans = [
        PlanOut(
            id="free",
            name="Free Tier",
            price_inr=0,
            max_reports_per_month=PLAN_PRICING["free"]["max_reports"],
            max_upload_mb=PLAN_PRICING["free"]["max_upload_mb"],
            max_rows=PLAN_PRICING["free"]["max_rows"],
            max_ai_questions=PLAN_PRICING["free"]["max_ai"],
            features=["3 reports / month", "Basic KPI synthesis", "Standard charts", "Community support"],
        ),
        PlanOut(
            id="pro",
            name="Pro Analyst",
            price_inr=PLAN_PRICING["pro"]["price_inr"],
            max_reports_per_month=PLAN_PRICING["pro"]["max_reports"],
            max_upload_mb=PLAN_PRICING["pro"]["max_upload_mb"],
            max_rows=PLAN_PRICING["pro"]["max_rows"],
            max_ai_questions=PLAN_PRICING["pro"]["max_ai"],
            features=["50 reports / month", "AI Assistant (500 questions)", "Full PDF & CSV exports", "Priority compute"],
        ),
        PlanOut(
            id="business",
            name="Business Enterprise",
            price_inr=PLAN_PRICING["business"]["price_inr"],
            max_reports_per_month=PLAN_PRICING["business"]["max_reports"],
            max_upload_mb=PLAN_PRICING["business"]["max_upload_mb"],
            max_rows=PLAN_PRICING["business"]["max_rows"],
            max_ai_questions=PLAN_PRICING["business"]["max_ai"],
            features=["500 reports / month", "Unlimited AI querying", "Custom KPI formulas", "Dedicated account rep"],
        ),
    ]
    return plans


@router.post("/billing/checkout", response_model=CheckoutResponse)
def checkout_plan(
    req: CheckoutRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> CheckoutResponse:
    """Creates a Razorpay payment order for upgrading subscription plan."""
    order_res = payment_service.create_order(req.plan_name, current_user["id"])
    if "error" in order_res and order_res["error"] != "payment_not_configured":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=order_res["error"])

    return CheckoutResponse(
        order_id=order_res.get("order_id"),
        amount_inr=order_res.get("amount_inr", 0),
        currency=order_res.get("currency", "INR"),
        key_id=order_res.get("key_id"),
        error=order_res.get("error"),
    )


@router.post("/billing/verify", response_model=StandardResponse[bool])
def verify_payment(
    req: VerifyPaymentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StandardResponse[bool]:
    """Verifies payment signature from Razorpay and promotes the user account."""
    valid = payment_service.verify_payment(
        payment_id=req.razorpay_payment_id,
        order_id=req.razorpay_order_id,
        signature=req.razorpay_signature,
    )
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed: invalid HMAC signature.",
        )

    payment_service.grant_plan_access(
        user_id=current_user["id"],
        plan_name=req.plan_name,
        payment_id=req.razorpay_payment_id,
    )

    return StandardResponse(success=True, message=f"Successfully upgraded to {req.plan_name} plan.", data=True)


@router.post("/billing/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None, alias="X-Razorpay-Signature"),
):
    """Processes server-to-server Razorpay webhook events securely."""
    payload = await request.body()
    result = payment_service.handle_webhook(payload, x_razorpay_signature or "")
    if not result.get("processed"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Webhook processing failed"))
    return {"status": "ok", "details": result}


@router.get("/subscriptions/me", response_model=SubscriptionOut)
def get_my_subscription(current_user: Dict[str, Any] = Depends(get_current_user)) -> SubscriptionOut:
    """Returns active subscription details for current user."""
    subs_col = get_db()["subscriptions"]
    sub = subs_col.find_one({"user_id": current_user["id"], "status": "active"})

    if not sub:
        return SubscriptionOut(
            id="sub_free",
            user_id=current_user["id"],
            plan_id="free",
            status="active",
            start_date=current_user.get("created_at") or current_user.get("timestamp"),
            end_date=None,
        )

    return SubscriptionOut(
        id=sub["id"],
        user_id=sub["user_id"],
        plan_id=sub.get("plan_id", "free"),
        status=sub.get("status", "active"),
        start_date=sub["start_date"],
        end_date=sub.get("end_date"),
    )
