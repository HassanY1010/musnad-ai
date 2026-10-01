import axios from 'axios'
import type { AnalysisResult, SourceItem } from '@/types'

// Use explicit backend URL or relative /api/v1 if proxied
const API_BASE = import.meta.env.VITE_API_URL || 'https://musnad-ai.onrender.com/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

export async function createAnalysis(content: string): Promise<AnalysisResult> {
  try {
    const response = await apiClient.post<{ success: boolean; data: AnalysisResult }>('/analyses', {
      content,
    })
    return response.data.data
  } catch (err: any) {
    console.error('Analysis creation error:', err)
    if (err.response?.data?.error?.message) {
      throw new Error(err.response.data.error.message)
    }
    if (err.message) {
      throw new Error(err.message)
    }
    throw new Error('تعذر الاتصال بالخادم الخلفي. تأكد من تشغيل الخادم على المنفذ 8000')
  }
}

export async function getAnalysis(analysisId: string): Promise<AnalysisResult> {
  const response = await apiClient.get<{ success: boolean; data: AnalysisResult }>(`/analyses/${analysisId}`)
  return response.data.data
}

export interface DatasetStats {
  dataset_version: string
  build_timestamp: string
  total_records: number
  quran_records: number
  hadith_records: number
  tafsir_records: number
  scholar_quotations: number
  fiqh_references: number
  verified_sources_count: number
  unverified_sources_count: number
  integrity_hash: string
}

export async function getSources(): Promise<SourceItem[]> {
  const response = await apiClient.get<{ success: boolean; data: { total: number; sources: SourceItem[] } }>('/sources')
  return response.data.data.sources
}

export async function getSource(sourceCode: string): Promise<SourceItem> {
  const response = await apiClient.get<{ success: boolean; data: SourceItem }>(`/sources/${sourceCode}`)
  return response.data.data
}

export async function getDatasetStats(): Promise<DatasetStats> {
  const response = await apiClient.get<{ success: boolean; data: DatasetStats }>('/sources/stats')
  return response.data.data
}
