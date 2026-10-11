from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.core.logging import logger
from app.core.security import get_current_user_optional
from app.schemas.schemas import AnalysisRequest, AnalysisStatus
from app.services.report_service import ReportService

router = APIRouter(prefix="/analysis", tags=["Analysis"])
report_service = ReportService()


@router.post("/{file_id}/run", response_model=AnalysisStatus, status_code=status.HTTP_202_ACCEPTED)
def run_analysis(
    file_id: str,
    request: AnalysisRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> AnalysisStatus:
    """Executes profiling, analysis, KPI synthesis, insights, and charts for an uploaded file."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    try:
        report = report_service.create_report(
            file_id=file_id,
            sheet_name=request.sheet_name,
            user_id=user_id,
            guest_token=guest_token,
            name=request.name,
        )
        return AnalysisStatus(
            report_id=report["id"],
            status="completed",
            progress=100,
            message="Analysis completed successfully.",
        )
    except Exception as exc:
        logger.error("Failed to run analysis on file %s: %s", file_id, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis failed: {str(exc)}",
        )


@router.get("/{report_id}/status", response_model=AnalysisStatus)
def get_analysis_status(
    report_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> AnalysisStatus:
    """Checks the computation status of a report analysis."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    report = report_service.get_report(report_id, user_id=user_id, guest_token=guest_token)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    status_str = report.get("status", "completed")
    progress = 100 if status_str == "completed" else (0 if status_str == "failed" else 50)
    msg = report.get("error_message") or ("Analysis ready." if status_str == "completed" else "Processing dataset.")

    return AnalysisStatus(
        report_id=report["id"],
        status=status_str,
        progress=progress,
        message=msg,
    )
