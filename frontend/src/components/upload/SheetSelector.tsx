import React from 'react'
import { SheetInfo } from '../../types'
import { FileSpreadsheet, ArrowRight, Check } from 'lucide-react'
import Button from '../ui/Button'

export interface SheetSelectorProps {
  sheets: SheetInfo[]
  selectedSheet: string
  onSelect: (sheetName: string) => void
  onConfirm: () => void
  isLoading?: boolean
}

export const SheetSelector: React.FC<SheetSelectorProps> = ({
  sheets,
  selectedSheet,
  onSelect,
  onConfirm,
  isLoading = false,
}) => {
  return (
    <div className="bg-white rounded-xl border border-gray-200/80 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-gray-900">Select Sheet</h3>
          <p className="text-sm text-gray-500">
            Choose which sheet from your workbook you want to analyze
          </p>
        </div>
        <span className="text-xs bg-blue-50 text-blue-700 font-medium px-2.5 py-1 rounded-full border border-blue-100">
          {sheets.length} {sheets.length === 1 ? 'Sheet' : 'Sheets'} found
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-6">
        {sheets.map((sheet) => {
          const isSelected = selectedSheet === sheet.name
          return (
            <div
              key={sheet.name}
              onClick={() => onSelect(sheet.name)}
              className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? 'border-blue-500 bg-blue-50/50 ring-2 ring-blue-500/20'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50/60'
              }`}
            >
              <div className="flex items-center gap-3 min-w-0">
                <div
                  className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    isSelected ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate">
                    {sheet.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {sheet.row_count.toLocaleString()} rows • {sheet.col_count} cols
                  </p>
                </div>
              </div>
              <div
                className={`w-5 h-5 rounded-full border flex items-center justify-center ml-2 flex-shrink-0 transition-colors ${
                  isSelected
                    ? 'border-blue-600 bg-blue-600 text-white'
                    : 'border-gray-300 bg-white'
                }`}
              >
                {isSelected && <Check className="w-3.5 h-3.5 stroke-[3]" />}
              </div>
            </div>
          )
        })}
      </div>

      <div className="flex justify-end">
        <Button
          onClick={onConfirm}
          disabled={!selectedSheet || isLoading}
          loading={isLoading}
          className="w-full sm:w-auto"
        >
          <span>Continue to Analysis</span>
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </div>
  )
}

export default SheetSelector
