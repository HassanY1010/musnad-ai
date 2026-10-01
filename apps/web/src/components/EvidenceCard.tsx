import { BookOpen, Award, CheckCircle, ShieldAlert, FileText, Hash } from 'lucide-react'
import type { EvidenceItem } from '@/types'

interface EvidenceCardProps {
  evidence: EvidenceItem
  index?: number
  isConflicting?: boolean
}

export default function EvidenceCard({ evidence, isConflicting = false }: EvidenceCardProps) {
  const isQuran = evidence.source_type === 'quran'

  return (
    <div
      style={{
        padding: '18px 20px',
        borderRadius: '14px',
        backgroundColor: isConflicting ? 'rgba(239, 68, 68, 0.08)' : 'var(--color-bg-card)',
        border: `1.5px solid ${isConflicting ? 'rgba(239, 68, 68, 0.4)' : 'var(--color-border)'}`,
        marginBottom: '14px',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)',
      }}
    >
      {/* Evidence Source Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            padding: '6px',
            borderRadius: '8px',
            backgroundColor: isConflicting ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
            color: isConflicting ? 'var(--color-conflict)' : 'var(--color-primary-bright)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <BookOpen size={16} />
          </div>
          <div>
            <span style={{ fontWeight: 800, fontSize: '0.96rem', color: '#FFFFFF' }}>
              {evidence.source_title_ar || evidence.source_title}
            </span>
          </div>
          <span
            style={{
              fontSize: '0.74rem',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '6px',
              backgroundColor: 'var(--color-bg-elevated)',
              color: 'var(--color-primary-bright)',
              border: '1px solid var(--color-border)',
              letterSpacing: '0.5px',
            }}
          >
            {evidence.source_code}
          </span>
        </div>

        {evidence.exact_match && (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              fontSize: '0.78rem',
              color: 'var(--color-emerald)',
              fontWeight: 700,
              backgroundColor: 'rgba(16, 185, 129, 0.12)',
              padding: '3px 10px',
              borderRadius: '999px',
              border: '1px solid rgba(16, 185, 129, 0.3)',
            }}
          >
            <CheckCircle size={14} />
            مطابقة لفظية تامة
          </span>
        )}
      </div>

      {/* Primary Evidence Passage */}
      <div
        className={isQuran ? 'quran-text' : 'hadith-text'}
        style={{
          padding: '16px 20px',
          borderRadius: '10px',
          backgroundColor: 'var(--color-bg-primary)',
          borderRight: `4px solid ${isConflicting ? 'var(--color-conflict)' : 'var(--color-primary-light)'}`,
          borderTop: '1px solid var(--color-border)',
          borderBottom: '1px solid var(--color-border)',
          borderLeft: '1px solid var(--color-border)',
          marginBottom: '14px',
          fontSize: isQuran ? '1.35rem' : '1.2rem',
          lineHeight: '2.1',
          color: '#FFFFFF',
          boxShadow: 'inset 0 2px 6px rgba(0, 0, 0, 0.3)',
        }}
      >
        « {evidence.text} »
      </div>

      {/* Provenance Metadata Details */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '10px',
          fontSize: '0.82rem',
        }}
      >
        {evidence.chapter && (
          <div style={{
            padding: '4px 10px',
            borderRadius: '6px',
            backgroundColor: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-secondary)',
          }}>
            <span style={{ color: 'var(--color-text-muted)' }}>الباب/السورة: </span>
            <strong style={{ color: '#FFFFFF' }}>{evidence.chapter}</strong>
          </div>
        )}
        {evidence.surah_number && evidence.verse_number && (
          <div style={{
            padding: '4px 10px',
            borderRadius: '6px',
            backgroundColor: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-secondary)',
          }}>
            <span style={{ color: 'var(--color-text-muted)' }}>الآية: </span>
            <strong style={{ color: '#FFFFFF' }}>{evidence.verse_number}</strong>
          </div>
        )}
        {evidence.hadith_number && (
          <div style={{
            padding: '4px 10px',
            borderRadius: '6px',
            backgroundColor: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-secondary)',
          }}>
            <span style={{ color: 'var(--color-text-muted)' }}>رقم الحديث: </span>
            <strong style={{ color: '#FFFFFF' }}>{evidence.hadith_number}</strong>
          </div>
        )}
        {evidence.grading && (
          <div style={{
            padding: '4px 10px',
            borderRadius: '6px',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: 'var(--color-primary-bright)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px',
            fontWeight: 600,
          }}>
            <Award size={14} />
            <span>درجة الحديث: {evidence.grading}</span>
            {evidence.grading_authority && <span style={{ opacity: 0.85 }}>({evidence.grading_authority})</span>}
          </div>
        )}
        {evidence.edition && (
          <div style={{
            padding: '4px 10px',
            borderRadius: '6px',
            backgroundColor: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-secondary)',
          }}>
            <span style={{ color: 'var(--color-text-muted)' }}>الطبعة: </span>
            <span style={{ color: '#FFFFFF' }}>{evidence.edition}</span>
          </div>
        )}
      </div>
    </div>
  )
}
