import logging
import re
import sys
from typing import Any
from app.core.config import get_settings

settings = get_settings()

SENSITIVE_PATTERNS = [
    re.compile(r'(password|secret|token|api_key|authorization)\s*[:=]\s*["\']?([^"\'\s]+)["\']?', re.IGNORECASE),
    re.compile(r'Bearer\s+([A-Za-z0-9\-._~+/]+=*)', re.IGNORECASE),
]


class SensitiveDataFilter(logging.Filter):
    """Filters out passwords, tokens, API keys, and secret values from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self._redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self._redact(str(v)) if isinstance(v, str) else v for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self._redact(v) if isinstance(v, str) else v for v in record.args)
        return True

    @staticmethod
    def _redact(text: str) -> str:
        for pattern in SENSITIVE_PATTERNS:
            text = pattern.sub(r'\1=***REDACTED***', text)
        return text


def setup_logging() -> logging.Logger:
    """Configures production-grade structured logging for the backend application."""
    log_level = logging.DEBUG if settings.APP_ENV == "development" else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveDataFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers on re-init
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)

    logger = logging.getLogger("ai_excel_insights")
    return logger


logger = setup_logging()
