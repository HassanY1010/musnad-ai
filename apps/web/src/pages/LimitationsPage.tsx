import { AlertTriangle, ShieldCheck, Scale, HelpCircle, Shield, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function LimitationsPage() {
  const limitations = [
    {
      title: 'مُسنَد ليس مفتياً ولا يُصدر فتاوى شرعية',
      desc: 'النظام أداة تدقيق وإسناد مصادري وليست هيئة إفتاء. المسائل الفقهية الاجتهادية والنوازل المعاصرة تحال فوراً إلى العلماء والمجامع الفقهية المعتمدة.',
      icon: <Scale size={24} color="#F87171" />,
      accent: 'rgba(239, 68, 68, 0.15)',
      border: 'rgba(239, 68, 68, 0.35)',
    },
    {
      title: 'النموذج اللغوي (LLM) ليس مصدراً للحقيقة',
      desc: 'الذكاء الاصطناعي يُستخدم حصراً في استخراج الادعاءات والمطابقة اللفظية والدلالية، بينما نتائج التحقق تُحسم عبر محرك قواعد قطعي (Deterministic Rules) مستند إلى النصوص الأصلية.',
      icon: <ShieldCheck size={24} color="#34D399" />,
      accent: 'rgba(16, 185, 129, 0.15)',
      border: 'rgba(16, 185, 129, 0.35)',
    },
    {
      title: 'التوقف والامتناع عند غياب الدليل (Abstention)',
      desc: 'عند عدم العثور على شاهد نصي في المصادر المتاحة، لا يلفق النظام دليلاً ولا يؤكد صحة النص أو بطلانه، بل يُصرّح بـ "دليل غير كافٍ" أو "يحتاج مراجعة" التزاماً بالأمانة العلمية.',
      icon: <HelpCircle size={24} color="#FBBF24" />,
      accent: 'rgba(245, 158, 11, 0.15)',
      border: 'rgba(245, 158, 11, 0.35)',
    },
    {
      title: 'نطاق قاعدة البيانات الحالي (MVP Coverage)',
      desc: 'تغطي النسخة الحالية (KB-002) القرآن الكريم كاملاً، وصحيحي البخاري ومسلم، والتفسير الميسر، ومختارات من الأربعين النووية والآثار. عدم وجود الحديث في النظام لا يعني بالضرورة عدم وروده في دواوين السنة الأخرى.',
      icon: <AlertTriangle size={24} color="#60A5FA" />,
      accent: 'rgba(59, 130, 246, 0.15)',
      border: 'rgba(59, 130, 246, 0.35)',
    },
  ]

  return (
    <div className="container" style={{ padding: '48px 20px 90px', maxWidth: '880px' }}>
      <div style={{ textAlign: 'center', marginBottom: '44px' }}>
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
          }}
        >
          <Shield size={16} />
          <span>ميثاق الشفافية والمسؤولية العلمية</span>
        </div>

        <h1 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '16px', color: '#FFFFFF', letterSpacing: '-0.5px' }}>
          حدود النظام ومبدأ الشفافية العلمية
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.85, fontSize: '1.05rem', maxWidth: '720px', margin: '0 auto' }}>
          التحقق من المحتوى الديني أمانة علمية وشرعية عظمى. نوضح هنا بكل جلاء ما يفعله «مُسنَد» وما لا يفعله تجنباً لأي لبس وتكريساً لمبدأ الذكاء الاصطناعي المسؤول.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '18px', marginBottom: '40px' }}>
        {limitations.map((item, idx) => (
          <div
            key={idx}
            className="card"
            style={{
              padding: '26px',
              border: '1.5px solid var(--color-border)',
              display: 'flex',
              gap: '22px',
              alignItems: 'flex-start',
            }}
          >
            <div
              style={{
                padding: '14px',
                borderRadius: '14px',
                backgroundColor: item.accent,
                border: `1px solid ${item.border}`,
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {item.icon}
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '8px', color: '#FFFFFF' }}>
                {item.title}
              </h3>
              <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.8, fontSize: '0.96rem' }}>
                {item.desc}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div style={{ textAlign: 'center' }}>
        <Link to="/" className="btn btn-primary btn-lg">
          <span>العودة إلى محرك التحقق</span>
          <ArrowLeft size={18} />
        </Link>
      </div>
    </div>
  )
}
