import uuid
from typing import Any, Dict, List, Optional
import pandas as pd
from app.core.logging import logger


class InsightEngine:
    def __init__(self):
        pass

    def generate_insights(
        self,
        df: pd.DataFrame,
        profile: Dict[str, Any],
        analysis: Dict[str, Any],
        dataset_type: str = "general",
    ) -> List[Dict[str, Any]]:
        """Generates actionable, fact-based business insights and quality diagnostics."""
        insights: List[Dict[str, Any]] = []

        # 1. Data Quality Diagnostics
        insights.extend(self._data_quality_insights(profile))

        # 2. Outliers & Anomalies
        insights.extend(self._outlier_insights(df, profile))

        # 3. Trends & Growth
        insights.extend(self._trend_insights(analysis))

        # 4. Domain & Business Analysis
        insights.extend(self._business_insights(df, profile, analysis, dataset_type))

        # Ensure unique IDs and confidence values
        for idx, item in enumerate(insights):
            if "id" not in item:
                item["id"] = f"ins_{idx+1}_{uuid.uuid4().hex[:6]}"

        return insights

    def _data_quality_insights(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Checks for missing data, duplicates, and dead/constant columns."""
        insights: List[Dict[str, Any]] = []
        col_profiles = profile.get("columns", {})
        total_rows = profile.get("total_rows", 0)

        # High missing value warnings (> 10%)
        for col_name, col_data in col_profiles.items():
            missing_pct = col_data.get("missing_pct", 0.0)
            missing_cnt = col_data.get("missing_count", 0)
            if missing_pct >= 10.0:
                insights.append({
                    "id": f"dq_missing_{col_name}",
                    "title": f"Elevated Missing Values in '{col_name}'",
                    "explanation": f"Column '{col_name}' is missing {missing_pct}% ({missing_cnt:,} rows) of its records. High sparsity may bias downstream calculations.",
                    "category": "data_quality",
                    "metric_value": f"{missing_pct}% Missing",
                    "evidence": f"{missing_cnt}/{total_rows} entries missing",
                    "confidence": 0.98,
                    "suggested_action": f"Audit source exports for '{col_name}' or impute standard baseline values prior to modeling.",
                    "warning": f"Avoid using '{col_name}' as a mandatory primary key or partitioning filter.",
                })

        # Duplicate row warning
        duplicates = profile.get("duplicate_rows", 0)
        if duplicates > 0:
            dup_pct = round((duplicates / total_rows * 100) if total_rows > 0 else 0.0, 1)
            insights.append({
                "id": "dq_duplicates",
                "title": f"{duplicates:,} Duplicate Rows Detected",
                "explanation": f"Found {duplicates:,} identical rows ({dup_pct}% of total records). Duplicates distort sums, revenue totals, and frequency counts.",
                "category": "data_quality",
                "metric_value": f"{duplicates:,} Rows",
                "evidence": f"{dup_pct}% of the dataset",
                "confidence": 1.0,
                "suggested_action": "Apply deduplication based on transaction IDs or unique record timestamps.",
                "warning": "Totals may be artificially inflated if duplicates reflect re-sent events.",
            })

        # Constant columns (zero variance)
        constant_cols = profile.get("constant_columns", [])
        if constant_cols:
            col_list_str = ", ".join(f"'{c}'" for c in constant_cols[:3])
            insights.append({
                "id": "dq_constant",
                "title": "Columns with Zero Variance",
                "explanation": f"Columns {col_list_str} contain only a single distinct value across all records. They provide no informational gain.",
                "category": "data_quality",
                "metric_value": f"{len(constant_cols)} Constant Columns",
                "evidence": f"Unique count <= 1 in {col_list_str}",
                "confidence": 1.0,
                "suggested_action": "Consider excluding redundant static columns to simplify report analysis.",
                "warning": None,
            })

        return insights

    def _trend_insights(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifies significant period-over-period changes and volatility."""
        insights: List[Dict[str, Any]] = []
        trend_data = analysis.get("trend_data", [])

        for trend in trend_data:
            metric_col = trend.get("metric_column")
            data_points = trend.get("data", [])
            if len(data_points) < 2:
                continue

            # Check most recent MoM change
            latest = data_points[-1]
            previous = data_points[-2]
            mom_change = latest.get("mom_change_pct")

            if mom_change is not None:
                if mom_change >= 10.0:
                    insights.append({
                        "id": f"trend_growth_{metric_col}",
                        "title": f"Strong Growth Momentum in {metric_col}",
                        "explanation": f"Value climbed {mom_change}% between {previous['date']} ({previous['value']:,}) and {latest['date']} ({latest['value']:,}).",
                        "category": "positive_trend",
                        "metric_value": f"+{mom_change}% MoM",
                        "evidence": f"From {previous['value']:,} to {latest['value']:,}",
                        "confidence": 0.95,
                        "suggested_action": "Analyze driving factors behind the surge to replicate strategies across other periods.",
                        "warning": None,
                    })
                elif mom_change <= -10.0:
                    insights.append({
                        "id": f"trend_decline_{metric_col}",
                        "title": f"Substantial Contraction in {metric_col}",
                        "explanation": f"Experienced a {abs(mom_change)}% contraction in the most recent period ({previous['date']} vs {latest['date']}).",
                        "category": "negative_trend",
                        "metric_value": f"{mom_change}% MoM",
                        "evidence": f"Dropped from {previous['value']:,} to {latest['value']:,}",
                        "confidence": 0.95,
                        "suggested_action": "Inspect customer churn, supply shortages, or seasonal factors triggering the slump.",
                        "warning": f"Risk of ongoing revenue/volume attrition if negative trend persists.",
                    })

        return insights

    def _outlier_insights(self, df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Highlights numeric columns containing statistical anomalies."""
        insights: List[Dict[str, Any]] = []
        col_profiles = profile.get("columns", {})

        for col_name, p in col_profiles.items():
            outlier_cnt = p.get("outlier_count", 0)
            if outlier_cnt > 0:
                mean_val = p.get("mean", 0)
                max_val = p.get("max", 0)
                samples = p.get("outlier_samples", [])
                sample_str = ", ".join(str(s) for s in samples[:3])

                insights.append({
                    "id": f"outlier_{col_name}",
                    "title": f"Statistical Outliers in '{col_name}'",
                    "explanation": f"Detected {outlier_cnt:,} values beyond 1.5x IQR boundaries. Max value reaches {max_val:,} compared to average of {mean_val:,}.",
                    "category": "unusual_value",
                    "metric_value": f"{outlier_cnt} Outliers",
                    "evidence": f"Extreme values observed: [{sample_str}]",
                    "confidence": 0.92,
                    "suggested_action": "Investigate whether these represent enterprise bulk transactions, currency mismatches, or entry errors.",
                    "warning": "Extreme outliers significantly skew mean and standard deviation metrics.",
                })

        return insights

    def _business_insights(
        self,
        df: pd.DataFrame,
        profile: Dict[str, Any],
        analysis: Dict[str, Any],
        dataset_type: str,
    ) -> List[Dict[str, Any]]:
        """Extracts domain-tailored business findings."""
        insights: List[Dict[str, Any]] = []

        ranked_cats = analysis.get("ranked_categories", [])
        if ranked_cats:
            cat_info = ranked_cats[0]
            cat_col = cat_info.get("category_column")
            metric_col = cat_info.get("metric_column")
            records = cat_info.get("data", [])

            if len(records) >= 2:
                top_item = records[0]
                total_metric_sum = sum(r["total"] for r in records)
                if total_metric_sum > 0:
                    top_share = round((top_item["total"] / total_metric_sum) * 100, 1)

                    if top_share > 40.0:
                        insights.append({
                            "id": f"biz_concentration_{cat_col}",
                            "title": f"High Concentration in '{top_item['category']}'",
                            "explanation": f"The top segment '{top_item['category']}' accounts for {top_share}% of total {metric_col} ({top_item['total']:,} of {total_metric_sum:,}).",
                            "category": "risk" if top_share > 60 else "important_finding",
                            "metric_value": f"{top_share}% Share",
                            "evidence": f"Top segment: {top_item['category']} ({top_item['total']:,})",
                            "confidence": 0.96,
                            "suggested_action": "Diversify reliance to prevent single-point dependency vulnerabilities.",
                            "warning": f"Revenue is vulnerable to disruptions impacting '{top_item['category']}'." if top_share > 60 else None,
                        })

        correlations = analysis.get("correlations", [])
        for corr in correlations:
            r = corr.get("coefficient", 0.0)
            c1, c2 = corr.get("col1"), corr.get("col2")
            if abs(r) >= 0.7:
                direction = "direct relationship" if r > 0 else "inverse relationship"
                insights.append({
                    "id": f"biz_corr_{c1}_{c2}",
                    "title": f"Strong Correlation: '{c1}' & '{c2}'",
                    "explanation": f"Correlation coefficient r={r:.2f} indicates a statistically strong {direction}. Changes in {c1} heavily co-occur with changes in {c2}.",
                    "category": "opportunity",
                    "metric_value": f"r = {r:.2f}",
                    "evidence": f"Pearson r = {r:.3f} across numeric observations",
                    "confidence": 0.90,
                    "suggested_action": f"Leverage {c1} as a leading predictive indicator for forecasting {c2}.",
                    "warning": "Correlation does not necessarily imply direct causality.",
                })

        return insights
