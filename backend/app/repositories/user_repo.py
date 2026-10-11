from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.core.logging import logger
from app.core.security import hash_password
from app.models.models import UserDocument
from app.repositories.db import get_db


class UserRepository:
    def __init__(self):
        pass

    @property
    def collection(self):
        return get_db()["users"]

    @property
    def usage_collection(self):
        return get_db()["usage"]

    def create_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Creates a new user record with hashed password."""
        hashed = hash_password(password)
        user = UserDocument(
            email=email.strip().lower(),
            hashed_password=hashed,
            name=name.strip(),
            plan="free",
        )
        user_dict = user.to_dict()
        self.collection.insert_one(user_dict)
        return user_dict

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Finds user by email address."""
        return self.collection.find_one({"email": email.strip().lower()})

    def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Finds user by user ID."""
        return self.collection.find_one({"id": user_id})

    def update_plan(self, user_id: str, plan_name: str) -> bool:
        """Updates user plan."""
        result = self.collection.update_one(
            {"id": user_id},
            {"$set": {"plan": plan_name}},
        )
        return result.modified_count > 0

    def increment_usage(self, user_id: str) -> int:
        """Increments total usage counter for user."""
        res = self.collection.find_one_and_update(
            {"id": user_id},
            {"$inc": {"usage_count": 1}},
            return_document=True,
        )
        return res.get("usage_count", 0) if res else 0

    def get_usage_this_month(self, user_id: str) -> int:
        """Counts actions performed by user in the current calendar month."""
        now = datetime.now(timezone.utc)
        first_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        count = self.usage_collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": first_of_month},
        })
        return count
