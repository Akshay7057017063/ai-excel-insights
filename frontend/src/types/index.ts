export interface User {
  id: string
  email: string
  name: string
  plan: 'free' | 'single' | 'pro' | 'business'
  usage_count: number
  created_at: string
}

export interface AuthTokens {
  access_token: string
  token_type: string
}

export interface SheetInfo {
  name: string
  row_count: number
  col_count: number
}

export interface ColumnInfo {
  name: string
  dtype: string
  inferred_type: string
  sample_values: (string | number | null)[]
  missing_pct: number
  unique_count: number
  is_numeric: boolean
  is_date: boolean
  is_categorical: boolean
}

export interface UploadResponse {
  file_id: string
  original_name: string
  size_bytes: number
  sheets: SheetInfo[]
  guest_token?: string
}

export interface PreviewResponse {
  columns: ColumnInfo[]
  rows: Record<string, unknown>[]
  total_rows: number
  page: number
  page_size: number
}

export interface KPICard {
  title: string
  value: string | number
  unit?: string
  change_pct?: number
  change_direction?: 'up' | 'down' | 'neutral'
  description: string
  icon?: string
}

export interface InsightCard {
  id: string
  title: string
  explanation: string
  category: 'important_finding' | 'positive_trend' | 'negative_trend' | 'unusual_value' | 'data_quality' | 'opportunity' | 'risk' | 'investigate'
  metric_value?: string
  evidence?: string
  confidence: 'high' | 'medium' | 'low'
  suggested_action?: string
  warning?: string
}

export interface ChartSpec {
  id: string
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'histogram'
  title: string
  x_label: string
  y_label: string
  data: Record<string, unknown>[]
  description: string
  chart_config?: Record<string, unknown>
}

export interface Report {
  id: string
  name: string
  file_id: string
  sheet_name: string
  status: 'processing' | 'ready' | 'error'
  created_at: string
  row_count: number
  col_count: number
  dataset_type: string
  dataset_type_confidence: number
  kpis: KPICard[]
  insights: InsightCard[]
  charts: ChartSpec[]
  column_info: ColumnInfo[]
  profile_summary?: Record<string, unknown>
  error_message?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  sources?: string[]
}

export interface Plan {
  id: string
  name: string
  price_inr: number
  max_reports_per_month: number
  max_upload_mb: number
  max_rows: number
  max_ai_questions: number
  features: string[]
  is_popular?: boolean
}

export interface Subscription {
  plan_name: string
  status: 'active' | 'cancelled' | 'expired'
  start_date: string
  end_date?: string
  reports_used_this_month: number
  reports_limit: number
}
