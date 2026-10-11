import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart3,
  Upload,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Lock,
  MessageSquare,
  FileSpreadsheet,
  Download,
  AlertCircle,
  HelpCircle,
  ChevronDown,
} from 'lucide-react'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'

export const LandingPage: React.FC = () => {
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(null)

  const toggleFaq = (index: number) => {
    setOpenFaqIndex(openFaqIndex === index ? null : index)
  }

  const faqs = [
    {
      q: 'What spreadsheet formats are supported?',
      a: 'We support Microsoft Excel files (.xlsx, .xls) and standard comma-separated value (.csv) files up to 50 MB in size.',
    },
    {
      q: 'Do I need an account to test the platform?',
      a: 'No! You can upload a file as a guest and immediately review your summary analysis. Creating a free account lets you save reports and access them anytime.',
    },
    {
      q: 'Is my spreadsheet data safe and confidential?',
      a: 'Yes. We process files securely, do not share your proprietary data with third parties, and allow you to permanently delete uploaded datasets at any time.',
    },
    {
      q: 'How does the AI assistant generate answers?',
      a: 'The AI uses statistical summaries, distribution metrics, and column correlations calculated directly from your uploaded data to provide factual answers.',
    },
    {
      q: 'Can I export the generated charts and insights?',
      a: 'Yes. You can export complete PDF summaries as well as clean CSV tables for downstream reporting or stakeholder presentations.',
    },
  ]

  return (
    <div className="min-h-screen bg-white text-gray-900 flex flex-col selection:bg-blue-100">
      {/* Navigation */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 font-bold text-xl text-gray-900">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <BarChart3 className="w-5 h-5" />
            </div>
            <span>DataPulse<span className="text-blue-600">AI</span></span>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600">
            <a href="#how-it-works" className="hover:text-gray-900 transition-colors">How It Works</a>
            <a href="#features" className="hover:text-gray-900 transition-colors">Features</a>
            <a href="#examples" className="hover:text-gray-900 transition-colors">Example Insights</a>
            <Link to="/pricing" className="hover:text-gray-900 transition-colors">Pricing</Link>
            <a href="#faq" className="hover:text-gray-900 transition-colors">FAQ</a>
          </nav>

          <div className="flex items-center gap-3">
            <Link to="/login">
              <Button variant="ghost" size="sm">Sign In</Button>
            </Link>
            <Link to="/upload">
              <Button variant="primary" size="sm">
                Try It Free
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-16 pb-20 md:pt-24 md:pb-28 overflow-hidden bg-gradient-to-b from-blue-50/50 via-white to-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-200/60 text-blue-700 text-xs font-semibold mb-6">
            <Sparkles className="w-3.5 h-3.5" />
            Instant Automated Spreadsheet Intelligence
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-gray-900 tracking-tight leading-[1.15]">
            Upload your Excel. <br className="hidden sm:inline" />
            Understand your data — <span className="text-blue-600">automatically.</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Turn dense spreadsheets and raw CSVs into clear executive KPI cards, automated trend detection, interactive visualizations, and interactive AI chat in seconds.
          </p>

          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <Link to="/upload" className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto px-8 shadow-md hover:shadow-lg">
                <Upload className="w-5 h-5 mr-2" />
                Upload Spreadsheet
              </Button>
            </Link>
            <Link to="/pricing" className="w-full sm:w-auto">
              <Button variant="secondary" size="lg" className="w-full sm:w-auto px-8">
                See Pricing
              </Button>
            </Link>
          </div>

          <p className="mt-3 text-xs text-gray-500">
            No credit card required • Supports .xlsx, .xls, .csv up to 50MB
          </p>

          {/* Clean UI Graphic Mockup */}
          <div className="mt-14 p-3 bg-gray-100/80 rounded-2xl border border-gray-200 shadow-xl max-w-4xl mx-auto">
            <div className="bg-white rounded-xl border border-gray-200 p-6 text-left">
              <div className="flex items-center justify-between pb-4 border-b border-gray-100 mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <FileSpreadsheet className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 text-sm">Q3_Sales_Performance.xlsx</h3>
                    <p className="text-xs text-gray-500">12,450 rows • 14 columns • Sheet: Transactions</p>
                  </div>
                </div>
                <Badge variant="success">Analysis Ready</Badge>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                <div className="p-4 rounded-xl bg-blue-50/50 border border-blue-100">
                  <span className="text-xs font-semibold text-gray-500">Total Net Revenue</span>
                  <div className="text-2xl font-bold text-gray-900 mt-1">₹42.8 Lakhs</div>
                  <span className="text-xs text-emerald-600 font-medium">↑ +14.2% MoM</span>
                </div>
                <div className="p-4 rounded-xl bg-purple-50/50 border border-purple-100">
                  <span className="text-xs font-semibold text-gray-500">Avg Order Value</span>
                  <div className="text-2xl font-bold text-gray-900 mt-1">₹3,450</div>
                  <span className="text-xs text-emerald-600 font-medium">↑ +5.8% MoM</span>
                </div>
                <div className="p-4 rounded-xl bg-amber-50/50 border border-amber-100">
                  <span className="text-xs font-semibold text-gray-500">Data Completeness</span>
                  <div className="text-2xl font-bold text-gray-900 mt-1">98.4%</div>
                  <span className="text-xs text-gray-500">2 minor missing fields</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-gray-50 border border-gray-200 text-xs text-gray-600 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                  <span><strong>AI Key Insight:</strong> Enterprise tier grew 28% while small-ticket customer returns dropped by 4%.</span>
                </div>
                <span className="text-blue-600 font-semibold cursor-pointer hover:underline">View Deep Dive →</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-gray-50/60 border-y border-gray-100">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">Workflow</h2>
            <h3 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              Three simple steps to clarity
            </h3>
            <p className="mt-3 text-gray-600 text-sm sm:text-base">
              No formulas, no complex pivot tables, and no configuration required.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-2xl border border-gray-200/80 shadow-sm relative">
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg mb-5">
                1
              </div>
              <h4 className="text-lg font-bold text-gray-900 mb-2">Upload File</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Drop your Excel (.xlsx, .xls) or CSV dataset. Preview sheet names, column data types, and row samples instantly.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-gray-200/80 shadow-sm relative">
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg mb-5">
                2
              </div>
              <h4 className="text-lg font-bold text-gray-900 mb-2">Automatic Analysis</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Our engine automatically identifies distributions, outliers, trends, and summary metrics across all columns.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-gray-200/80 shadow-sm relative">
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg mb-5">
                3
              </div>
              <h4 className="text-lg font-bold text-gray-900 mb-2">Get Insights & Chat</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Receive interactive visualizations, plain-language takeaway cards, downloadable reports, and an AI chat assistant.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">Capabilities</h2>
            <h3 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              Built for speed, accuracy, and clarity
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl border border-gray-200 hover:border-blue-200 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
                <Sparkles className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-gray-900 mb-2">Smart Analysis</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Calculates statistical profiles, variance, category concentrations, and time-series patterns without manual formulas.
              </p>
            </div>

            <div className="p-6 rounded-2xl border border-gray-200 hover:border-blue-200 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
                <BarChart3 className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-gray-900 mb-2">Beautiful Visualizations</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Automatically determines appropriate charts—bar charts, line graphs, distributions, and scatter plots.
              </p>
            </div>

            <div className="p-6 rounded-2xl border border-gray-200 hover:border-blue-200 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-4">
                <MessageSquare className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-gray-900 mb-2">Interactive AI Chat</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Ask natural questions like &quot;Which category saw the biggest decline?&quot; and receive answers grounded in your data.
              </p>
            </div>

            <div className="p-6 rounded-2xl border border-gray-200 hover:border-blue-200 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
                <Download className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-gray-900 mb-2">PDF & CSV Exports</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Download structured executive PDF reports and filtered CSV tables ready for team distribution or board meetings.
              </p>
            </div>

            <div className="p-6 rounded-2xl border border-gray-200 hover:border-blue-200 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center mb-4">
                <AlertCircle className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-gray-900 mb-2">Data Quality Checks</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Detects missing values, duplicated entries, corrupted data types, and potential calculation anomalies.
              </p>
            </div>

            <div className="p-6 rounded-2xl border border-gray-200 hover:border-blue-200 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
                <Lock className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-gray-900 mb-2">Privacy First</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Your spreadsheets are never used to train public machine learning models. Delete your files and reports at any time.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Example Insights Section */}
      <section id="examples" className="py-20 bg-gray-50/60 border-y border-gray-100">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">Sample Output</h2>
            <h3 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              Example Automated Insights
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              Generated in real-time from simulated datasets (clearly labeled as examples).
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <Badge variant="success">Positive Trend (Example)</Badge>
                  <span className="text-xs text-gray-400 font-medium">High confidence</span>
                </div>
                <h4 className="text-base font-semibold text-gray-900 mb-2">
                  Customer Retention Improved in Q2
                </h4>
                <div className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-1 rounded inline-block mb-2">
                  +18.4% Retention Rate
                </div>
                <p className="text-sm text-gray-600 leading-relaxed mb-3">
                  Cohorts acquired after April maintained an active rate 18.4% higher than earlier cohorts over the first 60 days.
                </p>
              </div>
              <div className="text-xs text-blue-600 italic bg-blue-50/50 p-2.5 rounded-lg border border-blue-100">
                Action: Identify onboarding factors that drove higher cohort retention.
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <Badge variant="error">Risk Detected (Example)</Badge>
                  <span className="text-xs text-gray-400 font-medium">High confidence</span>
                </div>
                <h4 className="text-base font-semibold text-gray-900 mb-2">
                  High Revenue Concentration in Top 2 Accounts
                </h4>
                <div className="text-xs font-semibold text-red-700 bg-rose-50 px-2 py-1 rounded inline-block mb-2">
                  61.2% Total Revenue
                </div>
                <p className="text-sm text-gray-600 leading-relaxed mb-3">
                  Two key accounts generate over 60% of all monthly revenue, presenting significant exposure risk if renewals stall.
                </p>
              </div>
              <div className="text-xs text-red-600 italic bg-rose-50/50 p-2.5 rounded-lg border border-rose-100">
                Action: Diversify mid-market pipeline to decrease reliance on two top clients.
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <Badge variant="warning">Anomaly (Example)</Badge>
                  <span className="text-xs text-gray-400 font-medium">Medium confidence</span>
                </div>
                <h4 className="text-base font-semibold text-gray-900 mb-2">
                  Unusual Shipping Cost Spike in August
                </h4>
                <div className="text-xs font-semibold text-amber-700 bg-amber-50 px-2 py-1 rounded inline-block mb-2">
                  +340% Standard Deviation
                </div>
                <p className="text-sm text-gray-600 leading-relaxed mb-3">
                  Logistics expenses in region North surged disproportionately during week 33 without a corresponding bump in units shipped.
                </p>
              </div>
              <div className="text-xs text-amber-700 italic bg-amber-50/50 p-2.5 rounded-lg border border-amber-100">
                Action: Cross-examine freight carrier invoices for August expedited delivery charges.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section className="py-20 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">Pricing</h2>
            <h3 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              Simple, transparent pricing in ₹ INR
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              Start free. Upgrade as your dataset volume and team analysis needs grow.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl border border-gray-200 bg-white flex flex-col justify-between">
              <div>
                <h4 className="font-bold text-gray-900 text-lg">Free</h4>
                <div className="mt-4 mb-4">
                  <span className="text-3xl font-extrabold text-gray-900">₹0</span>
                  <span className="text-xs text-gray-500"> / forever</span>
                </div>
                <p className="text-xs text-gray-500 mb-6">Explore the tool with quick spreadsheet summaries.</p>
                <ul className="space-y-3 text-sm text-gray-600 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>3 reports per month</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Up to 10 MB file size</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Automated KPI cards & charts</span>
                  </li>
                </ul>
              </div>
              <Link to="/upload">
                <Button variant="secondary" className="w-full">Start Free</Button>
              </Link>
            </div>

            <div className="p-6 rounded-2xl border-2 border-blue-600 bg-blue-50/20 flex flex-col justify-between relative shadow-md">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-[11px] font-bold px-3 py-0.5 rounded-full uppercase tracking-wider">
                Most Popular
              </div>
              <div>
                <h4 className="font-bold text-gray-900 text-lg">Pro</h4>
                <div className="mt-4 mb-4">
                  <span className="text-3xl font-extrabold text-gray-900">₹999</span>
                  <span className="text-xs text-gray-500"> / month</span>
                </div>
                <p className="text-xs text-gray-500 mb-6">For analysts, operators, and founders who work with data regularly.</p>
                <ul className="space-y-3 text-sm text-gray-600 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Unlimited reports</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Up to 50 MB file size</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Unlimited AI Analyst Q&A</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Full PDF & CSV exports</span>
                  </li>
                </ul>
              </div>
              <Link to="/pricing">
                <Button variant="primary" className="w-full">Upgrade to Pro</Button>
              </Link>
            </div>

            <div className="p-6 rounded-2xl border border-gray-200 bg-white flex flex-col justify-between">
              <div>
                <h4 className="font-bold text-gray-900 text-lg">Single Report</h4>
                <div className="mt-4 mb-4">
                  <span className="text-3xl font-extrabold text-gray-900">₹149</span>
                  <span className="text-xs text-gray-500"> / one-time</span>
                </div>
                <p className="text-xs text-gray-500 mb-6">Instant one-off deep analysis for urgent presentations.</p>
                <ul className="space-y-3 text-sm text-gray-600 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>1 comprehensive report</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Up to 50 MB file size</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Executive PDF export</span>
                  </li>
                </ul>
              </div>
              <Link to="/pricing">
                <Button variant="secondary" className="w-full">Buy 1 Report</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-20 bg-gray-50/60 border-y border-gray-100">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">Answers</h2>
            <h3 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              Frequently Asked Questions
            </h3>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => {
              const isOpen = openFaqIndex === index
              return (
                <div
                  key={index}
                  className="bg-white rounded-xl border border-gray-200/80 overflow-hidden transition-colors"
                >
                  <button
                    onClick={() => toggleFaq(index)}
                    className="w-full p-5 text-left flex items-center justify-between font-semibold text-gray-900 text-sm sm:text-base hover:text-blue-600"
                  >
                    <span>{faq.q}</span>
                    <ChevronDown
                      className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
                        isOpen ? 'rotate-180 text-blue-600' : ''
                      }`}
                    />
                  </button>
                  {isOpen && (
                    <div className="px-5 pb-5 pt-1 text-sm text-gray-600 leading-relaxed border-t border-gray-50">
                      {faq.a}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-12 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2 font-bold text-gray-900 text-sm">
            <div className="w-6 h-6 rounded-md bg-blue-600 flex items-center justify-center text-white text-xs">
              <BarChart3 className="w-3.5 h-3.5" />
            </div>
            <span>DataPulseAI</span>
          </div>

          <div className="flex items-center gap-6 text-xs text-gray-500">
            <Link to="/pricing" className="hover:text-gray-900">Pricing</Link>
            <Link to="/upload" className="hover:text-gray-900">Upload Data</Link>
            <a href="#faq" className="hover:text-gray-900">FAQ</a>
            <span>Privacy & Security</span>
            <span>Terms of Service</span>
          </div>

          <p className="text-xs text-gray-400">
            © {new Date().getFullYear()} DataPulseAI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
