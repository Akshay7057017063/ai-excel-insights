import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUpload } from '../hooks/useUpload'
import FileUploadZone from '../components/upload/FileUploadZone'
import SheetSelector from '../components/upload/SheetSelector'
import DataPreviewTable from '../components/upload/DataPreviewTable'
import Button from '../components/ui/Button'
import ErrorMessage from '../components/ui/ErrorMessage'
import { useAuth } from '../context/AuthContext'
import { Check, Sparkles, FileText, ArrowRight, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export const UploadPage: React.FC = () => {
  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [reportName, setReportName] = useState('')
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const {
    uploadResponse,
    preview,
    selectedSheet,
    isUploading,
    isAnalyzing,
    uploadProgress,
    error,
    setSelectedSheet,
    uploadFile,
    loadPreview,
    runAnalysis,
  } = useUpload()

  const handleFileSelect = async (file: File) => {
    try {
      const resp = await uploadFile(file)
      // default report name based on file name
      const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ')
      setReportName(cleanName.charAt(0).toUpperCase() + cleanName.slice(1))
      if (resp.sheets && resp.sheets.length > 0) {
        setStep(2)
      }
    } catch {
      // error handled in hook
    }
  }

  const handleSheetSelect = async (sheetName: string) => {
    setSelectedSheet(sheetName)
    if (uploadResponse) {
      await loadPreview(uploadResponse.file_id, sheetName, 1)
    }
  }

  const handlePageChange = async (newPage: number) => {
    if (uploadResponse && selectedSheet) {
      await loadPreview(uploadResponse.file_id, selectedSheet, newPage)
    }
  }

  const handleStartAnalysis = async () => {
    try {
      const finalName = reportName.trim() || 'Spreadsheet Analysis Report'
      const reportId = await runAnalysis(finalName)
      toast.success('Analysis started!')
      navigate(`/app/reports/${reportId}`)
    } catch {
      // Handled in hook
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Page Title & Guest banner */}
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          Upload & Analyze Dataset
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Generate full statistical KPIs, automated trend insights, and interactive charts.
        </p>

        {!isAuthenticated && (
          <div className="mt-4 p-3 rounded-xl bg-blue-50/70 border border-blue-200/80 flex items-center justify-between text-xs text-blue-800">
            <span className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600 flex-shrink-0" />
              <span>
                <strong>Guest Mode:</strong> You can upload and analyze files without logging in. Create a free account to permanently save your reports.
              </span>
            </span>
          </div>
        )}
      </div>

      {/* Stepper Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between max-w-lg mx-auto relative">
          <div className="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-0.5 bg-gray-200 -z-0" />

          {/* Step 1 */}
          <div className="flex flex-col items-center relative z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-colors ${
                step > 1
                  ? 'bg-blue-600 text-white'
                  : step === 1
                  ? 'bg-blue-600 text-white ring-4 ring-blue-100'
                  : 'bg-white border-2 border-gray-300 text-gray-400'
              }`}
            >
              {step > 1 ? <Check className="w-5 h-5 stroke-[2.5]" /> : '1'}
            </div>
            <span className="text-xs font-medium text-gray-700 mt-2">Upload</span>
          </div>

          {/* Step 2 */}
          <div className="flex flex-col items-center relative z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-colors ${
                step > 2
                  ? 'bg-blue-600 text-white'
                  : step === 2
                  ? 'bg-blue-600 text-white ring-4 ring-blue-100'
                  : 'bg-white border-2 border-gray-300 text-gray-400'
              }`}
            >
              {step > 2 ? <Check className="w-5 h-5 stroke-[2.5]" /> : '2'}
            </div>
            <span className="text-xs font-medium text-gray-700 mt-2">Select Sheet</span>
          </div>

          {/* Step 3 */}
          <div className="flex flex-col items-center relative z-10">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-colors ${
                step === 3
                  ? 'bg-blue-600 text-white ring-4 ring-blue-100'
                  : 'bg-white border-2 border-gray-300 text-gray-400'
              }`}
            >
              3
            </div>
            <span className="text-xs font-medium text-gray-700 mt-2">Analyze</span>
          </div>
        </div>
      </div>

      {/* Step Contents */}
      {step === 1 && (
        <div className="max-w-2xl mx-auto">
          <FileUploadZone
            onFileSelect={handleFileSelect}
            isLoading={isUploading}
            uploadProgress={uploadProgress}
            error={error}
          />
        </div>
      )}

      {step === 2 && uploadResponse && (
        <div className="space-y-6">
          <SheetSelector
            sheets={uploadResponse.sheets}
            selectedSheet={selectedSheet}
            onSelect={handleSheetSelect}
            onConfirm={() => setStep(3)}
          />

          {preview && (
            <DataPreviewTable
              preview={preview}
              onPageChange={handlePageChange}
            />
          )}

          <div className="flex justify-between items-center pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setStep(1)}
            >
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              Upload different file
            </Button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="max-w-xl mx-auto bg-white rounded-2xl border border-gray-200/80 p-6 sm:p-8 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
            <FileText className="w-6 h-6" />
          </div>

          <h3 className="text-lg font-bold text-gray-900 mb-1">
            Ready to generate report
          </h3>
          <p className="text-xs text-gray-500 mb-6">
            Customize the name for your report before starting automated analysis.
          </p>

          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                Report Name
              </label>
              <input
                type="text"
                value={reportName}
                onChange={(e) => setReportName(e.target.value)}
                placeholder="e.g. Q3 Sales Analysis"
                className="w-full px-3.5 py-2.5 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="p-3.5 rounded-xl bg-gray-50 border border-gray-200/70 text-xs text-gray-600 space-y-1">
              <p><strong>Selected Sheet:</strong> {selectedSheet}</p>
              <p><strong>Dataset File:</strong> {uploadResponse?.original_name}</p>
            </div>
          </div>

          {error && <ErrorMessage message={error} className="mb-4" />}

          <div className="flex items-center justify-between gap-3 pt-2">
            <Button
              variant="secondary"
              onClick={() => setStep(2)}
              disabled={isAnalyzing}
            >
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              Back
            </Button>

            <Button
              variant="primary"
              onClick={handleStartAnalysis}
              loading={isAnalyzing}
              disabled={isAnalyzing}
            >
              <span>Run Automated Analysis</span>
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default UploadPage
