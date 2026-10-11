import uuid
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from app.core.logging import logger


class ChartEngine:
    def __init__(self):
        pass

    def generate_charts(
        self,
        df: pd.DataFrame,
        profile: Dict[str, Any],
        analysis: Dict[str, Any],
        dataset_type: str = "general",
    ) -> List[Dict[str, Any]]:
        """Generates Recharts-ready specifications based on dataset profile and analysis."""
        charts: List[Dict[str, Any]] = []

        # 1. Trend Line Chart
        trend_data = analysis.get("trend_data", [])
        if trend_data:
            trend = trend_data[0]
            dates = [p["date"] for p in trend.get("data", [])]
            values = [p["value"] for p in trend.get("data", [])]
            metric_name = trend.get("metric_column", "Value")
            date_col = trend.get("date_column", "Date")

            charts.append(self._line_chart(
                dates=dates,
                values=values,
                title=f"{metric_name} Over Time",
                x_label=date_col,
                y_label=metric_name,
                description=f"Chronological trajectory of {metric_name} aggregated by {date_col}",
            ))

        # 2. Categorical Bar Chart
        ranked_cats = analysis.get("ranked_categories", [])
        if ranked_cats:
            cat_info = ranked_cats[0]
            categories = [r["category"] for r in cat_info.get("data", [])]
            values = [r["total"] for r in cat_info.get("data", [])]
            cat_col = cat_info.get("category_column", "Category")
            metric_col = cat_info.get("metric_column", "Total")

            charts.append(self._bar_chart(
                categories=categories,
                values=values,
                title=f"Top {cat_col} by {metric_col}",
                x_label=cat_col,
                y_label=f"Total {metric_col}",
                description=f"Comparison of {cat_col} segments ordered by aggregate volume",
            ))

            # 3. Share / Composition Pie Chart
            charts.append(self._pie_chart(
                labels=categories[:6],
                values=values[:6],
                title=f"{cat_col} Distribution Share",
                description=f"Proportional breakdown across leading {cat_col} categories",
            ))

        # 4. Distribution Histogram for primary numeric column
        col_profiles = profile.get("columns", {})
        num_cols = [c for c, p in col_profiles.items() if p.get("is_numeric")]
        if num_cols:
            primary_num = num_cols[0]
            clean_series = pd.to_numeric(
                df[primary_num].astype(str).str.replace(r'[\$,₹€£%]', '', regex=True),
                errors="coerce"
            ).dropna().tolist()

            if len(clean_series) >= 5:
                charts.append(self._histogram_chart(
                    values=clean_series,
                    title=f"Distribution of {primary_num}",
                    description=f"Frequency spread and skewness across value bins for {primary_num}",
                    bins=10,
                ))

        # 5. Scatter Chart if correlation exists
        correlations = analysis.get("correlations", [])
        if correlations and len(num_cols) >= 2:
            top_corr = correlations[0]
            c1, c2 = top_corr["col1"], top_corr["col2"]
            try:
                sub = df[[c1, c2]].dropna().head(200)
                x_vals = pd.to_numeric(sub[c1].astype(str).str.replace(r'[\$,₹€£%]', '', regex=True), errors="coerce").dropna().tolist()
                y_vals = pd.to_numeric(sub[c2].astype(str).str.replace(r'[\$,₹€£%]', '', regex=True), errors="coerce").dropna().tolist()

                if len(x_vals) == len(y_vals) and len(x_vals) > 5:
                    charts.append(self._scatter_chart(
                        x_values=x_vals,
                        y_values=y_vals,
                        title=f"{c1} vs {c2} Correlation",
                        x_label=c1,
                        y_label=c2,
                        description=f"Bivariate scatter plot demonstrating relationship (r = {top_corr['coefficient']})",
                    ))
            except Exception as exc:
                logger.debug("Failed building scatter plot: %s", exc)

        return charts

    def _line_chart(
        self,
        dates: List[str],
        values: List[float],
        title: str,
        x_label: str,
        y_label: str,
        description: str,
    ) -> Dict[str, Any]:
        """Creates line chart specification formatted for Recharts."""
        data = [{"name": d, "value": v} for d, v in zip(dates, values)]
        return {
            "id": f"chart_line_{uuid.uuid4().hex[:6]}",
            "type": "line",
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "data": data,
            "description": description,
            "chart_config": {
                "stroke": "#4f46e5",
                "strokeWidth": 2,
                "dot": True,
            },
        }

    def _bar_chart(
        self,
        categories: List[str],
        values: List[float],
        title: str,
        x_label: str,
        y_label: str,
        description: str,
    ) -> Dict[str, Any]:
        """Creates bar chart specification formatted for Recharts."""
        data = [{"name": str(cat), "value": v} for cat, v in zip(categories, values)]
        return {
            "id": f"chart_bar_{uuid.uuid4().hex[:6]}",
            "type": "bar",
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "data": data,
            "description": description,
            "chart_config": {
                "fill": "#3b82f6",
                "radius": [4, 4, 0, 0],
            },
        }

    def _pie_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str,
        description: str,
    ) -> Dict[str, Any]:
        """Creates pie / donut chart specification formatted for Recharts."""
        palette = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
        data = [
            {"name": str(lbl), "value": round(float(val), 2), "color": palette[i % len(palette)]}
            for i, (lbl, val) in enumerate(zip(labels, values))
        ]
        return {
            "id": f"chart_pie_{uuid.uuid4().hex[:6]}",
            "type": "pie",
            "title": title,
            "x_label": None,
            "y_label": None,
            "data": data,
            "description": description,
            "chart_config": {
                "innerRadius": 50,
                "outerRadius": 80,
            },
        }

    def _histogram_chart(
        self,
        values: List[float],
        title: str,
        description: str,
        bins: int = 10,
    ) -> Dict[str, Any]:
        """Generates binned frequency distribution chart."""
        arr = np.array(values, dtype=float)
        arr = arr[~np.isnan(arr)]
        if len(arr) == 0:
            hist_data = []
        else:
            counts, bin_edges = np.histogram(arr, bins=bins)
            hist_data = []
            for i in range(len(counts)):
                label = f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}"
                hist_data.append({"name": label, "value": int(counts[i])})

        return {
            "id": f"chart_hist_{uuid.uuid4().hex[:6]}",
            "type": "histogram",
            "title": title,
            "x_label": "Value Range",
            "y_label": "Count",
            "data": hist_data,
            "description": description,
            "chart_config": {
                "fill": "#6366f1",
            },
        }

    def _scatter_chart(
        self,
        x_values: List[float],
        y_values: List[float],
        title: str,
        x_label: str,
        y_label: str,
        description: str,
    ) -> Dict[str, Any]:
        """Creates 2D scatter plot specification formatted for Recharts."""
        data = [{"x": float(x), "y": float(y)} for x, y in zip(x_values, y_values)]
        return {
            "id": f"chart_scatter_{uuid.uuid4().hex[:6]}",
            "type": "scatter",
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "data": data,
            "description": description,
            "chart_config": {
                "fill": "#ec4899",
            },
        }
