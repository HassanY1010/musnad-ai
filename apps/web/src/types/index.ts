export type VerificationStatusType =
  | 'supported'
  | 'partially_supported'
  | 'needs_review'
  | 'insufficient_evidence'
  | 'source_conflict'
  | 'specialist_referral'
  | 'pending'
  | 'error'

export type VerificationStatus = VerificationStatusType

export interface EvidenceItem {
  chunk_id: string
  source_code: string
  source_title: string
  source_title_ar?: string
  source_type: string
  author?: string
  author_ar?: string
  edition?: string
  text: string
  page?: string
  chapter?: string
  hadith_number?: string
  surah_number?: number
  verse_number?: number
  reference?: string
  grading?: string
  grading_authority?: string
  exact_match?: boolean
  retrieval_method?: string
  relevance_score?: number
}

export interface ClaimResult {
  claim_id: string
  claim_index: number
  original_text: string
  normalized_text?: string
  claim_type: string
  status: VerificationStatusType
  status_label_ar: string
  status_color: string
  evidence_strength: 'high' | 'medium' | 'low' | 'none'
  source_traceability: 'high' | 'medium' | 'low' | 'none'
  interpretation_certainty: 'high' | 'medium' | 'low' | 'none'
  explanation_ar: string
  abstention_reason?: string | null
  has_exact_match: boolean
  has_conflict: boolean
  rules_triggered: string[]
  supporting_evidence: EvidenceItem[]
  conflicting_evidence: EvidenceItem[]
  needs_specialist: boolean
}

export interface AnalysisSummary {
  total: number
  supported: number
  partially_supported: number
  needs_review: number
  insufficient_evidence: number
  source_conflict: number
  specialist_referral: number
  has_exact_matches: boolean
  has_conflicts: boolean
}

export interface AnalysisResult {
  analysis_id: string
  processing_status: string
  total_claims: number
  claims: ClaimResult[]
  summary: AnalysisSummary
  language_detected: string
  kb_version: string
  model: string
}

export interface SourceItem {
  id: string
  source_code: string
  title: string
  title_ar?: string
  author?: string
  author_ar?: string
  source_type: string
  edition?: string
  publisher?: string
  year?: number
  language: string
  license?: string
  provenance?: string
  status: string
  kb_version: string
  chunk_count: number
}
