from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")


# --- Standard Generic Wrapper ---
class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    success: bool = False
    detail: str
    code: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None


# --- Health ---
class HealthResponse(BaseModel):
    status: str
    version: str
    mongodb_connected: bool
    ai_available: bool
    payment_available: bool
    timestamp: datetime


# --- Auth & User ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=2, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    plan: str
    created_at: datetime
    is_active: bool
    usage_count: int

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# --- Upload & Sheet Parsing ---
class SheetInfo(BaseModel):
    name: str
    row_count: int
    col_count: int


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size_bytes: int
    sheets: List[SheetInfo]
    guest_token: Optional[str] = None


class ColumnInfo(BaseModel):
    name: str
    dtype: str
    inferred_type: str = "general"
    sample_values: List[Any] = Field(default_factory=list)
    missing_pct: float = 0.0
    unique_count: int = 0
    is_numeric: bool = False
    is_date: bool = False
    is_categorical: bool = False


class PreviewResponse(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    page: int
    page_size: int
    sheet_name: str


# --- Analysis & Reports ---
class AnalysisRequest(BaseModel):
    sheet_name: Optional[str] = None
    header_row: int = 0
    name: Optional[str] = None


class AnalysisStatus(BaseModel):
    report_id: str
    status: str  # pending | processing | completed | failed
    progress: int = Field(0, ge=0, le=100)
    message: Optional[str] = None


class KPICard(BaseModel):
    title: str
    value: Any
    unit: Optional[str] = None
    change_pct: Optional[float] = None
    change_direction: Optional[str] = None  # up | down | neutral
    description: Optional[str] = None


class InsightCard(BaseModel):
    id: str
    title: str
    explanation: str
    category: str  # important_finding, positive_trend, negative_trend, unusual_value, data_quality, opportunity, risk, investigate
    metric_value: Optional[str] = None
    evidence: Optional[str] = None
    confidence: float = 1.0
    suggested_action: Optional[str] = None
    warning: Optional[str] = None


class ChartSpec(BaseModel):
    id: str
    type: str  # line | bar | pie | scatter | histogram
    title: str
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    data: List[Dict[str, Any]]
    description: Optional[str] = None
    chart_config: Dict[str, Any] = Field(default_factory=dict)


class ReportRenameRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class ReportOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    file_id: str
    name: str
    sheet_name: str
    status: str
    created_at: datetime
    row_count: int
    col_count: int
    column_info: List[ColumnInfo] = Field(default_factory=list)
    dataset_type: str = "general"
    insights_count: int = 0
    chart_count: int = 0
    kpis: List[KPICard] = Field(default_factory=list)
    insights: List[InsightCard] = Field(default_factory=list)
    charts: List[ChartSpec] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReportSummaryOut(BaseModel):
    id: str
    name: str
    sheet_name: str
    status: str
    created_at: datetime
    row_count: int
    col_count: int
    dataset_type: str
    insights_count: int
    chart_count: int
    expires_at: Optional[datetime] = None


# --- AI Chat ---
class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str
    timestamp: Optional[datetime] = None
    sources: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    message: str
    sources: List[str] = Field(default_factory=list)
    suggested_questions: List[str] = Field(default_factory=list)


# --- Billing & Subscriptions ---
class PlanOut(BaseModel):
    id: str
    name: str
    price_inr: int
    max_reports_per_month: int
    max_upload_mb: int
    max_rows: int
    max_ai_questions: int
    features: List[str]


class CheckoutRequest(BaseModel):
    plan_name: str


class CheckoutResponse(BaseModel):
    order_id: Optional[str] = None
    amount_inr: int
    currency: str = "INR"
    key_id: Optional[str] = None
    error: Optional[str] = None


class VerifyPaymentRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str
    plan_name: str


class SubscriptionOut(BaseModel):
    id: str
    user_id: str
    plan_id: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
