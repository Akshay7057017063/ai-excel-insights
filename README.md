# AI Excel Insights

> **Upload your Excel. Understand your data — automatically.**

AI Excel Insights is a production-oriented SaaS web application that transforms Excel and CSV files into clear, plain-language insights — no formulas, no pivot tables, no technical knowledge required.

---

## Table of Contents

- [Product Overview](#product-overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Local Development Setup (Windows PowerShell)](#local-development-setup-windows-powershell)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [Deployment Notes](#deployment-notes)
- [Limitations and Roadmap](#limitations-and-roadmap)

---

## Product Overview

**Workflow:** Upload file → Automatic inspection → Smart analysis → Insights dashboard → Ask questions → Download report

**Target users:** People who cannot write Excel formulas, create pivot tables, or interpret business data independently.

**What the app does automatically:**
- Detects column types (numeric, date, categorical, currency, percentage)
- Identifies missing values, duplicates, and outliers
- Infers dataset purpose (sales, finance, HR, inventory, education, etc.)
- Calculates appropriate business metrics
- Selects and renders suitable charts
- Generates plain-language insights with supporting evidence
- Allows natural-language questions through an AI chat interface
- Exports professional PDF reports

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Charts | Recharts |
| Icons | Lucide React |
| Forms | React Hook Form + Zod |
| Data Fetching | TanStack Query (React Query) |
| Backend | Python 3.12, FastAPI, Uvicorn |
| Data Analysis | Pandas, NumPy |
| File Parsing | openpyxl (XLSX), xlrd (XLS), chardet (CSV encoding) |
| PDF Export | ReportLab |
| Database | MongoDB with PyMongo |
| Authentication | JWT (python-jose), bcrypt |
| Payments | Razorpay (optional) |
| AI | Gemini API or OpenAI (configurable, optional) |

---

## Project Structure

```
ai-excel-insights/
├── frontend/                    # React/Vite application
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── ui/              # Base components (Button, Card, Badge, etc.)
│   │   │   ├── upload/          # Upload flow components
│   │   │   ├── dashboard/       # Report dashboard components
│   │   │   └── chat/            # AI chat panel
│   │   ├── pages/               # Route-level pages
│   │   ├── layouts/             # Page layout wrappers
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client functions
│   │   ├── types/               # TypeScript type definitions
│   │   ├── context/             # React context providers
│   │   └── utils/               # Utility functions
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.example
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings
│   │   │   ├── security.py      # JWT, password hashing
│   │   │   └── logging.py       # Structured logging
│   │   ├── api/
│   │   │   ├── router.py        # API router aggregation
│   │   │   └── routes/
│   │   │       ├── health.py    # Health check
│   │   │       ├── uploads.py   # File upload/preview
│   │   │       ├── analysis.py  # Run analysis
│   │   │       ├── reports.py   # Report management
│   │   │       ├── chat.py      # AI chat
│   │   │       ├── auth.py      # Authentication
│   │   │       └── billing.py   # Payments/subscriptions
│   │   ├── services/
│   │   │   ├── file_parser.py   # File validation, parsing, preview
│   │   │   ├── data_profiler.py # Dataset profiling, type inference
│   │   │   ├── analysis_engine.py # KPIs, trends, correlations
│   │   │   ├── insight_engine.py  # Plain-language insight generation
│   │   │   ├── chart_engine.py    # Chart specification generation
│   │   │   ├── ai_service.py    # LLM integration (Gemini/OpenAI)
│   │   │   ├── report_service.py  # Orchestration + PDF export
│   │   │   └── payment_service.py # Razorpay integration
│   │   ├── models/              # MongoDB document schemas
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── repositories/        # Database access layer
│   │   └── utils/               # Utilities
│   ├── tests/                   # pytest test suite
│   ├── uploads/                 # Temporary file storage (auto-cleaned)
│   ├── requirements.txt
│   └── .env.example
│
├── .gitignore
└── README.md
```

---

## Prerequisites

- **Python 3.12+** — [python.org/downloads](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **MongoDB** — [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community) (or use [MongoDB Atlas](https://www.mongodb.com/atlas) free tier)
- **Git** — [git-scm.com](https://git-scm.com/)

Optional (for full features):
- **Gemini API key** — [aistudio.google.com](https://aistudio.google.com/) (free tier available)
- **Razorpay account** — [razorpay.com](https://razorpay.com/) (for payments)

---

## Local Development Setup (Windows PowerShell)

### Backend Setup

```powershell
# Navigate to project root
cd C:\Users\Akshay\.gemini\antigravity\scratch\ai-excel-insights\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If activation is blocked by execution policy, run first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Copy environment template
Copy-Item .env.example .env

# Edit .env with your settings (MongoDB URI, AI key, etc.)
# At minimum, set MONGODB_URI if MongoDB is running locally:
# MONGODB_URI=mongodb://localhost:27017

# Start the backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# The API is now running at: http://127.0.0.1:8000
# Swagger docs at:           http://127.0.0.1:8000/docs
# ReDoc at:                  http://127.0.0.1:8000/redoc
```

### Frontend Setup

```powershell
# Navigate to frontend directory
cd C:\Users\Akshay\.gemini\antigravity\scratch\ai-excel-insights\frontend

# Install dependencies
npm install

# Copy environment template
Copy-Item .env.example .env.local

# Start the development server
npm run dev

# The frontend is now running at: http://localhost:5173

# Build for production
npm run build
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_ENV` | No | `development` or `production` (default: `development`) |
| `API_HOST` | No | Host to bind to (default: `127.0.0.1`) |
| `API_PORT` | No | Port to listen on (default: `8000`) |
| `MONGODB_URI` | **Yes** | MongoDB connection string |
| `MONGODB_DATABASE` | No | Database name (default: `ai_excel_insights`) |
| `JWT_SECRET` | **Yes (prod)** | Random secret for JWT signing |
| `AI_PROVIDER` | No | `gemini` or `openai` (leave empty to disable AI) |
| `AI_API_KEY` | No | API key for the selected AI provider |
| `AI_MODEL` | No | Model name (e.g., `gemini-1.5-flash`) |
| `MAX_UPLOAD_MB` | No | Maximum upload size in MB (default: `20`) |
| `MAX_ROWS` | No | Maximum rows to analyze (default: `100000`) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |
| `RAZORPAY_KEY_ID` | No | Razorpay key ID (payments disabled if absent) |
| `RAZORPAY_KEY_SECRET` | No | Razorpay key secret |
| `RAZORPAY_WEBHOOK_SECRET` | No | Razorpay webhook verification secret |

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`.

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend URL (default: `http://127.0.0.1:8000`) |

---

## Running Tests

```powershell
# Ensure you're in the backend directory with venv active
cd C:\Users\Akshay\.gemini\antigravity\scratch\ai-excel-insights\backend
.\venv\Scripts\Activate.ps1

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_file_parser.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run frontend type checking
cd ..\frontend
npm run build  # Catches TypeScript errors
```

---

## API Documentation

When the backend is running, full interactive documentation is available at:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/uploads` | Upload Excel/CSV file |
| `GET` | `/api/uploads/{file_id}/sheets` | List sheets in uploaded file |
| `GET` | `/api/uploads/{file_id}/preview` | Paginated data preview |
| `POST` | `/api/analysis/{file_id}/run` | Run full analysis |
| `GET` | `/api/reports/{report_id}` | Get complete report |
| `GET` | `/api/reports/{report_id}/insights` | Get insights list |
| `GET` | `/api/reports/{report_id}/charts` | Get chart specs |
| `POST` | `/api/reports/{report_id}/chat` | Ask AI about report |
| `GET` | `/api/reports/{report_id}/export/pdf` | Download PDF report |
| `POST` | `/api/auth/register` | Register account |
| `POST` | `/api/auth/login` | Login |
| `GET` | `/api/auth/me` | Get current user |
| `GET` | `/api/billing/plans` | List subscription plans |
| `POST` | `/api/billing/checkout` | Create payment order |
| `POST` | `/api/billing/webhook` | Razorpay webhook |
| `GET` | `/api/subscriptions/me` | Current subscription |

---

## Deployment Notes

### Production Checklist

- [ ] Set `APP_ENV=production`
- [ ] Use a strong random `JWT_SECRET` (at least 32 random characters)
- [ ] Configure `CORS_ORIGINS` to your actual frontend domain
- [ ] Use MongoDB Atlas or a secured MongoDB instance
- [ ] Set `MAX_UPLOAD_MB` appropriately for your plan
- [ ] Configure a cleanup job for expired uploads (see `report_service.cleanup_expired`)
- [ ] Put the backend behind a reverse proxy (nginx) with HTTPS
- [ ] Use process manager (systemd, PM2, or Docker) for reliability
- [ ] Set up log rotation
- [ ] Configure a MongoDB backup strategy

### Docker (Coming Soon)

Dockerfile and docker-compose.yml will be added for containerized deployment.

---

## Limitations and Roadmap

### Current Limitations

- **Excel macros:** Spreadsheet macros are never executed (security feature).
- **Very large files:** Files over `MAX_UPLOAD_MB` are rejected. For files with millions of rows, row sampling is applied.
- **XLS format:** Legacy `.xls` files are supported via `xlrd` but with limited feature support.
- **Formula results:** Cached formula results are used when available; formulas themselves are not recalculated.
- **AI chat:** Requires a valid `AI_API_KEY` to be configured. Without it, a rule-based fallback is used.
- **Payment:** Razorpay integration requires an Indian business account. International payment support is a roadmap item.
- **Background processing:** Long analyses run synchronously. A task queue (Celery + Redis) is planned for large datasets.

### Roadmap

- [ ] Docker containerization
- [ ] Background task queue for large file processing
- [ ] WebSocket streaming for real-time analysis progress
- [ ] More chart types (box plots, heatmaps)
- [ ] Dataset comparison (compare two files)
- [ ] Scheduled analysis (re-run when file updates)
- [ ] Team/organization accounts
- [ ] International payment providers (Stripe)
- [ ] Data connector integrations (Google Sheets, Airtable)

---

## Privacy and Security

- Uploaded files are stored temporarily with random IDs (not original filenames).
- Files are automatically deleted after the configured retention period.
- File contents are never sent to AI providers — only aggregated statistics and column metadata.
- Passwords are hashed with bcrypt — never stored in plaintext.
- Payment processing is handled entirely by Razorpay — no card details touch our server.
- All API responses use safe error messages — no internal stack traces exposed.

> This application processes data that users choose to upload. Review our Privacy Policy for details on data handling.

---

*Built with ❤️ for nontechnical users who deserve to understand their data.*
