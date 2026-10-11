import io
import openpyxl
import pytest
from app.services.file_parser import FileParser, FileParserError


def test_valid_xlsx_upload_accepted(sample_xlsx_bytes):
    parser = FileParser()
    res = parser.validate_and_save(sample_xlsx_bytes, "sales_report.xlsx")
    assert res["file_id"] is not None
    assert res["file_type"] == "xlsx"
    assert res["size_bytes"] == len(sample_xlsx_bytes)
    assert res["original_name"] == "sales_report.xlsx"

    # Cleanup
    parser.delete_file(res["file_id"])


def test_valid_csv_upload_accepted(sample_csv_bytes):
    parser = FileParser()
    res = parser.validate_and_save(sample_csv_bytes, "quarterly_data.csv")
    assert res["file_id"] is not None
    assert res["file_type"] == "csv"
    assert res["size_bytes"] == len(sample_csv_bytes)

    parser.delete_file(res["file_id"])


def test_oversized_file_rejected(sample_csv_bytes):
    parser = FileParser()
    small_limit = 50  # 50 bytes
    with pytest.raises(FileParserError) as exc:
        parser.validate_and_save(sample_csv_bytes, "data.csv", max_bytes=small_limit)
    assert "exceeds maximum allowed limit" in str(exc.value)


def test_invalid_file_type_rejected_fake_extension():
    parser = FileParser()
    fake_xlsx_content = b"This is just plain text, not a real excel PK zip file."
    with pytest.raises(FileParserError) as exc:
        parser.validate_and_save(fake_xlsx_content, "fraud.xlsx")
    assert "Excel file signature" in str(exc.value) or "Invalid file type" in str(exc.value)


def test_path_traversal_in_filename_sanitized(sample_csv_bytes):
    parser = FileParser()
    evil_name = "../../etc/passwd/malicious.csv"
    res = parser.validate_and_save(sample_csv_bytes, evil_name)
    assert ".." not in res["original_name"]
    assert "/" not in res["original_name"]
    assert "\\" not in res["original_name"]
    assert res["original_name"] == "malicious.csv"

    parser.delete_file(res["file_id"])


def test_empty_file_rejected():
    parser = FileParser()
    with pytest.raises(FileParserError) as exc:
        parser.validate_and_save(b"", "empty.xlsx")
    assert "empty" in str(exc.value).lower()


def test_multiple_sheets_detected_correctly():
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Summary"
    ws1.append(["ColA", "ColB"])
    ws1.append([1, 2])

    ws2 = wb.create_sheet(title="Details")
    ws2.append(["Col1", "Col2", "Col3"])
    ws2.append([10, 20, 30])
    ws2.append([40, 50, 60])

    buf = io.BytesIO()
    wb.save(buf)
    content = buf.getvalue()

    parser = FileParser()
    res = parser.validate_and_save(content, "multisheet.xlsx")
    sheets = parser.get_sheets(res["file_id"])

    assert len(sheets) == 2
    sheet_names = [s["name"] for s in sheets]
    assert "Summary" in sheet_names
    assert "Details" in sheet_names

    parser.delete_file(res["file_id"])


def test_preview_returns_correct_columns_and_rows(sample_xlsx_bytes):
    parser = FileParser()
    res = parser.validate_and_save(sample_xlsx_bytes, "preview_test.xlsx")
    preview = parser.get_preview(res["file_id"], sheet_name="SalesData", page=1, page_size=10)

    assert preview["columns"] == ["Date", "Product", "Region", "Amount", "Quantity"]
    assert len(preview["rows"]) == 6
    assert preview["total_rows"] == 6
    assert preview["rows"][0]["Product"] == "Laptop"

    parser.delete_file(res["file_id"])


def test_pagination_works_correctly(sample_xlsx_bytes):
    parser = FileParser()
    res = parser.validate_and_save(sample_xlsx_bytes, "paged_test.xlsx")

    page1 = parser.get_preview(res["file_id"], sheet_name="SalesData", page=1, page_size=2)
    assert len(page1["rows"]) == 2
    assert page1["rows"][0]["Product"] == "Laptop"
    assert page1["rows"][1]["Product"] == "Mouse"

    page2 = parser.get_preview(res["file_id"], sheet_name="SalesData", page=2, page_size=2)
    assert len(page2["rows"]) == 2
    assert page2["rows"][0]["Product"] == "Monitor"

    parser.delete_file(res["file_id"])
