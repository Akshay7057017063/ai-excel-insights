from datetime import datetime, timedelta, timezone
import io
from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import get_settings
from app.core.logging import logger
from app.repositories.report_repo import ReportRepository
from app.services.analysis_engine import AnalysisEngine
from app.services.chart_engine import ChartEngine
from app.services.data_profiler import DataProfiler
from app.services.file_parser import FileParser
from app.services.insight_engine import InsightEngine
from app.services.ai_service import AIService

settings = get_settings()


class ReportService:
    def __init__(self):
        self.file_parser = FileParser()
        self.profiler = DataProfiler()
        self.analysis_engine = AnalysisEngine()
        self.insight_engine = InsightEngine()
        self.chart_engine = ChartEngine()
        self.report_repo = ReportRepository()

    def create_report(
        self,
        file_id: str,
        sheet_name: Optional[str] = None,
        user_id: Optional[str] = None,
        guest_token: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Orchestrates end-to-end processing: loading, profiling, analyzing, insight & chart generation."""
        # 1. Load DataFrame
        df = self.file_parser.load_dataframe(file_id, sheet_name=sheet_name, max_rows=settings.MAX_ROWS)
        resolved_sheet = sheet_name or "Sheet1"
        report_name = name or f"Analysis - {resolved_sheet}"

        # 2. Data Profiling
        profile = self.profiler.profile(df)
        dataset_type = profile.get("dataset_type", {}).get("type", "general")

        # 3. Numeric & Trend Analysis
        analysis_data = self.analysis_engine.analyze(df, profile, dataset_type=dataset_type)

        # 4. Insights Generation
        insights = self.insight_engine.generate_insights(df, profile, analysis_data, dataset_type=dataset_type)

        # 5. Visualizations / Charts
        charts = self.chart_engine.generate_charts(df, profile, analysis_data, dataset_type=dataset_type)

        # 6. Format column info for schema
        column_info = []
        for col_name, c_prof in profile.get("columns", {}).items():
            column_info.append({
                "name": col_name,
                "dtype": c_prof.get("dtype", "object"),
                "inferred_type": c_prof.get("inferred_type", "general"),
                "sample_values": c_prof.get("sample_values", []),
                "missing_pct": c_prof.get("missing_pct", 0.0),
                "unique_count": c_prof.get("unique_count", 0),
                "is_numeric": c_prof.get("is_numeric", False),
                "is_date": c_prof.get("is_date", False),
                "is_categorical": c_prof.get("is_categorical", False),
            })

        # Retention expiration for guests / default retention
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REPORT_RETENTION_DAYS)

        # 7. Store in MongoDB
        doc = self.report_repo.create_report(
            file_id=file_id,
            name=report_name,
            sheet_name=resolved_sheet,
            user_id=user_id,
            guest_token=guest_token,
            row_count=profile.get("total_rows", 0),
            col_count=profile.get("total_cols", 0),
            column_info=column_info,
            dataset_type=dataset_type,
            kpis=analysis_data.get("kpis", []),
            insights=insights,
            charts=charts,
            analysis_data=analysis_data,
            expires_at=expires_at,
            status="completed",
        )

        return doc

    def get_report(
        self,
        report_id: str,
        user_id: Optional[str] = None,
        guest_token: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves report and verifies access permissions."""
        report = self.report_repo.get_report(report_id)
        if not report:
            return None

        # Check ownership: registered user or matching guest_token
        if user_id and report.get("user_id") and report.get("user_id") != user_id:
            return None
        if guest_token and report.get("guest_token") and report.get("guest_token") != guest_token and not report.get("user_id"):
            return None

        return report

    def export_pdf(
        self,
        report_id: str,
        user_id: Optional[str] = None,
        guest_token: Optional[str] = None,
    ) -> bytes:
        """Generates an executive PDF report using ReportLab with sanitization."""
        report = self.get_report(report_id, user_id=user_id, guest_token=guest_token)
        if not report:
            raise ValueError("Report not found or access denied.")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e1b4b"),
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "SubTitleStyle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=14,
        )
        section_style = ParagraphStyle(
            "SectionStyle",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#312e81"),
            spaceBefore=14,
            spaceAfter=8,
        )
        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )
        card_title = ParagraphStyle(
            "CardTitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=12,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1e293b"),
        )
        card_val = ParagraphStyle(
            "CardVal",
            parent=styles["Normal"],
            fontSize=14,
            leading=16,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#4f46e5"),
        )

        elements: List[Any] = []

        # Title & Metadata
        clean_name = escape(str(report.get("name", "Executive Excel Analysis Report")))
        clean_sheet = escape(str(report.get("sheet_name", "Sheet1")))
        clean_type = escape(str(report.get("dataset_type", "General")).title())
        date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")

        elements.append(Paragraph(clean_name, title_style))
        elements.append(Paragraph(f"Sheet: <b>{clean_sheet}</b> | Domain: <b>{clean_type}</b> | Generated: {date_str}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#e2e8f0"), spaceAfter=14))

        # KPI Summary Table
        kpis = report.get("kpis", [])
        if kpis:
            elements.append(Paragraph("Key Performance Indicators", section_style))
            kpi_cells = []
            row = []
            for k in kpis[:6]:
                k_title = escape(str(k.get("title", "")))
                k_val = escape(str(k.get("value", "")))
                k_desc = escape(str(k.get("description", "")))

                cell_content = [
                    Paragraph(k_title, card_title),
                    Spacer(1, 2),
                    Paragraph(f"{k_val} <font size=8>{escape(str(k.get('unit','') or ''))}</font>", card_val),
                    Spacer(1, 2),
                    Paragraph(k_desc, body_style),
                ]
                row.append(cell_content)
                if len(row) == 3:
                    kpi_cells.append(row)
                    row = []
            if row:
                while len(row) < 3:
                    row.append("")
                kpi_cells.append(row)

            kpi_table = Table(kpi_cells, colWidths=[2.4 * inch, 2.4 * inch, 2.4 * inch])
            kpi_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elements.append(kpi_table)
            elements.append(Spacer(1, 14))

        # Insights Section
        insights = report.get("insights", [])
        if insights:
            elements.append(Paragraph("Strategic Insights & Diagnostics", section_style))
            for ins in insights:
                i_title = escape(str(ins.get("title", "")))
                i_cat = escape(str(ins.get("category", "")).replace("_", " ").upper())
                i_exp = escape(str(ins.get("explanation", "")))
                i_act = escape(str(ins.get("suggested_action", "") or ""))

                content = [
                    Paragraph(f"<b>[{i_cat}] {i_title}</b>", card_title),
                    Spacer(1, 2),
                    Paragraph(i_exp, body_style),
                ]
                if i_act:
                    content.extend([
                        Spacer(1, 2),
                        Paragraph(f"<b>Recommended Action:</b> {i_act}", body_style),
                    ])

                ins_table = Table([[content]], colWidths=[7.2 * inch])
                ins_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]))
                elements.append(ins_table)
                elements.append(Spacer(1, 6))

        # Dataset Structure Summary
        col_info = report.get("column_info", [])
        if col_info:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Data Schema & Completeness", section_style))
            schema_data = [["Column", "Type", "Missing %", "Unique Values"]]
            for c in col_info[:15]:
                schema_data.append([
                    escape(str(c.get("name"))),
                    escape(str(c.get("inferred_type"))),
                    f"{c.get('missing_pct', 0)}%",
                    str(c.get("unique_count", 0)),
                ])

            schema_table = Table(schema_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1.7 * inch])
            schema_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ]))
            elements.append(schema_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def export_csv(
        self,
        report_id: str,
        user_id: Optional[str] = None,
        guest_token: Optional[str] = None,
        table_name: Optional[str] = None,
    ) -> str:
        """Exports analysis aggregates (trends, categories, or kpis) as a CSV string."""
        report = self.get_report(report_id, user_id=user_id, guest_token=guest_token)
        if not report:
            raise ValueError("Report not found or access denied.")

        analysis_data = report.get("analysis_data", {})

        if table_name == "trends" or (not table_name and analysis_data.get("trend_data")):
            trend_data = analysis_data.get("trend_data", [])
            if trend_data:
                rows = trend_data[0].get("data", [])
                df = pd.DataFrame(rows)
                return df.to_csv(index=False)

        if table_name == "categories" or (not table_name and analysis_data.get("ranked_categories")):
            cat_data = analysis_data.get("ranked_categories", [])
            if cat_data:
                rows = cat_data[0].get("data", [])
                df = pd.DataFrame(rows)
                return df.to_csv(index=False)

        # Default: Export KPIs
        kpis = report.get("kpis", [])
        df = pd.DataFrame(kpis)
        return df.to_csv(index=False)
