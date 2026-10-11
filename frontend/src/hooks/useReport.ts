import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { reportsAPI } from '../services/api'
import { Report } from '../types'

export function useReport(reportId: string) {
  return useQuery({
    queryKey: ['report', reportId],
    queryFn: async () => {
      const res = await reportsAPI.get(reportId)
      return res.data as Report
    },
    enabled: !!reportId,
    refetchInterval: (query) => {
      const data = query.state.data
      return data?.status === 'processing' ? 2000 : false
    },
  })
}

export function useReports() {
  return useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await reportsAPI.list()
      return res.data as Report[]
    },
  })
}

export function useDeleteReport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (reportId: string) => reportsAPI.delete(reportId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['reports'] }),
  })
}
