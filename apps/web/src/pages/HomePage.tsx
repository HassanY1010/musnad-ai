import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Loader2, Zap, Shield, Search, BookOpen, AlertCircle, Sparkles, CheckCircle2, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import { createAnalysis } from '@/lib/api'

// Demo scenarios for competition and live testing
const DEMO_SCENARIOS = [
  {
    label: 'آية قرآنية كريمة',
    tag: 'قرآن كريم',
    tagColor: '#10B981',
    icon: '📖',
    text: 'قال الله تعالى في سورة الإخلاص: قل هو الله أحد الله الصمد لم يلد ولم يولد ولم يكن له كفواً أحد',
    description: 'التحقق من نص قرآني كامل واسترجاع السورة والآية ومطابقتها نصياً بالرسم العثماني.',
  },
  {
    label: 'حديث نبوي مسند',
    tag: 'حديث صحيح',
    tagColor: '#3B82F6',
    icon: '📜',
    text: 'قال النبي ﷺ: إنما الأعمال بالنيات وإنما لكل امرئ ما نوى',
    description: 'التحقق من صحة الحديث وتتبع إسناده وموضعه ورقم الحديث في صحيح البخاري وصحيح مسلم.',
  },
  {
    label: 'ادعاء جزئي مركب',
    tag: 'فحص إسناد',
    tagColor: '#F59E0B',
    icon: '🔍',
    text: 'قال النبي صلى الله عليه وسلم: خير الناس من تعلم القرآن وعلمه، وهذا الحديث في صحيح البخاري',
    description: 'ادعاء يحتوي على شق صحيح وآخر يحتاج إلى تدقيق المصدر واللفظ في دواوين السنة.',
  },
  {
    label: 'دليل غير كافٍ (امتناع)',
    tag: 'توقف وشفافية',
    tagColor: '#94A3B8',
    icon: '⚠️',
    text: 'قال النبي ﷺ: من صلى في يوم الجمعة مئة مرة على النبي، نورت قلبه وأحاط الله به الملائكة',
    description: 'اختبار مبدأ الامتناع الصارم عند عدم وجود إسناد صحيح في قاعدة المعرفة المعتمدة.',
  },
  {
    label: 'تعارض في العزو',
    tag: 'كشف التعارض',
    tagColor: '#EC4899',
    icon: '⚖️',
    text: 'قال رسول الله ﷺ: لا ضرر ولا ضرار، وهذا الحديث صحيح رواه البخاري ومسلم في كتاب الإيمان',
    description: 'الحديث صحيح ومشهور لكنه غير مخرج في الصحيحين؛ يكتشف النظام خطأ نسبة الرواية.',
  },
]

export default function HomePage() {
  const [content, setContent] = useState('')
  const navigate = useNavigate()

  const mutation = useMutation({
    mutationFn: createAnalysis,
    onSuccess: (data) => {
      navigate(`/analysis/${data.analysis_id}`)
    },
    onError: (err: Error) => {
      toast.error(err.message || 'تعذر إجراء التحليل. يرجى المحاولة مرة أخرى.')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = content.trim()
    if (!trimmed) {
      toast.error('يرجى إدخال نص للتحقق منه أو اختيار أحد السيناريوهات التجريبية بالأسفل')
      const el = document.getElementById('content-input')
      if (el) el.focus()
      return
    }
    if (trimmed.length < 10) {
      toast.error('النص قصير جداً (أقل من 10 أحرف). يرجى إدخال نص أو حديث أطول للتحقق')
      return
    }
    mutation.mutate(trimmed)
  }

  const loadDemo = (text: string) => {
    setContent(text)
    toast.success('تم تحميل النص التجريبي بنجاح! انقر الآن على زر التحليل')
    // Smooth scroll to input
    const el = document.getElementById('content-input')
    if (el) {
      el.focus()
    }
  }

  return (
    <div>
      {/* Hero Section */}
      <div className="hero">
        <div className="container-narrow">
          <div className="hero-badge">
            <Shield size={16} />
            <span>محرك التحقق من المحتوى الإسلامي الرقمي القائم على الأدلة والمصادر</span>
          </div>

          <h1 className="hero-title">
            <span className="text-gradient">مُـسْـنَـد</span>
            <div style={{
              fontSize: '0.38em',
              color: 'var(--color-primary-bright)',
              fontWeight: 600,
              letterSpacing: '1.5px',
              marginTop: '4px',
              textTransform: 'uppercase',
            }}>
              MUSNAD AI — Islamic Content Verification Engine
            </div>
          </h1>

          <p className="hero-subtitle">
            استخرج الادعاءات، وفكك النصوص، وتحقق من صحة الأحاديث والآيات والأقوال عبر <strong>البحث الهجين وقواعد التحقق القطعية</strong> مع ربط كل نتيجة برقم المصدر وإسناده الموثق.
          </p>

          {/* Core Architecture Highlights */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '14px',
            marginBottom: '40px',
          }}>
            {[
              {
                icon: <Search size={20} />,
                title: 'بحث هجين ثلاثي الطبقات',
                desc: 'تطابق حرفي تام + بحث معجمي BM25 + بحث دلالي بالمتجهات',
              },
              {
                icon: <Shield size={20} />,
                title: 'قواعد حتمية قطعية',
                desc: 'المحرك البرمجي يبت في الحكم — والذكاء يشرح ولا يفتي',
              },
              {
                icon: <BookOpen size={20} />,
                title: 'إسناد مصدري كامل 100%',
                desc: 'كل نتيجة مرتبطة برقم المصدر والباب والصفحة والهاش المشفر',
              },
            ].map((f, i) => (
              <div key={i} className="feature-card">
                <div style={{
                  display: 'inline-flex',
                  padding: '10px',
                  borderRadius: '12px',
                  backgroundColor: 'rgba(16, 185, 129, 0.12)',
                  color: 'var(--color-primary-bright)',
                  marginBottom: '10px',
                }}>
                  {f.icon}
                </div>
                <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '6px' }}>
                  {f.title}
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                  {f.desc}
                </div>
              </div>
            ))}
          </div>

          {/* Analysis Main Input Box */}
          <form onSubmit={handleSubmit}>
            <div className="analysis-input-area">
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '14px',
                paddingBottom: '12px',
                borderBottom: '1px solid var(--color-border)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={18} color="var(--color-primary-bright)" />
                  <span style={{ fontWeight: 700, fontSize: '1rem', color: '#FFFFFF' }}>
                    أدخل النص أو الادعاء للتحقق من إسناده:
                  </span>
                </div>
                <span style={{
                  fontSize: '0.78rem',
                  padding: '3px 10px',
                  borderRadius: '999px',
                  backgroundColor: 'var(--color-bg-elevated)',
                  color: 'var(--color-text-secondary)',
                  border: '1px solid var(--color-border)',
                }}>
                  يدعم الآيات والأحاديث والأقوال
                </span>
              </div>

              <textarea
                id="content-input"
                className="textarea"
                placeholder="الصق هنا النص أو الحديث أو المقال المراد التحقق من صحته ونسبته...

مثال: قال النبي ﷺ: إنما الأعمال بالنيات وإنما لكل امرئ ما نوى، رواه البخاري في كتاب بدء الوحي."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                disabled={mutation.isPending}
                aria-label="النص المراد تحليله والتحقق منه"
              />

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderTop: '1px solid var(--color-border)',
                paddingTop: '16px',
                marginTop: '12px',
                flexWrap: 'wrap',
                gap: '12px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{
                    fontSize: '0.85rem',
                    color: content.length > 45000 ? 'var(--color-conflict)' : 'var(--color-text-secondary)',
                    fontWeight: 600,
                  }}>
                    {content.length.toLocaleString('ar-EG')} / 50,000 حرف
                  </span>
                  {content.length >= 10 && (
                    <span style={{
                      fontSize: '0.75rem',
                      color: 'var(--color-primary-bright)',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}>
                      <CheckCircle2 size={13} />
                      جاهز للتحليل
                    </span>
                  )}
                </div>

                <button
                  type="submit"
                  className="btn btn-primary btn-lg"
                  disabled={mutation.isPending}
                  id="analyze-btn"
                >
                  {mutation.isPending ? (
                    <>
                      <Loader2 size={20} className="animate-spin" />
                      <span>جارٍ فحص الإسناد والمطابقة...</span>
                    </>
                  ) : (
                    <>
                      <Zap size={20} />
                      <span>تحليل وتدقيق المحتوى الآن</span>
                      <ArrowLeft size={16} />
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>

          {/* Loading Animation & Progress Steps */}
          {mutation.isPending && (
            <div className="animate-fade-in" style={{ marginTop: '28px', textAlign: 'center' }}>
              <div className="progress-steps" style={{ justifyContent: 'center', flexWrap: 'wrap', gap: '12px' }}>
                {[
                  'استخراج الادعاءات الفردية',
                  'البحث الهجين في قاعدة المعرفة',
                  'المطابقة اللفظية والدلالية',
                  'تطبيق القواعد الحتمية والامتناع',
                  'توليد تقرير الإسناد الموثق',
                ].map((step, i) => (
                  <div key={i} className="progress-step active">
                    <div style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      background: 'var(--color-emerald)',
                      animation: 'pulse-glow 1.5s ease-in-out infinite',
                      animationDelay: `${i * 0.25}s`,
                    }} />
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Interactive Demo Scenarios */}
      <div className="container-narrow" style={{ paddingBottom: '70px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '20px',
        }}>
          <div>
            <div style={{
              fontSize: '1.25rem',
              fontWeight: 800,
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <Zap size={18} color="var(--color-gold)" />
              سيناريوهات ونماذج تجريبية للاختبار الفوري
            </div>
            <div style={{ fontSize: '0.88rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              انقر على أي نموذج لتعبئة النص فوراً وتجربة المحرك في مختلف الحالات العلمية
            </div>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '14px',
        }}>
          {DEMO_SCENARIOS.map((scenario, i) => (
            <button
              key={i}
              id={`demo-scenario-${i + 1}`}
              className="card"
              style={{
                textAlign: 'right',
                cursor: 'pointer',
                border: '1.5px solid var(--color-border)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                padding: '20px',
              }}
              onClick={() => loadDemo(scenario.text)}
              disabled={mutation.isPending}
            >
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '10px',
                }}>
                  <span style={{ fontSize: '1.4rem' }}>{scenario.icon}</span>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: '999px',
                    backgroundColor: `${scenario.tagColor}1A`,
                    color: scenario.tagColor,
                    border: `1px solid ${scenario.tagColor}40`,
                  }}>
                    {scenario.tag}
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#FFFFFF', marginBottom: '8px' }}>
                  {scenario.label}
                </div>
                <p style={{
                  fontSize: '0.84rem',
                  color: 'var(--color-text-secondary)',
                  lineHeight: 1.6,
                  marginBottom: '14px',
                }}>
                  {scenario.description}
                </p>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: 'var(--color-primary-bright)',
                borderTop: '1px solid var(--color-border-card)',
                paddingTop: '10px',
              }}>
                <span>تجربة هذا المثال</span>
                <ArrowLeft size={13} />
              </div>
            </button>
          ))}
        </div>

        {/* Responsible AI & Limitations Notice */}
        <div className="limitations-banner" style={{
          marginTop: '36px',
          borderLeft: '4px solid var(--color-emerald)',
          background: 'rgba(15, 23, 42, 0.85)',
        }}>
          <AlertCircle size={22} color="var(--color-primary-bright)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' }}>
              مبدأ الشفافية والأمانة العلمية (Responsible AI):
            </div>
            <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', lineHeight: 1.7 }}>
              نظام «مُسنَد» أداة تدقيق وإسناد مصادري، ولا يُمثل جهة إفتاء. عند غياب الدليل في المصادر المفهرسة، يتوقف النظام ويُعلن «دليل غير كافٍ» التزاماً بالأمانة العلمية.{' '}
              <a href="/limitations" style={{ color: 'var(--color-primary-bright)', fontWeight: 600, textDecoration: 'underline' }}>
                تعرّف على حدود النموذج وقواعد الشفافية ←
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
