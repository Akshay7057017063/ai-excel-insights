from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.models.models import ReportDocument
from app.repositories.db import get_db


class ReportRepository:
    def __init__(self):
        pass

    @property
    def collection(self):
        return get_db()["reports"]

    def create_report(
        self,
        file_id: str,
        name: str,
        sheet_name: str,
        user_id: Optional[str] = None,
        guest_token: Optional[str] = None,
        row_count: int = 0,
        col_count: int = 0,
        column_info: Optional[List[Dict[str, Any]]] = None,
        dataset_type: str = "general",
        kpis: Optional[List[Dict[str, Any]]] = None,
        insights: Optional[List[Dict[str, Any]]] = None,
        charts: Optional[List[Dict[str, Any]]] = None,
        analysis_data: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None,
        status: str = "completed",
    ) -> Dict[str, Any]:
        """Creates and stores a report document."""
        report = ReportDocument(
            user_id=user_id,
            guest_token=guest_token,
            file_id=file_id,
            name=name,
            sheet_name=sheet_name,
            status=status,
            row_count=row_count,
            col_count=col_count,
            column_info=column_info or [],
            dataset_type=dataset_type,
            insights_count=len(insights) if insights else 0,
            chart_count=len(charts) if charts else 0,
            kpis=kpis or [],
            insights=insights or [],
            charts=charts or [],
            analysis_data=analysis_data or {},
            expires_at=expires_at,
        )
        doc = report.to_dict()
        self.collection.insert_one(doc)
        return doc

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Fetch report by its ID."""
        doc = self.collection.find_one({"id": report_id})
        if doc and "_id" in doc:
            doc.pop("_id", None)
        return doc

    def get_user_reports(
        self,
        user_id: Optional[str] = None,
        guest_token: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List reports belonging to a user or guest session."""
        query: Dict[str, Any] = {}
        if user_id:
            query["user_id"] = user_id
        elif guest_token:
            query["guest_token"] = guest_token
        else:
            return []

        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        results = []
        for doc in cursor:
            if "_id" in doc:
                doc.pop("_id", None)
            results.append(doc)
        return results

    def update_report_status(
        self,
        report_id: str,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update report status and optionally its computed insights and charts."""
        update_fields: Dict[str, Any] = {"status": status}
        if error_message:
            update_fields["error_message"] = error_message
        if data:
            update_fields.update(data)

        res = self.collection.update_one({"id": report_id}, {"$set": update_fields})
        return res.modified_count > 0

    def rename_report(self, report_id: str, name: str, user_id: Optional[str] = None, guest_token: Optional[str] = None) -> bool:
        """Rename an existing report."""
        query: Dict[str, Any] = {"id": report_id}
        if user_id:
            query["user_id"] = user_id
        elif guest_token:
            query["guest_token"] = guest_token

        res = self.collection.update_one(query, {"$set": {"name": name}})
        return res.modified_count > 0

    def delete_report(
        self,
        report_id: str,
        user_id: Optional[str] = None,
        guest_token: Optional[str] = None,
    ) -> bool:
        """Delete report checking ownership."""
        query: Dict[str, Any] = {"id": report_id}
        if user_id:
            query["user_id"] = user_id
        elif guest_token:
            query["guest_token"] = guest_token

        res = self.collection.delete_one(query)
        return res.deleted_count > 0

    def cleanup_expired_reports(self) -> int:
        """Remove reports that have passed their expires_at date."""
        now = datetime.now(timezone.utc)
        res = self.collection.delete_many({
            "expires_at": {"$ne": None, "$lt": now}
        })
        return res.deleted_count
