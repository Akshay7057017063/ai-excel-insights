from typing import Any, Optional
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

_mongo_client: Optional[MongoClient] = None
class InMemoryCursor:
    def __init__(self, docs: list):
        self.docs = list(docs)

    def sort(self, field: str, direction: int = 1):
        reverse = direction < 0
        self.docs.sort(key=lambda d: str(d.get(field, "")), reverse=reverse)
        return self

    def skip(self, n: int):
        self.docs = self.docs[n:]
        return self

    def limit(self, n: int):
        self.docs = self.docs[:n]
        return self

    def __iter__(self):
        return iter(self.docs)

    def __list__(self):
        return self.docs


class InMemoryCollection:
    def __init__(self, name: str):
        self.name = name
        self.docs = []

    def create_index(self, *args, **kwargs):
        pass

    def insert_one(self, doc: dict):
        doc_copy = doc.copy()
        if "_id" not in doc_copy:
            doc_copy["_id"] = str(len(self.docs) + 1)
        self.docs.append(doc_copy)

        class Result:
            inserted_id = doc_copy["_id"]

        return Result()

    def find_one(self, query: dict, projection=None):
        for doc in self.docs:
            matched = True
            for k, v in query.items():
                if doc.get(k) != v:
                    matched = False
                    break
            if matched:
                return doc.copy()
        return None

    def find(self, query=None):
        query = query or {}
        matched = []
        for doc in self.docs:
            ok = True
            for k, v in query.items():
                if doc.get(k) != v:
                    ok = False
                    break
            if ok:
                matched.append(doc.copy())
        return InMemoryCursor(matched)

    def update_one(self, query: dict, update: dict):
        set_vals = update.get("$set", {})
        doc = self.find_one(query)
        if doc:
            for item in self.docs:
                if item.get("id") == doc.get("id") or item.get("_id") == doc.get("_id"):
                    item.update(set_vals)
                    break

            class Res:
                modified_count = 1

            return Res()

        class ZeroRes:
            modified_count = 0

        return ZeroRes()

    def find_one_and_update(self, query: dict, update: dict, return_document=True):
        doc = self.find_one(query)
        if doc:
            inc_vals = update.get("$inc", {})
            for k, delta in inc_vals.items():
                doc[k] = doc.get(k, 0) + delta
            set_vals = update.get("$set", {})
            doc.update(set_vals)
            for item in self.docs:
                if item.get("id") == doc.get("id") or item.get("_id") == doc.get("_id"):
                    item.update(doc)
            return doc.copy()
        return None

    def delete_one(self, query: dict):
        for i, doc in enumerate(self.docs):
            matched = True
            for k, v in query.items():
                if doc.get(k) != v:
                    matched = False
                    break
            if matched:
                self.docs.pop(i)

                class Res:
                    deleted_count = 1

                return Res()

        class ZeroRes:
            deleted_count = 0

        return ZeroRes()

    def delete_many(self, query: dict):
        count = len(self.docs)
        self.docs = []

        class Res:
            deleted_count = count

        return Res()

    def count_documents(self, query: dict) -> int:
        return len(list(self.find(query)))


class InMemoryDatabase:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name: str) -> InMemoryCollection:
        if name not in self.collections:
            self.collections[name] = InMemoryCollection(name)
        return self.collections[name]

    def command(self, cmd: str):
        return {"ok": 1}


_database = None
_in_memory_db = InMemoryDatabase()


def get_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        try:
            _mongo_client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=1000,
                connectTimeoutMS=1000,
            )
        except Exception as exc:
            logger.error("Failed to create MongoClient: %s", exc)
            raise
    return _mongo_client


def get_db():
    global _database
    if _database is None:
        try:
            client = get_client()
            client.admin.command("ping")
            _database = client[settings.MONGODB_DATABASE]
        except Exception as exc:
            logger.info("MongoDB unavailable (%s), running with in-memory development database.", exc)
            _database = _in_memory_db
    return _database


def check_db_connection() -> bool:
    try:
        client = get_client()
        client.admin.command("ping")
        return True
    except Exception:
        return False


def init_db() -> None:
    """Initialize database indexes on startup."""
    try:
        db = get_db()
        # Ping to check liveness
        db.command("ping")

        # Indexes for users
        users = db["users"]
        users.create_index([("email", ASCENDING)], unique=True)
        users.create_index([("id", ASCENDING)], unique=True)

        # Indexes for reports
        reports = db["reports"]
        reports.create_index([("id", ASCENDING)], unique=True)
        reports.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        reports.create_index([("guest_token", ASCENDING)])
        reports.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)

        # Indexes for usage records
        usage = db["usage"]
        usage.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])

        # Indexes for payments
        payments = db["payments"]
        payments.create_index([("id", ASCENDING)], unique=True)
        payments.create_index([("user_id", ASCENDING)])
        payments.create_index([("provider_order_id", ASCENDING)])

        # Indexes for chat messages
        chats = db["chat_messages"]
        chats.create_index([("report_id", ASCENDING), ("timestamp", ASCENDING)])

        logger.info("Successfully initialized MongoDB collections and indexes.")
    except Exception as exc:
        logger.warning("MongoDB connection / index setup deferred or failed: %s", exc)


def close_db() -> None:
    global _mongo_client, _database
    if _mongo_client is not None:
        try:
            _mongo_client.close()
            logger.info("Closed MongoDB connection.")
        except Exception as exc:
            logger.error("Error closing MongoDB client: %s", exc)
        finally:
            _mongo_client = None
            _database = None
