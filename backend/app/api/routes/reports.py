from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from app.core.logging import logger
from app.core.security import get_current_user_optional
from app.repositories.report_repo import ReportRepository
from app.schemas.schemas import ChartSpec, InsightCard, ReportOut, ReportRenameRequest, ReportSummaryOut, StandardResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])
report_service = ReportService()
report_repo = ReportRepository()


@router.get("", response_model=List[ReportSummaryOut])
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> List[ReportSummaryOut]:
    """Retrieves list of reports belonging to the authenticated user or guest session."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    if not user_id and not guest_token:
        return []

    reports = report_repo.get_user_reports(user_id=user_id, guest_token=guest_token, skip=skip, limit=limit)
    summaries = []
    for r in reports:
        summaries.append(ReportSummaryOut(
            id=r["id"],
            name=r.get("name", "Untitled Report"),
            sheet_name=r.get("sheet_name", "Sheet1"),
            status=r.get("status", "completed"),
            created_at=r["created_at"],
            row_count=r.get("row_count", 0),
            col_count=r.get("col_count", 0),
            dataset_type=r.get("dataset_type", "general"),
            insights_count=r.get("insights_count", 0),
            chart_count=r.get("chart_count", 0),
            expires_at=r.get("expires_at"),
        ))
    return summaries


@router.get("/{report_id}", response_model=ReportOut)
def get_report(
    report_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> ReportOut:
    """Retrieves full report details, KPIs, insights, and charts."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    report = report_service.get_report(report_id, user_id=user_id, guest_token=guest_token)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found or access denied.")
    return ReportOut(**report)


@router.get("/{report_id}/insights", response_model=List[InsightCard])
def get_report_insights(
    report_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> List[InsightCard]:
    """Retrieves computed insights for a specific report."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    report = report_service.get_report(report_id, user_id=user_id, guest_token=guest_token)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    return [InsightCard(**ins) for ins in report.get("insights", [])]


@router.get("/{report_id}/charts", response_model=List[ChartSpec])
def get_report_charts(
    report_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> List[ChartSpec]:
    """Retrieves chart specifications for a specific report."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    report = report_service.get_report(report_id, user_id=user_id, guest_token=guest_token)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    return [ChartSpec(**ch) for ch in report.get("charts", [])]


@router.patch("/{report_id}", response_model=StandardResponse[bool])
def rename_report(
    report_id: str,
    req: ReportRenameRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> StandardResponse[bool]:
    """Renames an existing report."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    success = report_repo.rename_report(report_id, req.name, user_id=user_id, guest_token=guest_token)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found or not authorized.")
    return StandardResponse(success=True, message="Report renamed successfully.", data=True)


@router.delete("/{report_id}", response_model=StandardResponse[bool])
def delete_report(
    report_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> StandardResponse[bool]:
    """Deletes a report with ownership validation."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    success = report_repo.delete_report(report_id, user_id=user_id, guest_token=guest_token)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found or not authorized.")
    return StandardResponse(success=True, message="Report deleted successfully.", data=True)


@router.get("/{report_id}/export/pdf")
def export_report_pdf(
    report_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
):
    """Generates and downloads a clean, branded PDF report."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    try:
        pdf_bytes = report_service.export_pdf(report_id, user_id=user_id, guest_token=guest_token)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="report_{report_id[:8]}.pdf"'},
        )
    except Exception as exc:
        logger.error("PDF export error for %s: %s", report_id, exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{report_id}/export/csv")
def export_report_csv(
    report_id: str,
    table: Optional[str] = Query(None, description="Specific table (kpis, trends, categories)"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
):
    """Exports structured metrics as CSV."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    try:
        csv_data = report_service.export_csv(report_id, user_id=user_id, guest_token=guest_token, table_name=table)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="report_{report_id[:8]}_{table or "summary"}.csv"'},
        )
    except Exception as exc:
        logger.error("CSV export error for %s: %s", report_id, exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
