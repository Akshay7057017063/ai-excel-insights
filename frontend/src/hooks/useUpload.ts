import { useState } from 'react'
import { uploadAPI, analysisAPI } from '../services/api'
import { UploadResponse, PreviewResponse } from '../types'
import toast from 'react-hot-toast'

export function useUpload() {
  const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(null)
  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [selectedSheet, setSelectedSheet] = useState<string>('')
  const [isUploading, setIsUploading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const uploadFile = async (file: File) => {
    setIsUploading(true)
    setError(null)
    try {
      const res = await uploadAPI.upload(file, setUploadProgress)
      const data: UploadResponse = res.data
      setUploadResponse(data)
      if (data.guest_token) sessionStorage.setItem('guest_token', data.guest_token)
      if (data.sheets.length > 0) {
        setSelectedSheet(data.sheets[0].name)
        await loadPreview(data.file_id, data.sheets[0].name)
      }
      return data
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Upload failed. Please try again.'
      setError(msg)
      toast.error(msg)
      throw err
    } finally {
      setIsUploading(false)
    }
  }

  const loadPreview = async (fileId: string, sheetName: string, page = 1) => {
    try {
      const res = await uploadAPI.getPreview(fileId, sheetName, page)
      setPreview(res.data)
    } catch {
      toast.error('Could not load data preview.')
    }
  }

  const runAnalysis = async (reportName: string): Promise<string> => {
    if (!uploadResponse) throw new Error('No file uploaded')
    setIsAnalyzing(true)
    setError(null)
    try {
      const res = await analysisAPI.runAnalysis(uploadResponse.file_id, {
        sheet_name: selectedSheet,
        name: reportName,
      })
      return res.data.report_id
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Analysis failed. Please try again.'
      setError(msg)
      toast.error(msg)
      throw err
    } finally {
      setIsAnalyzing(false)
    }
  }

  return {
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
  }
}
