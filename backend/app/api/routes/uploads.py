import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from app.core.logging import logger
from app.core.security import get_current_user_optional
from app.schemas.schemas import PreviewResponse, SheetInfo, StandardResponse, UploadResponse
from app.services.file_parser import FileParser, FileParserError

router = APIRouter(prefix="/uploads", tags=["Uploads"])
file_parser = FileParser()


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
) -> UploadResponse:
    """Uploads, scans, and parses an Excel or CSV file. Issues a guest session token if unauthenticated."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file filename provided.")

    try:
        content = await file.read()
        save_info = file_parser.validate_and_save(content, file.filename)
        sheets_data = file_parser.get_sheets(save_info["file_id"])

        sheets = [SheetInfo(**s) for s in sheets_data]

        guest_token = None
        if not current_user:
            guest_token = str(uuid.uuid4())

        return UploadResponse(
            file_id=save_info["file_id"],
            filename=save_info["original_name"],
            size_bytes=save_info["size_bytes"],
            sheets=sheets,
            guest_token=guest_token,
        )
    except FileParserError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected upload error: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process uploaded file.")


@router.get("/{file_id}/sheets", response_model=List[SheetInfo])
def list_sheets(file_id: str) -> List[SheetInfo]:
    """Retrieves metadata of all available sheets within the uploaded spreadsheet."""
    try:
        sheets_data = file_parser.get_sheets(file_id)
        return [SheetInfo(**s) for s in sheets_data]
    except FileParserError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.error("Error reading sheets for %s: %s", file_id, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to inspect spreadsheet sheets.")


@router.get("/{file_id}/preview", response_model=PreviewResponse)
def get_file_preview(
    file_id: str,
    sheet_name: Optional[str] = Query(None, description="Target sheet name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> PreviewResponse:
    """Returns paginated preview rows and columns for a specific worksheet."""
    try:
        preview_data = file_parser.get_preview(
            file_id=file_id,
            sheet_name=sheet_name,
            page=page,
            page_size=page_size,
        )
        return PreviewResponse(**preview_data)
    except FileParserError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.error("Error generating preview for %s: %s", file_id, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate worksheet preview.")


@router.delete("/{file_id}", response_model=StandardResponse[bool])
def delete_file(file_id: str) -> StandardResponse[bool]:
    """Deletes uploaded file from server storage."""
    success = file_parser.delete_file(file_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found or already deleted.")
    return StandardResponse(success=True, message="File successfully deleted.", data=True)
