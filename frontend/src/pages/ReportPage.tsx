import React, { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useReport } from '../hooks/useReport'
import { reportsAPI } from '../services/api'
import KPICardComponent from '../components/dashboard/KPICardComponent'
import InsightCardComponent from '../components/dashboard/InsightCardComponent'
import ChartContainer from '../components/dashboard/ChartContainer'
import ChatPanel from '../components/chat/ChatPanel'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import {
  Download,
  FileSpreadsheet,
  Calendar,
  Layers,
  CheckCircle2,
  Edit2,
  Check,
  X,
  FileDown,
  Sparkles,
} from 'lucide-react'
import toast from 'react-hot-toast'

export const ReportPage: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>()
  const { data: report, isLoading, isError, refetch } = useReport(reportId || '')

  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const [reportTitle, setReportTitle] = useState('')
  const [isExportingPdf, setIsExportingPdf] = useState(false)
  const [isExportingCsv, setIsExportingCsv] = useState(false)

  // Sync title when report loads
  React.useEffect(() => {
    if (report?.name) {
      setReportTitle(report.name)
    }
  }, [report?.name])

  const handleSaveTitle = async () => {
    if (!reportId || !reportTitle.trim()) return
    try {
      await reportsAPI.rename(reportId, reportTitle.trim())
      setIsEditingTitle(false)
      refetch()
      toast.success('Report title updated')
    } catch {
      toast.error('Failed to update title')
    }
  }

  const handleExportPdf = async () => {
    if (!reportId) return
    setIsExportingPdf(true)
    try {
      const res = await reportsAPI.exportPdf(reportId)
      const blob = new Blob([res.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${report?.name || 'report'}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('PDF download started')
    } catch {
      toast.error('Failed to export PDF')
    } finally {
      setIsExportingPdf(false)
    }
  }

  const handleExportCsv = async () => {
    if (!reportId) return
    setIsExportingCsv(true)
    try {
      const res = await reportsAPI.exportCsv(reportId, report?.sheet_name || 'sheet1')
      const blob = new Blob([res.data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${report?.name || 'dataset'}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('CSV download started')
    } catch {
      toast.error('Failed to export CSV')
    } finally {
      setIsExportingCsv(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center">
        <LoadingSpinner size="lg" label="Loading analysis report..." />
        <p className="text-xs text-gray-400 mt-2">Computing distributions and automated insights...</p>
      </div>
    )
  }

  if (isError || !report) {
    return (
      <div className="max-w-xl mx-auto py-12">
        <ErrorMessage
          title="Report Not Found"
          message="We could not locate this report or you may not have permission to view it."
          onRetry={() => refetch()}
        />
        <div className="mt-6 text-center">
          <Link to="/upload">
            <Button variant="primary">Upload New File</Button>
          </Link>
        </div>
      </div>
    )
  }

  if (report.status === 'processing') {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center max-w-md mx-auto text-center p-8 bg-white rounded-2xl border border-gray-200">
        <LoadingSpinner size="lg" label="Analyzing dataset..." />
        <h3 className="text-base font-bold text-gray-900 mt-4">Generating Insights & Charts</h3>
        <p className="text-xs text-gray-500 mt-2">
          This usually takes a few seconds. The page will automatically refresh as soon as processing finishes.
        </p>
      </div>
    )
  }

  // Calculate completeness percentage from column info
  const avgMissingPct =
    report.column_info && report.column_info.length > 0
      ? report.column_info.reduce((acc, c) => acc + (c.missing_pct || 0), 0) / report.column_info.length
      : 0
  const completenessPct = Math.max(0, Math.min(100, Math.round(100 - avgMissingPct)))

  return (
    <div className="space-y-8 pb-12">
      {/* Title & Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200/80">
        <div className="flex-1">
          {isEditingTitle ? (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                className="text-xl font-bold text-gray-900 px-3 py-1 border border-blue-500 rounded-lg focus:outline-none"
                autoFocus
              />
              <button
                onClick={handleSaveTitle}
                className="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-lg"
              >
                <Check className="w-5 h-5" />
              </button>
              <button
                onClick={() => {
                  setReportTitle(report.name)
                  setIsEditingTitle(false)
                }}
                className="p-1.5 text-gray-400 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 group">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
                {report.name}
              </h1>
              <button
                onClick={() => setIsEditingTitle(true)}
                className="text-gray-400 hover:text-gray-600 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Rename report"
              >
                <Edit2 className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="flex items-center gap-2 mt-1">
            <Badge variant="success">Ready</Badge>
            <span className="text-xs text-gray-500">Sheet: {report.sheet_name}</span>
          </div>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2.5">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleExportCsv}
            loading={isExportingCsv}
          >
            <FileSpreadsheet className="w-4 h-4 mr-1.5" />
            Export CSV
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleExportPdf}
            loading={isExportingPdf}
          >
            <Download className="w-4 h-4 mr-1.5" />
            Download PDF
          </Button>
        </div>
      </div>

      {/* Dataset Summary & Quality Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-5 rounded-2xl bg-white border border-gray-200/80 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase">Dataset Size</p>
            <p className="text-sm font-bold text-gray-900">
              {report.row_count?.toLocaleString()} rows × {report.col_count} cols
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase">Dataset Type</p>
            <p className="text-sm font-bold text-gray-900 capitalize">
              {report.dataset_type || 'General Tabular'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase">Data Quality</p>
            <p className="text-sm font-bold text-emerald-700">
              {completenessPct}% complete
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gray-100 text-gray-600 flex items-center justify-center">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase">Created</p>
            <p className="text-sm font-bold text-gray-900">
              {new Date(report.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      {report.kpis && report.kpis.length > 0 && (
        <section>
          <h2 className="text-base font-bold text-gray-900 mb-4">Key Metrics</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {report.kpis.map((kpi, idx) => (
              <KPICardComponent key={idx} card={kpi} />
            ))}
          </div>
        </section>
      )}

      {/* Insights Section */}
      {report.insights && report.insights.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-gray-900">Automated Insights & Findings</h2>
            <span className="text-xs text-gray-500 font-medium">
              {report.insights.length} findings generated
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {report.insights.map((insight) => (
              <InsightCardComponent key={insight.id} insight={insight} />
            ))}
          </div>
        </section>
      )}

      {/* Charts Section */}
      {report.charts && report.charts.length > 0 && (
        <section>
          <h2 className="text-base font-bold text-gray-900 mb-4">Visualizations</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {report.charts.map((chart) => (
              <ChartContainer key={chart.id} chart={chart} />
            ))}
          </div>
        </section>
      )}

      {/* AI Analyst Chat Section */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <h2 className="text-base font-bold text-gray-900">Ask AI Analyst</h2>
        </div>
        <ChatPanel reportId={report.id} />
      </section>
    </div>
  )
}

export default ReportPage
