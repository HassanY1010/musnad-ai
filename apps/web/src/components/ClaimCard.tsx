import { useState } from 'react'
import { ChevronDown, ChevronLeft, Shield, AlertCircle, UserCheck, Info } from 'lucide-react'
import type { ClaimResult } from '@/types'
import StatusBadge from './StatusBadge'
import EvidenceCard from './EvidenceCard'

const CLAIM_TYPE_LABELS: Record<string, string> = {
  quran_verse: 'آية قرآنية',
  hadith: 'حديث',
  scholarly_quote: 'اقتباس علمي',
  fiqh_claim: 'حكم فقهي',
  historical_claim: 'ادعاء تاريخي',
  theological_claim: 'ادعاء عقدي',
  attribution: 'نسبة قول',
  general_islamic_claim: 'ادعاء إسلامي عام',
  source_claim: 'ادعاء مصدر',
  unknown: 'غير محدد',
}

const STRENGTH_LABELS: Record<string, { label: string; color: string }> = {
  high: { label: 'عالية', color: 'var(--color-emerald)' },
  medium: { label: 'متوسطة', color: 'var(--color-review)' },
  low: { label: 'منخفضة', color: 'var(--color-conflict)' },
  none: { label: 'لا يوجد', color: 'var(--color-text-muted)' },
}

interface ClaimCardProps {
  claim: ClaimResult
  index: number
}

export default function ClaimCard({ claim, index }: ClaimCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [activeTab, setActiveTab] = useState<'evidence' | 'conflict' | 'audit'>('evidence')

  const strengthLabel = STRENGTH_LABELS[claim.evidence_strength] || STRENGTH_LABELS.none
  const sourceLabel = STRENGTH_LABELS[claim.source_traceability] || STRENGTH_LABELS.none
  const certaintyLabel = STRENGTH_LABELS[claim.interpretation_certainty] || STRENGTH_LABELS.none

  const hasEvidence = claim.supporting_evidence.length > 0
  const hasConflict = claim.conflicting_evidence.length > 0

  const statusBorderColor: Record<string, string> = {
    supported: 'rgba(16, 185, 129, 0.3)',
    partially_supported: 'rgba(59, 130, 246, 0.3)',
    needs_review: 'rgba(245, 158, 11, 0.3)',
    insufficient_evidence: 'rgba(107, 114, 128, 0.2)',
    source_conflict: 'rgba(249, 115, 22, 0.3)',
    specialist_referral: 'rgba(239, 68, 68, 0.3)',
  }

  return (
    <div
      className="claim-card"
      style={{
        borderColor: expanded ? (statusBorderColor[claim.status] || 'var(--color-border)') : undefined,
        animation: `fadeIn 0.35s ease ${index * 0.08}s both`,
      }}
    >
      {/* Header */}
      <div
        className="claim-card-header"
        onClick={() => setExpanded(!expanded)}
        role="button"
        aria-expanded={expanded}
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setExpanded(!expanded)}
      >
        <div style={{ flex: 1 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
              الادعاء {claim.claim_index + 1}
            </span>
            <span className="claim-type-badge">
              {CLAIM_TYPE_LABELS[claim.claim_type] || claim.claim_type}
            </span>
            {claim.has_exact_match && (
              <span style={{
                fontSize: '0.72rem',
                color: 'var(--color-emerald)',
                display: 'flex', alignItems: 'center', gap: '3px',
              }}>
                <Shield size={11} />
                تطابق تام
              </span>
            )}
            {claim.has_conflict && (
              <span style={{
                fontSize: '0.72rem',
                color: 'var(--color-conflict)',
                display: 'flex', alignItems: 'center', gap: '3px',
              }}>
                <AlertCircle size={11} />
                تعارض
              </span>
            )}
            {claim.needs_specialist && (
              <span style={{
                fontSize: '0.72rem',
                color: 'var(--color-specialist)',
                display: 'flex', alignItems: 'center', gap: '3px',
              }}>
                <UserCheck size={11} />
                يحتاج مختصاً
              </span>
            )}
          </div>
          <p className="claim-text">{claim.original_text}</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px', flexShrink: 0 }}>
          <StatusBadge status={claim.status} />
          <div style={{ color: 'var(--color-text-muted)', transition: 'transform 0.2s' }}>
            {expanded ? <ChevronDown size={16} /> : <ChevronLeft size={16} />}
          </div>
        </div>
      </div>

      {/* Expanded body */}
      {expanded && (
        <div className="claim-card-body animate-fade-in">

          {/* Verification Dimensions */}
          <div className="verification-result">
            <div className="verification-dimension">
              <div className="verification-dimension-label">قوة الدليل</div>
              <div className="verification-dimension-value" style={{ color: strengthLabel.color }}>
                {strengthLabel.label}
              </div>
            </div>
            <div className="verification-dimension">
              <div className="verification-dimension-label">إمكانية التتبع</div>
              <div className="verification-dimension-value" style={{ color: sourceLabel.color }}>
                {sourceLabel.label}
              </div>
            </div>
            <div className="verification-dimension">
              <div className="verification-dimension-label">يقين التفسير</div>
              <div className="verification-dimension-value" style={{ color: certaintyLabel.color }}>
                {certaintyLabel.label}
              </div>
            </div>
          </div>

          {/* Explanation */}
          {claim.explanation_ar && (
            <div style={{ marginBottom: '16px' }}>
              <div style={{
                fontSize: '0.78rem',
                color: 'var(--color-text-muted)',
                marginBottom: '6px',
                display: 'flex', alignItems: 'center', gap: '4px',
              }}>
                <Info size={12} />
                سبب الحكم
              </div>
              <p style={{ fontSize: '0.92rem', color: 'var(--color-text-secondary)', lineHeight: 1.8 }}>
                {claim.explanation_ar}
              </p>
            </div>
          )}

          {/* Abstention Notice */}
          {claim.abstention_reason && (
            <div className="abstention-notice" style={{ marginBottom: '16px' }}>
              <div className="notice-title">⚠️ ملاحظة مهمة</div>
              {claim.abstention_reason}
            </div>
          )}

          {/* Tabs */}
          {(hasEvidence || hasConflict) && (
            <>
              <div className="tabs">
                <button
                  className={`tab-btn ${activeTab === 'evidence' ? 'active' : ''}`}
                  onClick={() => setActiveTab('evidence')}
                >
                  الأدلة {hasEvidence ? `(${claim.supporting_evidence.length})` : ''}
                </button>
                {hasConflict && (
                  <button
                    className={`tab-btn ${activeTab === 'conflict' ? 'active' : ''}`}
                    onClick={() => setActiveTab('conflict')}
                  >
                    تعارض ({claim.conflicting_evidence.length})
                  </button>
                )}
                <button
                  className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
                  onClick={() => setActiveTab('audit')}
                >
                  مسار التحقق
                </button>
              </div>

              {activeTab === 'evidence' && (
                <div>
                  {hasEvidence ? (
                    claim.supporting_evidence.map((ev, i) => (
                      <EvidenceCard key={ev.chunk_id} evidence={ev} index={i} />
                    ))
                  ) : (
                    <div style={{ textAlign: 'center', padding: '24px', color: 'var(--color-text-muted)' }}>
                      لم يتم العثور على دليل في المصادر المفهرسة
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'conflict' && hasConflict && (
                <div>
                  <div className="limitations-banner" style={{ marginBottom: '12px' }}>
                    <AlertCircle size={15} style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>تنتج هذه المصادر أدلة متعارضة. النظام لا يختار تلقائياً — يُعرض التعارض للمراجعة.</span>
                  </div>
                  {claim.conflicting_evidence.map((ev, i) => (
                    <EvidenceCard key={ev.chunk_id} evidence={ev} index={i} isConflicting />
                  ))}
                </div>
              )}

              {activeTab === 'audit' && (
                <div>
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
                      القواعد المُطبَّقة في التحقق
                    </div>
                    {claim.rules_triggered.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {claim.rules_triggered.map((rule, i) => (
                          <div key={i} style={{
                            background: 'var(--color-surface)',
                            border: '1px solid var(--color-border)',
                            borderRadius: '6px',
                            padding: '8px 12px',
                            fontSize: '0.8rem',
                            fontFamily: 'var(--font-mono)',
                            color: 'var(--color-text-secondary)',
                            direction: 'ltr',
                            textAlign: 'left',
                          }}>
                            {i + 1}. {rule}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                        لا تتوفر معلومات عن القواعد المُطبَّقة
                      </div>
                    )}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '16px' }}>
                    معرّف الادعاء: <code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>{claim.claim_id}</code>
                  </div>
                </div>
              )}
            </>
          )}

          {/* No evidence at all */}
          {!hasEvidence && !hasConflict && (
            <div style={{ textAlign: 'center', padding: '24px', color: 'var(--color-text-muted)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔍</div>
              <div>لم يتم العثور على دليل في المصادر المفهرسة المتاحة</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
