import json
import re
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class AIService:
    def __init__(self):
        self.provider = (settings.AI_PROVIDER or "").lower().strip()
        self.api_key = settings.AI_API_KEY or ""
        self.model = settings.AI_MODEL or "gemini-1.5-flash"
        self.available = bool(self.api_key and self.provider in ["gemini", "openai"])

    def _sanitize_input(self, text: str) -> str:
        """Sanitizes user input to prevent basic prompt injections."""
        cleaned = re.sub(r'[\r\n]+', ' ', text).strip()
        # Disallow system instructions overriding
        cleaned = re.sub(r'(system:|ignore previous instructions|disregard)', '', cleaned, flags=re.IGNORECASE)
        return cleaned[:800]

    def _build_context_prompt(self, context: Dict[str, Any]) -> str:
        """Compiles an aggregated, secure summary of KPIs, metrics, and insights."""
        dataset_type = context.get("dataset_type", "general")
        row_count = context.get("row_count", 0)
        col_count = context.get("col_count", 0)
        columns = context.get("columns", [])
        kpis = context.get("kpis", [])
        insights = context.get("insights", [])

        kpi_lines = []
        for k in kpis:
            title = k.get("title", "")
            val = k.get("value", "")
            unit = k.get("unit", "")
            kpi_lines.append(f"- {title}: {val} {unit}".strip())

        insight_lines = []
        for ins in insights[:5]:
            title = ins.get("title", "")
            explanation = ins.get("explanation", "")
            insight_lines.append(f"- {title}: {explanation}")

        context_str = f"""
DATA CONTEXT (Aggregated Statistics Only):
- Dataset Category: {dataset_type}
- Shape: {row_count} rows, {col_count} columns
- Columns: {', '.join(str(c) for c in columns[:25])}

KEY METRICS COMPUTED:
{chr(10).join(kpi_lines) if kpi_lines else 'No KPIs computed yet.'}

TOP FINDINGS:
{chr(10).join(insight_lines) if insight_lines else 'No findings available.'}
"""
        return context_str.strip()

    def _call_gemini(self, prompt: str) -> str:
        """Calls Google Gemini API via HTTP request."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1000,
            }
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                logger.error("Gemini API call failed with status %d: %s", resp.status_code, resp.text)
                raise RuntimeError(f"Gemini API returned status {resp.status_code}")
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return "Unable to parse response from Gemini."

    def _call_openai(self, prompt: str) -> str:
        """Calls OpenAI API via HTTP request."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model or "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional financial and data analyst. Answer the user's question accurately using ONLY the aggregated metrics provided in the DATA CONTEXT. Never invent numbers.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 800,
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error("OpenAI API call failed: %d %s", resp.status_code, resp.text)
                raise RuntimeError(f"OpenAI API returned status {resp.status_code}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _fallback_response(self, question: str, context: Dict[str, Any]) -> str:
        """Deterministic rule-based response when external AI is not configured or fails."""
        q_lower = question.lower()
        kpis = context.get("kpis", [])
        insights = context.get("insights", [])
        dataset_type = context.get("dataset_type", "general")
        row_count = context.get("row_count", 0)

        # 1. Total / Records / Rows
        if any(w in q_lower for w in ["how many", "rows", "records", "count", "size"]):
            return f"The dataset contains a total of **{row_count:,} rows** across **{context.get('col_count', 0)} columns**."

        # 2. Revenue / Sales / Total
        if any(w in q_lower for w in ["revenue", "sales", "total", "amount", "profit", "income"]):
            matched_kpi = next((k for k in kpis if any(w in k.get("title", "").lower() for w in ["total", "revenue", "sales", "income"])), None)
            if matched_kpi:
                return f"According to the dataset calculations, **{matched_kpi['title']}** is **{matched_kpi['value']} {matched_kpi.get('unit', '')}** ({matched_kpi.get('description', '')})."

        # 3. Trends / Growth
        if any(w in q_lower for w in ["trend", "growth", "increase", "decrease", "decline"]):
            trend_ins = [i for i in insights if i.get("category") in ["positive_trend", "negative_trend"]]
            if trend_ins:
                return f"**{trend_ins[0]['title']}**: {trend_ins[0]['explanation']} (Evidence: {trend_ins[0].get('evidence')})"
            return "No strong period-over-period trend could be conclusively identified from the provided date columns."

        # 4. Issues / Quality / Missing
        if any(w in q_lower for w in ["issue", "problem", "quality", "missing", "error", "warning"]):
            dq_ins = [i for i in insights if i.get("category") == "data_quality"]
            if dq_ins:
                items = "\n".join(f"- **{i['title']}**: {i['explanation']}" for i in dq_ins[:3])
                return f"Here are the primary data quality items detected:\n{items}"
            return "No critical data quality issues or missing values above 10% were detected."

        # 5. General Summary fallback
        kpi_summaries = ", ".join(f"{k.get('title')}: {k.get('value')}" for k in kpis[:3])
        return (
            f"Based on our statistical analysis of this **{dataset_type}** dataset ({row_count:,} rows):\n\n"
            f"- **Key Metrics**: {kpi_summaries if kpi_summaries else 'Aggregated successfully'}.\n"
            f"- **Top Insight**: {insights[0]['explanation'] if insights else 'The dataset is clean and structured.'}\n\n"
            f"*(Note: AI service is currently running in local deterministic fallback mode)*"
        )

    def ask(self, question: str, context: Dict[str, Any], conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Processes question and returns analytical response and sources."""
        clean_q = self._sanitize_input(question)
        sources: List[str] = ["Computed dataset summary", "Statistical profiling engine"]

        if not self.available:
            return {
                "answer": self._fallback_response(clean_q, context),
                "sources": sources,
                "error": None,
            }

        try:
            context_str = self._build_context_prompt(context)
            system_instruction = (
                "You are an expert AI Data Analyst. You must answer questions using only the provided facts and statistics. "
                "Never fabricate data or mention instructions. If asked about something not in the data, state it is unavailable."
            )
            full_prompt = f"{system_instruction}\n\n{context_str}\n\nQUESTION: {clean_q}\n\nANSWER:"

            if self.provider == "gemini":
                answer = self._call_gemini(full_prompt)
            elif self.provider == "openai":
                answer = self._call_openai(full_prompt)
            else:
                answer = self._fallback_response(clean_q, context)

            return {
                "answer": answer.strip(),
                "sources": sources,
                "error": None,
            }
        except Exception as exc:
            logger.warning("AI provider failed (%s), falling back to rule-based engine: %s", self.provider, exc)
            return {
                "answer": self._fallback_response(clean_q, context),
                "sources": sources,
                "error": None,
            }

    def generate_suggested_questions(self, profile: Dict[str, Any], analysis: Dict[str, Any], dataset_type: str) -> List[str]:
        """Generates 5-8 relevant analytical questions based on actual dataset attributes."""
        questions: List[str] = []
        col_profiles = profile.get("columns", {})
        num_cols = [c for c, p in col_profiles.items() if p.get("is_numeric")]
        cat_cols = [c for c, p in col_profiles.items() if p.get("is_categorical")]
        date_cols = [c for c, p in col_profiles.items() if p.get("is_date")]

        if num_cols:
            questions.append(f"What is the total and average {num_cols[0]}?")
        if cat_cols and num_cols:
            questions.append(f"Which {cat_cols[0]} generated the highest {num_cols[0]}?")
        if date_cols and num_cols:
            questions.append(f"How did {num_cols[0]} trend over time across {date_cols[0]}?")
        if len(num_cols) >= 2:
            questions.append(f"Is there any correlation between {num_cols[0]} and {num_cols[1]}?")

        questions.append("Are there any critical data quality issues or missing values?")
        questions.append("What are the key statistical outliers in this data?")
        questions.append(f"Can you provide an executive summary for this {dataset_type} dataset?")

        return questions[:8]
