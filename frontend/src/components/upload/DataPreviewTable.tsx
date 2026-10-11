import React from 'react'
import { PreviewResponse } from '../../types'
import { ChevronLeft, ChevronRight, Hash, Calendar, Tag, AlertTriangle } from 'lucide-react'
import Button from '../ui/Button'
import Badge from '../ui/Badge'

export interface DataPreviewTableProps {
  preview: PreviewResponse
  onPageChange: (newPage: number) => void
  isLoading?: boolean
}

export const DataPreviewTable: React.FC<DataPreviewTableProps> = ({
  preview,
  onPageChange,
  isLoading = false,
}) => {
  const { columns, rows, total_rows, page, page_size } = preview
  const totalPages = Math.max(1, Math.ceil(total_rows / page_size))

  const getColumnIcon = (col: (typeof columns)[0]) => {
    if (col.is_numeric) return <Hash className="w-3 h-3 mr-1 text-blue-600" />
    if (col.is_date) return <Calendar className="w-3 h-3 mr-1 text-emerald-600" />
    if (col.is_categorical) return <Tag className="w-3 h-3 mr-1 text-purple-600" />
    return null
  }

  const getBadgeVariant = (col: (typeof columns)[0]): 'info' | 'success' | 'warning' | 'neutral' => {
    if (col.is_numeric) return 'info'
    if (col.is_date) return 'success'
    if (col.is_categorical) return 'warning'
    return 'neutral'
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200/80 shadow-sm overflow-hidden">
      <div className="p-4 sm:p-5 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-gray-900">Data Preview</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Showing first {rows.length} rows of {total_rows.toLocaleString()} total rows across {columns.length} columns
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-rose-100 border border-rose-300"></span>
            Missing / Null
          </span>
        </div>
      </div>

      <div className="overflow-x-auto relative min-h-[220px]">
        {isLoading && (
          <div className="absolute inset-0 bg-white/70 backdrop-blur-[1px] flex items-center justify-center z-10">
            <span className="text-sm font-medium text-blue-600">Updating preview...</span>
          </div>
        )}
        <table className="w-full text-left text-xs sm:text-sm border-collapse">
          <thead>
            <tr className="bg-gray-50/80 border-b border-gray-200 text-gray-700">
              <th className="py-3 px-4 font-semibold w-12 text-gray-400">#</th>
              {columns.map((col) => (
                <th key={col.name} className="py-3 px-4 font-semibold min-w-[150px]">
                  <div className="flex flex-col gap-1.5">
                    <span className="truncate text-gray-900 font-semibold" title={col.name}>
                      {col.name}
                    </span>
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <Badge variant={getBadgeVariant(col)} className="text-[10px] py-0 px-1.5">
                        <span className="flex items-center">
                          {getColumnIcon(col)}
                          {col.inferred_type || col.dtype}
                        </span>
                      </Badge>
                      {col.missing_pct > 0 && (
                        <span
                          className="text-[10px] text-amber-600 font-medium flex items-center"
                          title={`${col.missing_pct.toFixed(1)}% missing values`}
                        >
                          <AlertTriangle className="w-2.5 h-2.5 mr-0.5" />
                          {col.missing_pct.toFixed(0)}% null
                        </span>
                      )}
                    </div>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-gray-700 font-mono text-xs">
            {rows.map((row, rowIdx) => {
              const rowNum = (page - 1) * page_size + rowIdx + 1
              return (
                <tr key={rowIdx} className="hover:bg-blue-50/20 transition-colors">
                  <td className="py-2.5 px-4 text-gray-400 select-none font-sans text-xs">
                    {rowNum}
                  </td>
                  {columns.map((col) => {
                    const value = row[col.name]
                    const isNull = value === null || value === undefined || value === ''
                    return (
                      <td
                        key={col.name}
                        className={`py-2.5 px-4 truncate max-w-[200px] ${
                          isNull ? 'bg-rose-50/50 text-rose-400 italic' : ''
                        }`}
                        title={isNull ? 'null' : String(value)}
                      >
                        {isNull ? 'null' : String(value)}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="p-4 border-t border-gray-100 bg-gray-50/50 flex items-center justify-between">
        <p className="text-xs text-gray-500">
          Page <span className="font-semibold text-gray-800">{page}</span> of{' '}
          <span className="font-semibold text-gray-800">{totalPages}</span>
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            disabled={page <= 1 || isLoading}
            onClick={() => onPageChange(page - 1)}
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Previous
          </Button>
          <Button
            variant="secondary"
            size="sm"
            disabled={page >= totalPages || isLoading}
            onClick={() => onPageChange(page + 1)}
          >
            Next
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      </div>
    </div>
  )
}

export default DataPreviewTable
