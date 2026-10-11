import React, { useState, useRef, DragEvent, ChangeEvent } from 'react'
import { UploadCloud, FileSpreadsheet, AlertCircle, CheckCircle2 } from 'lucide-react'
import Button from '../ui/Button'
import ProgressBar from '../ui/ProgressBar'

export interface FileUploadZoneProps {
  onFileSelect: (file: File) => void
  isLoading?: boolean
  uploadProgress?: number
  error?: string | null
  maxSizeMb?: number
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({
  onFileSelect,
  isLoading = false,
  uploadProgress = 0,
  error = null,
  maxSizeMb = 50,
}) => {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const allowedExtensions = ['.xlsx', '.xls', '.csv']

  const validateAndHandle = (file: File) => {
    setValidationError(null)
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!allowedExtensions.includes(ext)) {
      setValidationError(`Invalid file type. Please upload a .xlsx, .xls, or .csv file.`)
      return
    }

    const maxSizeBytes = maxSizeMb * 1024 * 1024
    if (file.size > maxSizeBytes) {
      setValidationError(`File is too large. Maximum supported size is ${maxSizeMb} MB.`)
      return
    }

    setSelectedFile(file)
    onFileSelect(file)
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    if (isLoading) return

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndHandle(e.dataTransfer.files[0])
    }
  }

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndHandle(e.target.files[0])
    }
  }

  const triggerBrowse = () => {
    if (isLoading) return
    fileInputRef.current?.click()
  }

  const currentError = validationError || error

  return (
    <div className="w-full">
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.xls,.csv"
        className="hidden"
        onChange={handleFileInputChange}
        disabled={isLoading}
      />

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={!selectedFile || !isLoading ? triggerBrowse : undefined}
        className={`relative flex flex-col items-center justify-center p-8 md:p-12 border-2 border-dashed rounded-2xl transition-all cursor-pointer text-center ${
          isDragging
            ? 'border-blue-500 bg-blue-50/70 scale-[1.01]'
            : currentError
            ? 'border-red-300 bg-red-50/30'
            : selectedFile
            ? 'border-emerald-300 bg-emerald-50/20'
            : 'border-gray-300 hover:border-blue-400 bg-white hover:bg-gray-50/60'
        }`}
      >
        <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 shadow-sm">
          {selectedFile ? (
            <FileSpreadsheet className="w-8 h-8 text-emerald-600" />
          ) : (
            <UploadCloud className="w-8 h-8 text-blue-600" />
          )}
        </div>

        {selectedFile ? (
          <div className="space-y-2 max-w-md w-full">
            <div className="flex items-center justify-center gap-2 text-sm font-semibold text-gray-900">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span className="truncate">{selectedFile.name}</span>
            </div>
            <p className="text-xs text-gray-500">
              {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
            </p>

            {isLoading && (
              <div className="pt-2 w-full">
                <ProgressBar
                  progress={uploadProgress}
                  label="Uploading file..."
                  showPercentage={true}
                />
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-gray-900">
              Drag & drop your Excel or CSV file here
            </h3>
            <p className="text-sm text-gray-500">
              Supports .xlsx, .xls, and .csv files up to {maxSizeMb} MB
            </p>
            <div className="pt-2">
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  triggerBrowse()
                }}
              >
                or browse files
              </Button>
            </div>
          </div>
        )}
      </div>

      {currentError && (
        <div className="mt-3 flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-200">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{currentError}</span>
        </div>
      )}
    </div>
  )
}

export default FileUploadZone
