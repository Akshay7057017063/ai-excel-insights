from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from app.core.logging import logger


class DataProfiler:
    def __init__(self):
        pass

    def profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Performs comprehensive profiling on the given DataFrame."""
        total_rows = int(len(df))
        total_cols = int(len(df.columns))

        if total_rows == 0 or total_cols == 0:
            return {
                "total_rows": total_rows,
                "total_cols": total_cols,
                "duplicate_rows": 0,
                "constant_columns": [],
                "columns": {},
                "dataset_type": {"type": "general", "confidence": 0.0, "reasoning": "Empty dataset"},
            }

        duplicate_rows = int(df.duplicated().sum())

        col_profiles: Dict[str, Any] = {}
        constant_columns: List[str] = []

        for col_name in df.columns:
            series = df[col_name]
            col_profile = self._profile_column(series, str(col_name), total_rows)
            col_profiles[str(col_name)] = col_profile
            if col_profile.get("unique_count", 0) <= 1:
                constant_columns.append(str(col_name))

        dataset_type_info = self._infer_dataset_type(df, col_profiles)

        return {
            "total_rows": total_rows,
            "total_cols": total_cols,
            "duplicate_rows": duplicate_rows,
            "constant_columns": constant_columns,
            "columns": col_profiles,
            "dataset_type": dataset_type_info,
        }

    def _infer_column_type(self, series: pd.Series, col_name: str) -> str:
        """Infers the semantic type of a column based on name heuristics and values."""
        name_lower = col_name.lower().strip()
        non_null = series.dropna()

        if len(non_null) == 0:
            return "empty"

        # Check boolean
        if series.dtype == bool or set(str(v).lower() for v in non_null.head(100)).issubset({"true", "false", "yes", "no", "0", "1", "t", "f"}):
            if len(non_null.unique()) <= 2:
                return "boolean"

        # Check ID
        if any(token in name_lower for token in ["_id", "id", "code", "uuid", "guid", "sku", "isbn"]):
            return "id"

        # Check percentage
        if any(token in name_lower for token in ["pct", "percent", "percentage", "rate", "ratio"]):
            return "percentage"

        # Check currency / monetary
        if any(token in name_lower for token in ["price", "cost", "amount", "revenue", "salary", "fee", "profit", "total", "sales", "discount", "tax", "charge"]):
            # Confirm if numeric
            try:
                pd.to_numeric(non_null.astype(str).str.replace(r'[\$,₹€£]', '', regex=True))
                return "currency"
            except Exception:
                pass

        # Check Date
        if pd.api.types.is_datetime64_any_dtype(series):
            return "date"
        if any(token in name_lower for token in ["date", "time", "timestamp", "year", "month", "day", "created_at"]):
            try:
                pd.to_datetime(non_null.head(50), errors="raise")
                return "date"
            except Exception:
                pass

        # Check Numeric
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        else:
            try:
                pd.to_numeric(non_null.head(50))
                return "numeric"
            except Exception:
                pass

        # Categorical vs General Text
        unique_count = len(non_null.unique())
        if unique_count <= 50 or (len(non_null) > 0 and (unique_count / len(non_null) < 0.2)):
            return "categorical"

        return "text"

    def _profile_column(self, series: pd.Series, col_name: str, total_rows: int) -> Dict[str, Any]:
        """Generates statistical and type profile for a single column."""
        missing_count = int(series.isna().sum())
        missing_pct = round((missing_count / total_rows * 100) if total_rows > 0 else 0.0, 2)
        non_null = series.dropna()
        unique_count = int(non_null.nunique())

        inferred_type = self._infer_column_type(series, col_name)

        sample_vals = [
            str(x) if not isinstance(x, (int, float, bool)) else x
            for x in non_null.head(5).tolist()
        ]

        profile: Dict[str, Any] = {
            "name": col_name,
            "dtype": str(series.dtype),
            "inferred_type": inferred_type,
            "missing_count": missing_count,
            "missing_pct": missing_pct,
            "unique_count": unique_count,
            "sample_values": sample_vals,
            "is_numeric": inferred_type in ["numeric", "currency", "percentage"],
            "is_date": inferred_type == "date",
            "is_categorical": inferred_type in ["categorical", "boolean"],
        }

        # Numeric statistics & Outlier calculation via IQR
        if profile["is_numeric"]:
            try:
                clean_num = pd.to_numeric(
                    non_null.astype(str).str.replace(r'[\$,₹€£%]', '', regex=True),
                    errors="coerce",
                ).dropna()

                if len(clean_num) > 0:
                    q25 = float(clean_num.quantile(0.25))
                    q75 = float(clean_num.quantile(0.75))
                    iqr = q75 - q25
                    lower_bound = q25 - 1.5 * iqr
                    upper_bound = q75 + 1.5 * iqr
                    outliers = clean_num[(clean_num < lower_bound) | (clean_num > upper_bound)]

                    profile.update({
                        "min": round(float(clean_num.min()), 4),
                        "max": round(float(clean_num.max()), 4),
                        "mean": round(float(clean_num.mean()), 4),
                        "median": round(float(clean_num.median()), 4),
                        "std": round(float(clean_num.std()), 4) if len(clean_num) > 1 else 0.0,
                        "q25": round(q25, 4),
                        "q75": round(q75, 4),
                        "outlier_count": int(len(outliers)),
                        "outlier_samples": [round(float(v), 2) for v in outliers.head(5).tolist()],
                    })
            except Exception as exc:
                logger.debug("Failed computing numeric stats for %s: %s", col_name, exc)

        # Categorical statistics
        if profile["is_categorical"]:
            top_values = non_null.value_counts().head(5).to_dict()
            profile["top_values"] = {str(k): int(v) for k, v in top_values.items()}

        # Date statistics
        if profile["is_date"]:
            try:
                date_series = pd.to_datetime(non_null, errors="coerce").dropna()
                if len(date_series) > 0:
                    profile["min_date"] = str(date_series.min())
                    profile["max_date"] = str(date_series.max())
            except Exception as exc:
                logger.debug("Failed computing date stats for %s: %s", col_name, exc)

        return profile

    def _infer_dataset_type(self, df: pd.DataFrame, col_profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Infers the business domain of the dataset with a confidence score."""
        cols_lower = [c.lower() for c in df.columns]

        keywords = {
            "sales": ["sales", "order", "revenue", "product", "customer", "discount", "quantity", "profit", "unit_price", "region"],
            "finance": ["balance", "income", "expense", "transaction", "debit", "credit", "account", "ledger", "invoice", "cash"],
            "hr": ["employee", "department", "salary", "hire_date", "designation", "role", "leave", "performance", "bonus"],
            "inventory": ["stock", "warehouse", "inventory", "sku", "reorder", "quantity_on_hand", "supplier"],
            "marketing": ["campaign", "clicks", "impressions", "leads", "ctr", "cpc", "conversion", "ad_spend"],
            "education": ["student", "grade", "score", "course", "marks", "exam", "gpa", "class", "subject"],
        }

        scores: Dict[str, int] = {}
        for domain, domain_kws in keywords.items():
            match_count = sum(1 for kw in domain_kws if any(kw in col for col in cols_lower))
            scores[domain] = match_count

        best_domain = max(scores, key=scores.get)
        best_score = scores[best_domain]

        if best_score >= 3:
            confidence = min(0.95, 0.5 + (best_score * 0.1))
            return {
                "type": best_domain,
                "confidence": round(confidence, 2),
                "reasoning": f"Identified multiple domain-specific columns matching '{best_domain}' domain.",
            }
        elif best_score >= 1:
            confidence = 0.60
            return {
                "type": best_domain,
                "confidence": confidence,
                "reasoning": f"Some column names suggest a '{best_domain}' dataset.",
            }
        else:
            return {
                "type": "general",
                "confidence": 0.50,
                "reasoning": "Generic tabular dataset without strong domain-specific keywords.",
            }
