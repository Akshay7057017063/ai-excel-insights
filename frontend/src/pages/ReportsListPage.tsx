import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useReports, useDeleteReport } from '../hooks/useReport'
import { useAuth } from '../context/AuthContext'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import EmptyState from '../components/ui/EmptyState'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import {
  FileSpreadsheet,
  Trash2,
  ExternalLink,
  Upload,
  Calendar,
  Layers,
  Sparkles,
  AlertCircle,
} from 'lucide-react'
import toast from 'react-hot-toast'

export const ReportsListPage: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const { data: reports, isLoading, isError, refetch } = useReports()
  const deleteMutation = useDeleteReport()
  const [reportToDelete, setReportToDelete] = useState<string | null>(null)

  const handleDelete = async (reportId: string) => {
    try {
      await deleteMutation.mutateAsync(reportId)
      toast.success('Report deleted')
      setReportToDelete(null)
    } catch {
      toast.error('Failed to delete report')
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <LoadingSpinner size="lg" label="Loading your reports..." />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Reports</h1>
          <p className="text-sm text-gray-500 mt-1">
            Access, view, and manage all your generated dataset analyses
          </p>
        </div>

        <Link to="/upload">
          <Button variant="primary">
            <Upload className="w-4 h-4 mr-2" />
            Upload New File
          </Button>
        </Link>
      </div>

      {!isAuthenticated && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="text-xs">
            <strong className="font-semibold">Notice for Guest Users:</strong> Reports created in guest mode are tied to your browser session. To ensure you never lose access to your reports across devices, please{' '}
            <Link to="/register" className="font-bold underline text-amber-950">
              create a free account
            </Link>
            .
          </div>
        </div>
      )}

      {/* Reports List */}
      {!reports || reports.length === 0 ? (
        <EmptyState
          icon={<FileSpreadsheet className="w-6 h-6 text-blue-600" />}
          title="No reports created yet"
          message="Upload your first Excel or CSV file to generate instant KPI cards, charts, and automated findings."
          action={
            <Link to="/upload">
              <Button variant="primary">Upload Spreadsheet</Button>
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((report) => (
            <div
              key={report.id}
              className="bg-white rounded-xl border border-gray-200/80 p-5 shadow-sm hover:border-blue-300 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <Badge
                    variant={
                      report.status === 'ready'
                        ? 'success'
                        : report.status === 'processing'
                        ? 'warning'
                        : 'error'
                    }
                  >
                    {report.status}
                  </Badge>
                  <span className="text-[11px] text-gray-400 capitalize">
                    {report.dataset_type || 'Tabular Data'}
                  </span>
                </div>

                <h3 className="text-base font-semibold text-gray-900 line-clamp-1 mb-1">
                  {report.name}
                </h3>
                <p className="text-xs text-gray-500 mb-4">
                  Sheet: {report.sheet_name}
                </p>

                <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 py-3 border-y border-gray-100 mb-4">
                  <div className="flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-gray-400" />
                    <span>{report.row_count?.toLocaleString() || 0} rows</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-gray-400" />
                    <span>{new Date(report.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between gap-2 pt-1">
                <Link to={`/app/reports/${report.id}`} className="flex-1">
                  <Button variant="secondary" size="sm" className="w-full text-xs">
                    <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
                    View Report
                  </Button>
                </Link>

                {reportToDelete === report.id ? (
                  <div className="flex items-center gap-1">
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(report.id)}
                      loading={deleteMutation.isPending}
                      className="text-xs px-2"
                    >
                      Confirm
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setReportToDelete(null)}
                      className="text-xs px-2"
                    >
                      Cancel
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setReportToDelete(report.id)}
                    className="text-gray-400 hover:text-red-600 px-2"
                    title="Delete report"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ReportsListPage
