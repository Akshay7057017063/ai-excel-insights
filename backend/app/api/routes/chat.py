from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.core.logging import logger
from app.core.security import get_current_user_optional
from app.models.models import ConversationMessage
from app.repositories.db import get_db
from app.schemas.schemas import ChatMessage, ChatRequest, ChatResponse
from app.services.ai_service import AIService
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports/{report_id}/chat", tags=["AI Chat"])
report_service = ReportService()
ai_service = AIService()


def get_chat_collection():
    return get_db()["chat_messages"]


@router.post("", response_model=ChatResponse)
def send_chat_message(
    report_id: str,
    request: ChatRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> ChatResponse:
    """Interacts with the AI analyst regarding the analyzed dataset."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    report = report_service.get_report(report_id, user_id=user_id, guest_token=guest_token)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    col = get_chat_collection()

    # Save user message
    user_msg = ConversationMessage(
        report_id=report_id,
        role="user",
        content=request.message,
    )
    col.insert_one(user_msg.to_dict())

    # Build context from report metrics
    context = {
        "dataset_type": report.get("dataset_type", "general"),
        "row_count": report.get("row_count", 0),
        "col_count": report.get("col_count", 0),
        "columns": [c.get("name") for c in report.get("column_info", [])],
        "kpis": report.get("kpis", []),
        "insights": report.get("insights", []),
    }

    # Fetch last few messages for history
    history_cursor = col.find({"report_id": report_id}).sort("timestamp", -1).limit(6)
    history = [{"role": doc.get("role", "user"), "content": doc.get("content", "")} for doc in reversed(list(history_cursor))]

    # Call AI
    ai_result = ai_service.ask(request.message, context=context, conversation_history=history)

    # Save assistant message
    asst_msg = ConversationMessage(
        report_id=report_id,
        role="assistant",
        content=ai_result["answer"],
        sources=ai_result.get("sources", []),
    )
    col.insert_one(asst_msg.to_dict())

    # Suggested followups
    suggestions = ai_service.generate_suggested_questions(
        profile={"columns": {c["name"]: c for c in report.get("column_info", [])}},
        analysis=report.get("analysis_data", {}),
        dataset_type=report.get("dataset_type", "general"),
    )

    return ChatResponse(
        message=ai_result["answer"],
        sources=ai_result.get("sources", []),
        suggested_questions=suggestions[:4],
    )


@router.get("/history", response_model=List[ChatMessage])
def get_chat_history(
    report_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> List[ChatMessage]:
    """Retrieves conversation history for the specified report."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    report = report_service.get_report(report_id, user_id=user_id, guest_token=guest_token)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    col = get_chat_collection()
    cursor = col.find({"report_id": report_id}).sort("timestamp", 1).limit(50)

    messages = []
    for doc in cursor:
        messages.append(ChatMessage(
            role=doc.get("role", "user"),
            content=doc.get("content", ""),
            timestamp=doc.get("timestamp"),
            sources=doc.get("sources", []),
        ))
    return messages


@router.get("/suggestions", response_model=List[str])
def get_suggested_questions(
    report_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    x_guest_token: Optional[str] = Header(None, alias="X-Guest-Token"),
) -> List[str]:
    """Returns AI-recommended analytical questions tailored to this dataset."""
    user_id = current_user["id"] if current_user else None
    guest_token = x_guest_token if not user_id else None

    report = report_service.get_report(report_id, user_id=user_id, guest_token=guest_token)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    return ai_service.generate_suggested_questions(
        profile={"columns": {c["name"]: c for c in report.get("column_info", [])}},
        analysis=report.get("analysis_data", {}),
        dataset_type=report.get("dataset_type", "general"),
    )
