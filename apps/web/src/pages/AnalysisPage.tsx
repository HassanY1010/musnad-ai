import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Download, AlertTriangle, CheckCircle, Info, Sparkles, Shield, Database, Cpu } from 'lucide-react'
import { getAnalysis } from '@/lib/api'
import ClaimCard from '@/components/ClaimCard'

function SummaryCard({ label, value, color, icon }: { label: string; value: number; color?: string; icon?: string }) {
  return (
    <div className="summary-stat">
      {icon && <div style={{ fontSize: '1.2rem', marginBottom: '4px' }}>{icon}</div>}
      <div className="summary-stat-value" style={{ color: color || 'var(--color-text-primary)' }}>
        {value}
      </div>
      <div className="summary-stat-label">{label}</div>
    </div>
  )
}

function AnalysisSkeleton() {
  return (
    <div style={{ padding: '40px 0' }}>
      <div style={{ marginBottom: '24px' }}>
        <div className="skeleton" style={{ height: '32px', width: '240px', marginBottom: '12px', borderRadius: '8px' }} />
        <div className="skeleton" style={{ height: '18px', width: '360px', borderRadius: '6px' }} />
      </div>
      <div className="summary-grid" style={{ marginBottom: '32px' }}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: '110px', borderRadius: '14px' }} />
        ))}
      </div>
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height: '90px', borderRadius: '16px', marginBottom: '14px' }} />
      ))}
    </div>
  )
}

function EmptyState() {
  return (
    <div className="card" style={{ textAlign: 'center', padding: '60px 24px', margin: '20px 0' }}>
      <div style={{ fontSize: '3.5rem', marginBottom: '16px' }}>🔍</div>
      <h3 style={{ marginBottom: '10px', color: '#FFFFFF', fontSize: '1.3rem' }}>لم يتم اكتشاف ادعاءات مستقلة</h3>
      <p style={{ fontSize: '0.95rem', lineHeight: 1.8, color: 'var(--color-text-secondary)', maxWidth: '520px', margin: '0 auto' }}>
        لم يتعرف محرك الاستخراج على ادعاءات إسلامية أو نصوص قابلة للتحقق في النص المُدخَل.
        حاول إدخال نصوص تتضمن أحاديث نبوية، آيات قرآنية، أو أقوالاً فقهية صريحة.
      </p>
    </div>
  )
}

export default function AnalysisPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['analysis', id],
    queryFn: () => getAnalysis(id!),
    enabled: !!id,
    staleTime: Infinity,
  })

  if (isLoading) {
    return (
      <div className="container-narrow" style={{ paddingTop: '40px' }}>
        <AnalysisSkeleton />
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="container-narrow" style={{ paddingTop: '60px', textAlign: 'center' }}>
        <div className="card" style={{ padding: '40px', maxWidth: '600px', margin: '0 auto' }}>
          <AlertTriangle size={52} style={{ color: 'var(--color-conflict)', margin: '0 auto 16px' }} />
          <h2 style={{ marginBottom: '10px', color: '#FFFFFF' }}>تعذر استرجاع نتائج التحليل</h2>
          <p style={{ color: 'var(--color-text-secondary)', marginBottom: '24px', lineHeight: 1.7 }}>
            {error instanceof Error ? error.message : 'حدث خطأ أثناء تحميل سجل التحليل من الخادم'}
          </p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            <ArrowRight size={18} />
            <span>العودة إلى الصفحة الرئيسية</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container-narrow" style={{ paddingTop: '36px', paddingBottom: '70px' }}>
      {/* Back button */}
      <button
        className="btn btn-ghost btn-sm"
        onClick={() => navigate('/')}
        style={{ marginBottom: '24px', gap: '8px' }}
      >
        <ArrowRight size={16} />
        <span>إجراء تحليل وتدقيق جديد</span>
      </button>

      {/* Analysis Header Card */}
      <div className="card" style={{ marginBottom: '28px', padding: '24px', border: '1.5px solid var(--color-border)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Shield size={20} color="var(--color-primary-bright)" />
              <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: '#FFFFFF' }}>
                تقرير التحقق وتتبع الإسناد
              </h1>
            </div>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '10px' }}>
              <span style={{
                fontSize: '0.8rem',
                color: 'var(--color-primary-bright)',
                backgroundColor: 'rgba(16, 185, 129, 0.12)',
                padding: '3px 10px',
                borderRadius: '6px',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
              }}>
                <Database size={13} />
                قاعدة المعرفة: {analysis.kb_version}
              </span>
              <span style={{
                fontSize: '0.8rem',
                color: 'var(--color-text-secondary)',
                backgroundColor: 'var(--color-bg-elevated)',
                padding: '3px 10px',
                borderRadius: '6px',
                border: '1px solid var(--color-border)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
              }}>
                <Cpu size={13} />
                النموذج: {analysis.model}
              </span>
              <span style={{
                fontSize: '0.78rem',
                color: 'var(--color-text-muted)',
                fontFamily: 'var(--font-mono)',
                padding: '3px 8px',
              }}>
                ID: {analysis.analysis_id.slice(0, 8)}...
              </span>
            </div>
          </div>

          <button
            className="btn btn-secondary btn-sm"
            onClick={() => {
              const blob = new Blob([JSON.stringify(analysis, null, 2)], { type: 'application/json' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `musnad-${analysis.analysis_id.slice(0, 8)}.json`
              a.click()
            }}
          >
            <Download size={15} />
            <span>تصدير تقرير JSON</span>
          </button>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="summary-grid" style={{ marginBottom: '28px' }}>
        <SummaryCard label="إجمالي الادعاءات" value={analysis.summary.total} />
        <SummaryCard
          label="مدعوم بالدليل"
          value={analysis.summary.supported}
          color="var(--color-supported)"
          icon="✓"
        />
        <SummaryCard
          label="مدعوم جزئياً"
          value={analysis.summary.partially_supported}
          color="var(--color-partial)"
          icon="◐"
        />
        <SummaryCard
          label="يحتاج مراجعة"
          value={analysis.summary.needs_review}
          color="var(--color-review)"
          icon="⚠"
        />
        <SummaryCard
          label="دليل غير كافٍ"
          value={analysis.summary.insufficient_evidence}
          color="var(--color-insufficient)"
          icon="∅"
        />
        <SummaryCard
          label="إحالة لمختص"
          value={analysis.summary.specialist_referral}
          color="var(--color-specialist)"
          icon="⚖"
        />
      </div>

      {/* Special notices */}
      {analysis.summary.has_exact_matches && (
        <div className="limitations-banner" style={{
          marginBottom: '16px',
          background: 'rgba(16, 185, 129, 0.1)',
          borderColor: 'rgba(16, 185, 129, 0.4)',
        }}>
          <CheckCircle size={18} style={{ color: 'var(--color-emerald)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong style={{ color: '#FFFFFF' }}>تطابق لفظي تام: </strong>
            <span style={{ color: 'var(--color-text-secondary)' }}>
              تم العثور على مطابقة حرفية تامة لأحد الادعاءات في مصادر قاعدة المعرفة المعتمدة.
            </span>
          </div>
        </div>
      )}

      {analysis.summary.has_conflicts && (
        <div className="limitations-banner" style={{
          marginBottom: '16px',
          background: 'rgba(239, 68, 68, 0.1)',
          borderColor: 'rgba(239, 68, 68, 0.4)',
        }}>
          <AlertTriangle size={18} style={{ color: 'var(--color-conflict)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong style={{ color: '#FFFFFF' }}>تنبيه تعارض في الأدلة: </strong>
            <span style={{ color: 'var(--color-text-secondary)' }}>
              تم اكتشاف تعارض في رواية أو نسبة هذا النص بين المصادر. النظام يعرض التعارض بشفافية ولا يرجح تلقائياً.
            </span>
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="limitations-banner" style={{
        marginBottom: '32px',
        background: 'rgba(30, 41, 59, 0.6)',
        borderColor: 'var(--color-border)',
      }}>
        <Info size={18} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--color-primary-bright)' }} />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
          هذه النتائج مستندة إلى المصادر المفهرسة في {analysis.kb_version}. «مُسنَد» محرك تدقيق وإسناد مصادري ولا يصدر فتاوى شرعية.
        </span>
      </div>

      {/* Claims List */}
      {analysis.claims.length === 0 ? (
        <EmptyState />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {analysis.claims.map((claim, i) => (
            <ClaimCard key={claim.claim_id} claim={claim} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}
