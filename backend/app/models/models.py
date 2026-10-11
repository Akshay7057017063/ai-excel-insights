from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_id() -> str:
    return str(uuid.uuid4())


@dataclass
class UserDocument:
    id: str = field(default_factory=generate_id)
    email: str = ""
    hashed_password: str = ""
    name: str = ""
    plan: str = "free"  # free | pro | business
    created_at: datetime = field(default_factory=utc_now)
    is_active: bool = True
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReportDocument:
    id: str = field(default_factory=generate_id)
    user_id: Optional[str] = None  # None for guest sessions
    guest_token: Optional[str] = None  # UUID for anonymous users
    file_id: str = ""
    name: str = ""
    sheet_name: str = ""
    status: str = "pending"  # pending | processing | completed | failed
    created_at: datetime = field(default_factory=utc_now)
    row_count: int = 0
    col_count: int = 0
    column_info: List[Dict[str, Any]] = field(default_factory=list)
    dataset_type: str = "general"
    insights_count: int = 0
    chart_count: int = 0
    kpis: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[Dict[str, Any]] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    analysis_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UsageRecord:
    id: str = field(default_factory=generate_id)
    user_id: Optional[str] = None
    report_id: Optional[str] = None
    action: str = ""  # upload | analyze | chat | export_pdf | export_csv
    timestamp: datetime = field(default_factory=utc_now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanDocument:
    id: str = ""
    name: str = ""  # Free, Pro, Business
    price_inr: int = 0
    max_reports_per_month: int = 3
    max_upload_mb: int = 10
    max_rows: int = 20000
    max_ai_questions: int = 15
    features: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SubscriptionDocument:
    id: str = field(default_factory=generate_id)
    user_id: str = ""
    plan_id: str = ""
    status: str = "active"  # active | cancelled | expired
    start_date: datetime = field(default_factory=utc_now)
    end_date: Optional[datetime] = None
    razorpay_subscription_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PaymentRecord:
    id: str = field(default_factory=generate_id)
    user_id: str = ""
    report_id: Optional[str] = None
    amount_inr: int = 0
    currency: str = "INR"
    status: str = "created"  # created | captured | failed
    provider: str = "razorpay"
    provider_payment_id: Optional[str] = None
    provider_order_id: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConversationMessage:
    id: str = field(default_factory=generate_id)
    report_id: str = ""
    role: str = "user"  # user | assistant
    content: str = ""
    timestamp: datetime = field(default_factory=utc_now)
    sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
