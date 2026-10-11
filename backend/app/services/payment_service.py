import hashlib
import hmac
import json
from typing import Any, Dict, Optional
import httpx
from app.core.config import get_settings
from app.core.logging import logger
from app.models.models import PaymentRecord, SubscriptionDocument
from app.repositories.db import get_db
from app.repositories.user_repo import UserRepository

settings = get_settings()

PLAN_PRICING = {
    "free": {"price_inr": 0, "max_reports": 3, "max_upload_mb": 10, "max_rows": 20000, "max_ai": 15},
    "pro": {"price_inr": 799, "max_reports": 50, "max_upload_mb": 50, "max_rows": 200000, "max_ai": 500},
    "business": {"price_inr": 2499, "max_reports": 500, "max_upload_mb": 100, "max_rows": 1000000, "max_ai": 5000},
}


class PaymentService:
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        self.razorpay_available = bool(self.key_id and self.key_secret)
        self.user_repo = UserRepository()

    @property
    def payments_col(self):
        return get_db()["payments"]

    @property
    def subscriptions_col(self):
        return get_db()["subscriptions"]

    def create_order(self, plan_name: str, user_id: str) -> Dict[str, Any]:
        """Creates a Razorpay order for purchasing or upgrading subscription tier."""
        plan_key = plan_name.lower().strip()
        if plan_key not in PLAN_PRICING:
            return {"error": f"Invalid plan: {plan_name}"}

        plan_info = PLAN_PRICING[plan_key]
        amount_inr = plan_info["price_inr"]
        amount_paise = amount_inr * 100

        if not self.razorpay_available:
            return {
                "error": "payment_not_configured",
                "message": "Payment gateway credentials not configured.",
                "amount_inr": amount_inr,
            }

        url = "https://api.razorpay.com/v1/orders"
        payload = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"usr_{user_id[:8]}_{plan_key}",
            "notes": {"user_id": user_id, "plan": plan_key},
        }

        try:
            with httpx.Client(auth=(self.key_id, self.key_secret), timeout=15.0) as client:
                res = client.post(url, json=payload)
                if res.status_code not in (200, 201):
                    logger.error("Razorpay order creation failed: %d %s", res.status_code, res.text)
                    return {"error": "Failed to initialize payment with provider"}

                order_data = res.json()
                order_id = order_data.get("id")

                # Store pending payment record
                payment_rec = PaymentRecord(
                    user_id=user_id,
                    amount_inr=amount_inr,
                    currency="INR",
                    status="created",
                    provider="razorpay",
                    provider_order_id=order_id,
                )
                self.payments_col.insert_one(payment_rec.to_dict())

                return {
                    "order_id": order_id,
                    "amount_inr": amount_inr,
                    "currency": "INR",
                    "key_id": self.key_id,
                }
        except Exception as exc:
            logger.error("Exception creating Razorpay order: %s", exc)
            return {"error": "Payment service communication error"}

    def verify_payment(self, payment_id: str, order_id: str, signature: str) -> bool:
        """Verifies Razorpay payment signature via HMAC-SHA256."""
        if not self.key_secret:
            return False

        message = f"{order_id}|{payment_id}".encode("utf-8")
        secret_bytes = self.key_secret.encode("utf-8")
        expected = hmac.new(secret_bytes, message, hashlib.sha256).hexdigest()

        return hmac.compare_digest(expected, signature)

    def grant_plan_access(self, user_id: str, plan_name: str, payment_id: Optional[str] = None) -> bool:
        """Promotes user subscription after successful payment verification."""
        plan_key = plan_name.lower().strip()
        # 1. Update User Document
        self.user_repo.update_plan(user_id, plan_key)

        # 2. Update Payment Record if exists
        if payment_id:
            self.payments_col.update_one(
                {"provider_payment_id": payment_id},
                {"$set": {"status": "captured"}},
            )

        # 3. Insert or update Subscription Document
        sub_doc = SubscriptionDocument(
            user_id=user_id,
            plan_id=plan_key,
            status="active",
        )
        self.subscriptions_col.insert_one(sub_doc.to_dict())

        logger.info("Granted plan '%s' to user %s (payment: %s)", plan_key, user_id, payment_id)
        return True

    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Validates webhook signature and processes payment/subscription events idempotently."""
        if not self.webhook_secret:
            return {"processed": False, "error": "Webhook secret not configured"}

        # Verify signature
        expected = hmac.new(self.webhook_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            logger.warning("Invalid webhook signature received.")
            return {"processed": False, "error": "Invalid signature"}

        try:
            event_data = json.loads(payload.decode("utf-8"))
            event_type = event_data.get("event")
            entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = entity.get("order_id")
            payment_id = entity.get("id")
            notes = entity.get("notes", {})
            user_id = notes.get("user_id")
            plan_name = notes.get("plan", "pro")

            if event_type == "payment.captured" and user_id:
                # Idempotency check: see if payment is already recorded as captured
                existing = self.payments_col.find_one({"provider_payment_id": payment_id, "status": "captured"})
                if existing:
                    return {"processed": True, "event_type": event_type, "note": "Already processed"}

                self.grant_plan_access(user_id=user_id, plan_name=plan_name, payment_id=payment_id)
                return {"processed": True, "event_type": event_type}

            return {"processed": True, "event_type": event_type}
        except Exception as exc:
            logger.error("Error handling webhook: %s", exc)
            return {"processed": False, "error": str(exc)}
