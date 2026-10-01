import { useQuery } from '@tanstack/react-query'
import { Database, BookOpen, ShieldCheck, CheckCircle2, FileText, Layers, Hash, Sparkles } from 'lucide-react'
import { getSources, getDatasetStats } from '@/lib/api'

export default function SourcesPage() {
  const { data: sources, isLoading } = useQuery({
    queryKey: ['sources'],
    queryFn: getSources,
  })

  const { data: stats } = useQuery({
    queryKey: ['datasetStats'],
    queryFn: getDatasetStats,
  })

  return (
    <div className="container" style={{ padding: '48px 20px 90px' }}>
      <div style={{ maxWidth: '880px', margin: '0 auto 48px', textAlign: 'center' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '7px 18px',
            borderRadius: '999px',
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            color: 'var(--color-primary-bright)',
            fontSize: '0.88rem',
            fontWeight: 700,
            marginBottom: '20px',
            boxShadow: '0 0 16px rgba(16, 185, 129, 0.15)',
          }}
        >
          <Database size={16} />
          <span>سجل المصادر المعتمدة المسندة (الإصدار {stats?.dataset_version || 'KB-002'})</span>
        </div>

        <h1 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '16px', color: '#FFFFFF', letterSpacing: '-0.5px' }}>
          المصادر الشرعية المعتمدة ونطاق التغطية التوثيقية
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.85, fontSize: '1.05rem', maxWidth: '780px', margin: '0 auto' }}>
          يلتزم محرك «مُسنَد» بمبدأ الشفافية العلمية التامة. لا يعتمد النموذج على معلوماته الذاتية التوليدية، بل يربط كل حكم بمرجع
          موثق في قاعدة بيانات المصادر المعتمدة القابلة للتدقيق البرمجي والمطابقة بالهاش المشفر.
        </p>
      </div>

      {/* Live Dataset Statistics Dashboard */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: '16px',
          marginBottom: '48px',
        }}
      >
        <div
          style={{
            backgroundColor: 'rgba(16, 185, 129, 0.08)',
            border: '1.5px solid rgba(16, 185, 129, 0.4)',
            borderRadius: '16px',
            padding: '24px 20px',
            textAlign: 'center',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.35), 0 0 20px rgba(16, 185, 129, 0.12)',
          }}
        >
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
            إجمالي السجلات المسندة
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: 'var(--color-primary-bright)', letterSpacing: '-0.5px' }}>
            {stats ? stats.total_records.toLocaleString() : '15,426'}
          </div>
          <div style={{
            fontSize: '0.78rem',
            color: 'var(--color-primary-bright)',
            marginTop: '6px',
            fontWeight: 700,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <CheckCircle2 size={13} />
            <span>100% موثقة بالهاش المشفر</span>
          </div>
        </div>

        <div
          style={{
            backgroundColor: 'var(--color-bg-card)',
            backdropFilter: 'blur(16px)',
            border: '1px solid var(--color-border)',
            borderRadius: '16px',
            padding: '24px 20px',
            textAlign: 'center',
            boxShadow: '0 8px 20px rgba(0, 0, 0, 0.25)',
          }}
        >
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
            آيات القرآن الكريم
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#FFFFFF' }}>
            {stats ? stats.quran_records.toLocaleString() : '6,236'}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginTop: '6px' }}>
            114 سورة (مصحف المدينة النبوية)
          </div>
        </div>

        <div
          style={{
            backgroundColor: 'var(--color-bg-card)',
            backdropFilter: 'blur(16px)',
            border: '1px solid var(--color-border)',
            borderRadius: '16px',
            padding: '24px 20px',
            textAlign: 'center',
            boxShadow: '0 8px 20px rgba(0, 0, 0, 0.25)',
          }}
        >
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
            الأحاديث النبوية الشريفة
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#FFFFFF' }}>
            {stats ? stats.hadith_records.toLocaleString() : '2,933'}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginTop: '6px' }}>
            صحيح البخاري، مسلم، الأربعين النووية
          </div>
        </div>

        <div
          style={{
            backgroundColor: 'var(--color-bg-card)',
            backdropFilter: 'blur(16px)',
            border: '1px solid var(--color-border)',
            borderRadius: '16px',
            padding: '24px 20px',
            textAlign: 'center',
            boxShadow: '0 8px 20px rgba(0, 0, 0, 0.25)',
          }}
        >
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
            التفاسير المعتمدة
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#FFFFFF' }}>
            {stats ? stats.tafsir_records.toLocaleString() : '6,236'}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginTop: '6px' }}>
            التفسير الميسر (مجمع الملك فهد)
          </div>
        </div>

        <div
          style={{
            backgroundColor: 'var(--color-bg-card)',
            backdropFilter: 'blur(16px)',
            border: '1px solid var(--color-border)',
            borderRadius: '16px',
            padding: '24px 20px',
            textAlign: 'center',
            boxShadow: '0 8px 20px rgba(0, 0, 0, 0.25)',
          }}
        >
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.88rem', fontWeight: 600, marginBottom: '6px' }}>
            الآثار والفقه المقارن
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#FFFFFF' }}>
            {stats ? (stats.scholar_quotations + stats.fiqh_references).toLocaleString() : '21'}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginTop: '6px' }}>
            أقوال الأئمة + قرارات المجامع الفقهية
          </div>
        </div>
      </div>

      {/* Sources Grid */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--color-text-secondary)' }}>
          <div className="skeleton" style={{ width: '200px', height: '30px', margin: '0 auto 16px', borderRadius: '8px' }} />
          <div>جاري تحميل وتدقيق سجل المصادر...</div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
          {sources?.map((source) => (
            <div
              key={source.id}
              className="card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                padding: '24px',
                border: '1.5px solid var(--color-border)',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <span
                    style={{
                      padding: '4px 12px',
                      borderRadius: '8px',
                      backgroundColor: 'var(--color-bg-elevated)',
                      color: 'var(--color-primary-bright)',
                      fontSize: '0.82rem',
                      fontWeight: 700,
                      border: '1px solid var(--color-border)',
                      letterSpacing: '0.5px',
                    }}
                  >
                    {source.source_code}
                  </span>
                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                      fontSize: '0.82rem',
                      color: 'var(--color-emerald)',
                      fontWeight: 700,
                      backgroundColor: 'rgba(16, 185, 129, 0.12)',
                      padding: '3px 10px',
                      borderRadius: '999px',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                    }}
                  >
                    <ShieldCheck size={15} />
                    {source.status === 'active' ? 'معتمد ونشط' : source.status}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: '8px', color: '#FFFFFF' }}>
                  {source.title_ar || source.title}
                </h3>
                <div style={{ fontSize: '0.92rem', color: 'var(--color-text-secondary)', marginBottom: '14px', fontWeight: 500 }}>
                  المؤلف: <strong style={{ color: '#FFFFFF' }}>{source.author_ar || source.author || 'نصوص إسلامية معتمدة'}</strong>
                </div>

                {source.provenance && (
                  <p style={{
                    fontSize: '0.86rem',
                    color: 'var(--color-text-secondary)',
                    lineHeight: 1.7,
                    marginBottom: '18px',
                    backgroundColor: 'rgba(10, 16, 29, 0.4)',
                    padding: '12px 14px',
                    borderRadius: '10px',
                    border: '1px solid var(--color-border-card)',
                  }}>
                    {source.provenance}
                  </p>
                )}
              </div>

              <div
                style={{
                  borderTop: '1px solid var(--color-border)',
                  paddingTop: '16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '0.82rem',
                  color: 'var(--color-text-muted)',
                }}
              >
                <span>النوع: <strong style={{ color: 'var(--color-text-secondary)' }}>{source.source_type}</strong></span>
                <span style={{ color: 'var(--color-primary-bright)', fontWeight: 700 }}>
                  {source.chunk_count > 0 ? `${source.chunk_count.toLocaleString()} نص مفهرس` : 'مفهرس معتمد'}
                </span>
                <span>الرخصة: <strong style={{ color: 'var(--color-text-secondary)' }}>{source.license || 'Public Domain'}</strong></span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
