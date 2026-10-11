import io
from typing import Any, Dict, List, Optional
import openpyxl
import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import app

settings = get_settings()


class MockCursor:
    def __init__(self, docs: List[Dict[str, Any]]):
        self.docs = docs

    def sort(self, field: str, direction: int = 1):
        # basic sort support
        reverse = direction < 0
        self.docs.sort(key=lambda d: d.get(field, 0), reverse=reverse)
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


class MockCollection:
    def __init__(self, name: str):
        self.name = name
        self.docs: List[Dict[str, Any]] = []

    def create_index(self, *args, **kwargs):
        pass

    def insert_one(self, doc: Dict[str, Any]):
        doc_copy = doc.copy()
        if "_id" not in doc_copy:
            doc_copy["_id"] = str(len(self.docs) + 1)
        self.docs.append(doc_copy)

        class Result:
            inserted_id = doc_copy["_id"]

        return Result()

    def find_one(self, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None):
        for doc in self.docs:
            matched = True
            for k, v in query.items():
                if doc.get(k) != v:
                    matched = False
                    break
            if matched:
                return doc.copy()
        return None

    def find(self, query: Optional[Dict[str, Any]] = None):
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
        return MockCursor(matched)

    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]):
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

    def find_one_and_update(self, query: Dict[str, Any], update: Dict[str, Any], return_document=True):
        doc = self.find_one(query)
        if doc:
            inc_vals = update.get("$inc", {})
            for k, delta in inc_vals.items():
                doc[k] = doc.get(k, 0) + delta
            set_vals = update.get("$set", {})
            doc.update(set_vals)
            for item in self.docs:
                if item.get("id") == doc.get("id"):
                    item.update(doc)
            return doc.copy()
        return None

    def delete_one(self, query: Dict[str, Any]):
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

    def delete_many(self, query: Dict[str, Any]):
        count = len(self.docs)
        self.docs = []

        class Res:
            deleted_count = count

        return Res()

    def count_documents(self, query: Dict[str, Any]) -> int:
        return len(list(self.find(query)))


class MockDatabase:
    def __init__(self):
        self.collections: Dict[str, MockCollection] = {}

    def __getitem__(self, name: str) -> MockCollection:
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]

    def command(self, cmd: str):
        return {"ok": 1}


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Provides isolated in-memory MongoDB replacement for deterministic testing."""
    mock_database = MockDatabase()
    import app.repositories.db as db_mod
    import app.repositories.user_repo as u_repo
    import app.repositories.report_repo as r_repo
    import app.services.payment_service as pay_mod
    import app.api.routes.billing as bill_route
    import app.api.routes.chat as chat_route

    db_mod._database = mock_database
    monkeypatch.setattr(db_mod, "get_db", lambda: mock_database)
    monkeypatch.setattr(db_mod, "check_db_connection", lambda: True)
    monkeypatch.setattr(u_repo, "get_db", lambda: mock_database)
    monkeypatch.setattr(r_repo, "get_db", lambda: mock_database)
    monkeypatch.setattr(pay_mod, "get_db", lambda: mock_database)
    monkeypatch.setattr(bill_route, "get_db", lambda: mock_database)
    monkeypatch.setattr(chat_route, "get_db", lambda: mock_database)
    return mock_database


@pytest.fixture
def test_app():
    return app


@pytest.fixture
async def test_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_sales_data():
    return [
        {"Date": "2024-01-15", "Product": "Laptop", "Region": "North", "Amount": 1200.0, "Quantity": 2},
        {"Date": "2024-01-20", "Product": "Mouse", "Region": "South", "Amount": 50.0, "Quantity": 5},
        {"Date": "2024-02-10", "Product": "Monitor", "Region": "North", "Amount": 300.0, "Quantity": 1},
        {"Date": "2024-02-15", "Product": "Laptop", "Region": "East", "Amount": 2400.0, "Quantity": 4},
        {"Date": "2024-03-01", "Product": "Keyboard", "Region": "West", "Amount": 100.0, "Quantity": 2},
        {"Date": "2024-03-12", "Product": "Laptop", "Region": "North", "Amount": 1200.0, "Quantity": 2},
    ]


@pytest.fixture
def sample_xlsx_bytes(sample_sales_data) -> bytes:
    """Creates a valid, in-memory openpyxl XLSX workbook."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "SalesData"

    headers = list(sample_sales_data[0].keys())
    ws.append(headers)

    for row in sample_sales_data:
        ws.append(list(row.values()))

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.fixture
def sample_csv_bytes(sample_sales_data) -> bytes:
    """Creates a valid, in-memory CSV file."""
    df = pd.DataFrame(sample_sales_data)
    return df.to_csv(index=False).encode("utf-8")
