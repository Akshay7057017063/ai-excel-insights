import io
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
import uuid
import zipfile

import chardet
import numpy as np
import openpyxl
import pandas as pd

from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

XLSX_MAGIC = b"PK\x03\x04"
XLS_MAGIC = b"\xD0\xCF\x11\xE0"
MAX_ZIP_RATIO = 100.0  # Max compression ratio allowed to prevent zip bombs
MAX_UNCOMPRESSED_BYTES = 500 * 1024 * 1024  # 500 MB max expanded size


class FileParserError(Exception):
    """Raised when file validation or parsing fails."""
    pass


class FileParser:
    def __init__(self):
        self.upload_dir: Path = settings.upload_path

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitizes filename and removes any directory traversal components."""
        basename = os.path.basename(filename)
        # Strip path traversal and weird chars
        clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', basename)
        if not clean_name:
            clean_name = "upload.xlsx"
        return clean_name

    def _detect_file_type(self, file_bytes: bytes, filename: str) -> str:
        """Detect file type via magic bytes; verify CSV has non-binary text content."""
        if not file_bytes:
            raise FileParserError("Uploaded file is empty.")

        if file_bytes.startswith(XLSX_MAGIC):
            return "xlsx"
        elif file_bytes.startswith(XLS_MAGIC):
            return "xls"

        # Check for plain text / CSV
        # If file has null bytes or high non-printable chars in the first 1024 bytes, reject
        sample = file_bytes[:4096]
        if b"\x00" in sample:
            raise FileParserError("Invalid file type: binary content detected with unsupported format.")

        # Try to detect if it looks like text / delimited data
        lower_name = filename.lower()
        if lower_name.endswith(".csv") or lower_name.endswith(".txt") or lower_name.endswith(".tsv"):
            return "csv"

        # If extension claimed xlsx/xls but magic bytes mismatched
        if lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
            raise FileParserError("File contents do not match Excel file signature.")

        # Default fallback if text
        return "csv"

    def _verify_zip_safety(self, file_bytes: bytes) -> None:
        """Inspect zip archive to protect against zip bomb attacks."""
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes), "r") as zf:
                total_uncompressed = 0
                compressed_size = len(file_bytes)
                for info in zf.infolist():
                    total_uncompressed += info.file_size
                    if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
                        raise FileParserError("File exceeds maximum uncompressed size limit (potential zip bomb).")

                if compressed_size > 0:
                    ratio = total_uncompressed / compressed_size
                    if ratio > MAX_ZIP_RATIO:
                        raise FileParserError(
                            f"Suspicious compression ratio ({ratio:.1f}x) exceeds safe limits."
                        )
        except zipfile.BadZipFile:
            raise FileParserError("Corrupted or invalid Excel (ZIP) archive.")

    def validate_and_save(self, file_bytes: bytes, filename: str, max_bytes: Optional[int] = None) -> Dict[str, Any]:
        """Validates file signature, size, and zip safety; saves to uploads directory."""
        limit = max_bytes or settings.max_upload_bytes
        size_bytes = len(file_bytes)

        if size_bytes == 0:
            raise FileParserError("Empty file uploaded.")

        if size_bytes > limit:
            raise FileParserError(
                f"File size ({size_bytes / (1024 * 1024):.2f}MB) exceeds maximum allowed limit ({limit / (1024 * 1024):.2f}MB)."
            )

        sanitized_name = self._sanitize_filename(filename)
        file_type = self._detect_file_type(file_bytes, sanitized_name)

        if file_type == "xlsx":
            self._verify_zip_safety(file_bytes)

        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{sanitized_name}"
        safe_path = self.upload_dir / safe_filename

        with open(safe_path, "wb") as f:
            f.write(file_bytes)

        logger.info("Saved upload %s (%s, %d bytes) to %s", file_id, file_type, size_bytes, safe_path)

        return {
            "file_id": file_id,
            "original_name": sanitized_name,
            "safe_path": str(safe_path),
            "file_type": file_type,
            "size_bytes": size_bytes,
        }

    def _get_file_path(self, file_id: str) -> Path:
        """Finds safe file on disk by file_id prefix."""
        # Sanitize file_id to prevent path traversal
        clean_id = re.sub(r'[^a-zA-Z0-9-]', '', file_id)
        matches = list(self.upload_dir.glob(f"{clean_id}_*"))
        if not matches:
            raise FileParserError(f"File not found for ID: {clean_id}")
        return matches[0]

    def get_sheets(self, file_id: str) -> List[Dict[str, Any]]:
        """Returns list of {name, row_count, col_count} for the given file."""
        file_path = self._get_file_path(file_id)
        ext = file_path.suffix.lower()

        if ext in [".xlsx", ".xlsm"]:
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            sheets = []
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                sheets.append({
                    "name": sheet_name,
                    "row_count": ws.max_row or 0,
                    "col_count": ws.max_column or 0,
                })
            wb.close()
            return sheets
        elif ext == ".xls":
            import xlrd
            wb = xlrd.open_workbook(file_path, on_demand=True)
            sheets = []
            for sheet_name in wb.sheet_names():
                sh = wb.sheet_by_name(sheet_name)
                sheets.append({
                    "name": sheet_name,
                    "row_count": sh.nrows,
                    "col_count": sh.ncols,
                })
            wb.release_resources()
            return sheets
        else:
            # CSV / text file - single sheet
            df = self.load_dataframe(file_id, sheet_name=None, max_rows=settings.MAX_ROWS)
            return [{
                "name": "Sheet1",
                "row_count": int(len(df)),
                "col_count": int(len(df.columns)),
            }]

    def load_dataframe(self, file_id: str, sheet_name: Optional[str] = None, max_rows: Optional[int] = None) -> pd.DataFrame:
        """Loads a clean pandas DataFrame from disk."""
        file_path = self._get_file_path(file_id)
        limit = max_rows or settings.MAX_ROWS
        ext = file_path.suffix.lower()

        if ext in [".xlsx", ".xlsm"]:
            target_sheet = sheet_name or 0
            df = pd.read_excel(file_path, sheet_name=target_sheet, nrows=limit, engine="openpyxl")
        elif ext == ".xls":
            target_sheet = sheet_name or 0
            df = pd.read_excel(file_path, sheet_name=target_sheet, nrows=limit, engine="xlrd")
        else:
            # CSV: Detect encoding
            with open(file_path, "rb") as f:
                raw_head = f.read(65536)
            detected = chardet.detect(raw_head)
            encoding = detected.get("encoding") or "utf-8"

            try:
                df = pd.read_csv(file_path, nrows=limit, encoding=encoding)
            except Exception:
                # Fallback to latin-1
                df = pd.read_csv(file_path, nrows=limit, encoding="latin-1")

        # Standardize column names (strip whitespace, ensure string)
        df.columns = [str(col).strip() if col is not None else f"Column_{i}" for i, col in enumerate(df.columns)]
        return df

    def get_preview(
        self,
        file_id: str,
        sheet_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Returns paginated preview rows and column metadata."""
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        df = self.load_dataframe(file_id, sheet_name=sheet_name)
        total_rows = len(df)
        columns = [str(c) for c in df.columns]

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        subset = df.iloc[start_idx:end_idx]

        # Convert to JSON-safe dictionary records
        records = []
        for _, row in subset.iterrows():
            clean_row: Dict[str, Any] = {}
            for col in columns:
                val = row[col]
                if pd.isna(val) or val is None or val is np.nan:
                    clean_row[col] = None
                elif isinstance(val, (pd.Timestamp, np.datetime64)):
                    clean_row[col] = str(val)
                elif isinstance(val, (int, np.integer)):
                    clean_row[col] = int(val)
                elif isinstance(val, (float, np.floating)):
                    clean_row[col] = round(float(val), 4)
                else:
                    clean_row[col] = str(val)
            records.append(clean_row)

        resolved_sheet = sheet_name or "Sheet1"
        return {
            "columns": columns,
            "rows": records,
            "total_rows": total_rows,
            "page": page,
            "page_size": page_size,
            "sheet_name": resolved_sheet,
        }

    def delete_file(self, file_id: str) -> bool:
        """Securely deletes file from disk."""
        try:
            file_path = self._get_file_path(file_id)
            if file_path.exists():
                file_path.unlink()
                logger.info("Deleted file %s", file_path)
                return True
        except Exception as exc:
            logger.warning("Error deleting file %s: %s", file_id, exc)
        return False
