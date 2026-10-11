import math
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from app.core.logging import logger


class AnalysisEngine:
    def __init__(self):
        pass

    def analyze(self, df: pd.DataFrame, profile: Dict[str, Any], dataset_type: str = "general") -> Dict[str, Any]:
        """Runs deterministic mathematical analysis on DataFrame based on profile."""
        kpis = self._compute_kpis(df, profile, dataset_type)
        trend_data = self._compute_trends(df, profile)
        ranked_categories = self._compute_category_analysis(df, profile)
        correlations = self._compute_correlations(df, profile)

        return {
            "kpis": kpis,
            "trend_data": trend_data,
            "ranked_categories": ranked_categories,
            "correlations": correlations,
        }

    def _compute_kpis(self, df: pd.DataFrame, profile: Dict[str, Any], dataset_type: str) -> List[Dict[str, Any]]:
        """Computes summary metrics and domain-specific KPI cards."""
        kpis: List[Dict[str, Any]] = []
        total_rows = len(df)
        total_cols = len(df.columns)

        # Baseline KPI: Total Records
        kpis.append({
            "title": "Total Records",
            "value": total_rows,
            "unit": "rows",
            "change_pct": None,
            "change_direction": "neutral",
            "description": f"Dataset contains {total_rows:,} rows across {total_cols} columns",
        })

        # Baseline KPI: Data Completeness
        total_cells = total_rows * total_cols
        total_missing = sum(p.get("missing_count", 0) for p in profile.get("columns", {}).values())
        completeness_pct = round(((total_cells - total_missing) / total_cells * 100), 1) if total_cells > 0 else 100.0

        kpis.append({
            "title": "Data Completeness",
            "value": f"{completeness_pct}%",
            "unit": "%",
            "change_pct": None,
            "change_direction": "up" if completeness_pct >= 90 else "down",
            "description": f"{total_missing:,} missing values detected across all columns",
        })

        # Identify numeric columns for aggregations
        col_profiles = profile.get("columns", {})
        numeric_cols = [c for c, p in col_profiles.items() if p.get("is_numeric")]

        if dataset_type == "sales":
            # Search for revenue / amount column
            revenue_col = next((c for c in numeric_cols if any(k in c.lower() for k in ["amount", "revenue", "sales", "total"])), None)
            qty_col = next((c for c in numeric_cols if any(k in c.lower() for k in ["qty", "quantity", "units"])), None)
            prod_col = next((c for c, p in col_profiles.items() if p.get("is_categorical") and any(k in c.lower() for k in ["product", "item", "sku"])), None)

            if revenue_col:
                series = pd.to_numeric(df[revenue_col].astype(str).str.replace(r'[\$,₹€£]', '', regex=True), errors="coerce").dropna()
                tot_rev = series.sum()
                avg_rev = series.mean()
                kpis.append({
                    "title": f"Total {revenue_col.title()}",
                    "value": round(float(tot_rev), 2),
                    "unit": "sum",
                    "change_pct": None,
                    "change_direction": "up",
                    "description": f"Sum of all {revenue_col} entries",
                })
                kpis.append({
                    "title": f"Avg {revenue_col.title()} / Order",
                    "value": round(float(avg_rev), 2),
                    "unit": "avg",
                    "change_pct": None,
                    "change_direction": "neutral",
                    "description": f"Average ticket size across {len(series):,} orders",
                })

            if qty_col:
                qty_series = pd.to_numeric(df[qty_col].astype(str).str.replace(r'[\$,₹€£]', '', regex=True), errors="coerce").dropna()
                kpis.append({
                    "title": f"Total Units ({qty_col})",
                    "value": int(qty_series.sum()),
                    "unit": "units",
                    "change_pct": None,
                    "change_direction": "neutral",
                    "description": f"Cumulative volume across records",
                })

            if prod_col:
                top_prod = df[prod_col].dropna().value_counts().head(1)
                if not top_prod.empty:
                    kpis.append({
                        "title": "Top Selling Category/Product",
                        "value": str(top_prod.index[0]),
                        "unit": f"{int(top_prod.iloc[0])} transactions",
                        "change_pct": None,
                        "change_direction": "up",
                        "description": f"Most frequent item in column {prod_col}",
                    })

        elif dataset_type == "finance":
            income_col = next((c for c in numeric_cols if any(k in c.lower() for k in ["income", "credit", "revenue"])), None)
            expense_col = next((c for c in numeric_cols if any(k in c.lower() for k in ["expense", "debit", "cost"])), None)

            if income_col:
                inc_val = pd.to_numeric(df[income_col], errors="coerce").sum()
                kpis.append({
                    "title": "Total Income",
                    "value": round(float(inc_val), 2),
                    "unit": "INR",
                    "change_pct": None,
                    "change_direction": "up",
                    "description": f"Aggregated income recorded in {income_col}",
                })
            if expense_col:
                exp_val = pd.to_numeric(df[expense_col], errors="coerce").sum()
                kpis.append({
                    "title": "Total Expenses",
                    "value": round(float(exp_val), 2),
                    "unit": "INR",
                    "change_pct": None,
                    "change_direction": "down",
                    "description": f"Aggregated expenses recorded in {expense_col}",
                })

        # Generic KPI addition if specific ones were not found
        if len(kpis) < 4:
            for num_col in numeric_cols[:2]:
                if not any(kpi["title"].endswith(num_col) for kpi in kpis):
                    clean_s = pd.to_numeric(df[num_col], errors="coerce").dropna()
                    if not clean_s.empty:
                        kpis.append({
                            "title": f"Total {num_col}",
                            "value": round(float(clean_s.sum()), 2),
                            "unit": "sum",
                            "change_pct": None,
                            "change_direction": "neutral",
                            "description": f"Cumulative sum of {num_col} (Avg: {round(float(clean_s.mean()), 2):,})",
                        })

        return kpis

    def _compute_trends(self, df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifies time-series pairs and aggregates by date/month."""
        trends: List[Dict[str, Any]] = []
        col_profiles = profile.get("columns", {})

        date_cols = [c for c, p in col_profiles.items() if p.get("is_date")]
        num_cols = [c for c, p in col_profiles.items() if p.get("is_numeric")]

        if not date_cols or not num_cols:
            return trends

        date_col = date_cols[0]
        num_col = num_cols[0]

        try:
            temp_df = df[[date_col, num_col]].dropna().copy()
            temp_df["parsed_date"] = pd.to_datetime(temp_df[date_col], errors="coerce")
            temp_df["clean_val"] = pd.to_numeric(
                temp_df[num_col].astype(str).str.replace(r'[\$,₹€£%]', '', regex=True),
                errors="coerce"
            )
            temp_df = temp_df.dropna(subset=["parsed_date", "clean_val"])

            if len(temp_df) < 2:
                return trends

            temp_df = temp_df.sort_values("parsed_date")

            # Group by year-month or date
            temp_df["period"] = temp_df["parsed_date"].dt.strftime("%Y-%m")
            grouped = temp_df.groupby("period")["clean_val"].agg(["sum", "mean", "count"]).reset_index()

            data_points = []
            prev_sum = None
            for _, r in grouped.iterrows():
                curr_sum = float(r["sum"])
                mom_change = None
                if prev_sum is not None and prev_sum != 0:
                    mom_change = round(((curr_sum - prev_sum) / prev_sum) * 100, 2)
                prev_sum = curr_sum

                data_points.append({
                    "date": str(r["period"]),
                    "value": round(curr_sum, 2),
                    "mean": round(float(r["mean"]), 2),
                    "count": int(r["count"]),
                    "mom_change_pct": mom_change,
                })

            trends.append({
                "date_column": date_col,
                "metric_column": num_col,
                "data": data_points,
            })
        except Exception as exc:
            logger.warning("Error computing trend for %s and %s: %s", date_col, num_col, exc)

        return trends

    def _compute_category_analysis(self, df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Groups numeric metrics across top categories."""
        ranked_categories: List[Dict[str, Any]] = []
        col_profiles = profile.get("columns", {})

        cat_cols = [c for c, p in col_profiles.items() if p.get("is_categorical") and p.get("unique_count", 0) <= 50]
        num_cols = [c for c, p in col_profiles.items() if p.get("is_numeric")]

        if not cat_cols or not num_cols:
            return ranked_categories

        for cat_col in cat_cols[:2]:
            num_col = num_cols[0]
            try:
                temp_df = df[[cat_col, num_col]].dropna().copy()
                temp_df["clean_val"] = pd.to_numeric(
                    temp_df[num_col].astype(str).str.replace(r'[\$,₹€£%]', '', regex=True),
                    errors="coerce"
                )
                temp_df = temp_df.dropna(subset=["clean_val"])

                grouped = (
                    temp_df.groupby(cat_col)["clean_val"]
                    .agg(["sum", "mean", "count"])
                    .sort_values(by="sum", ascending=False)
                    .head(10)
                    .reset_index()
                )

                category_data = []
                for _, r in grouped.iterrows():
                    category_data.append({
                        "category": str(r[cat_col]),
                        "total": round(float(r["sum"]), 2),
                        "mean": round(float(r["mean"]), 2),
                        "count": int(r["count"]),
                    })

                ranked_categories.append({
                    "category_column": cat_col,
                    "metric_column": num_col,
                    "data": category_data,
                })
            except Exception as exc:
                logger.warning("Category aggregation error on %s: %s", cat_col, exc)

        return ranked_categories

    def _compute_correlations(self, df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Computes Pearson correlations between numeric columns, filtering for |r| >= 0.4."""
        correlations: List[Dict[str, Any]] = []
        col_profiles = profile.get("columns", {})
        num_cols = [c for c, p in col_profiles.items() if p.get("is_numeric")]

        if len(num_cols) < 2:
            return correlations

        try:
            clean_num_df = pd.DataFrame()
            for col in num_cols:
                clean_num_df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(r'[\$,₹€£%]', '', regex=True),
                    errors="coerce"
                )

            corr_matrix = clean_num_df.corr(method="pearson")
            n = len(clean_num_df)

            cols = list(corr_matrix.columns)
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    c1, c2 = cols[i], cols[j]
                    val = corr_matrix.loc[c1, c2]

                    if pd.notna(val) and abs(val) >= 0.4:
                        r = float(val)
                        # Estimate p-value roughly via t-distribution approx if n > 2
                        p_val = 0.05
                        if n > 2 and (1 - r ** 2) > 0:
                            t_stat = r * math.sqrt((n - 2) / (1 - r ** 2))
                            # rough p-value indicator
                            p_val = round(max(0.0001, min(0.1, 2.0 / (abs(t_stat) + 1.0))), 4)

                        correlations.append({
                            "col1": c1,
                            "col2": c2,
                            "coefficient": round(r, 3),
                            "relationship": "Strong Positive" if r > 0.7 else ("Moderate Positive" if r > 0.4 else ("Strong Negative" if r < -0.7 else "Moderate Negative")),
                            "p_value_estimate": p_val,
                        })
        except Exception as exc:
            logger.warning("Correlation calculation error: %s", exc)

        return correlations
