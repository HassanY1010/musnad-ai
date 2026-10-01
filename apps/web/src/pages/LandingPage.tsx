import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Search, CheckCircle } from 'lucide-react';
import { Header } from '../components/layout/Header';

export const LandingPage = () => {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header />
      
      <main style={{ flex: 1 }}>
        {/* Hero Section */}
        <section className="container" style={{ paddingTop: '80px', paddingBottom: '80px', textAlign: 'center' }}>
          <div className="hero-badge" style={{ margin: '0 auto 24px' }}>
            <Shield size={18} />
            <span>AI Evidence & Verification Engine</span>
          </div>
          <h1 className="hero-title" style={{ fontSize: 'clamp(2.5rem, 5vw, 4rem)' }}>
            الذكاء الاصطناعي الذي لا يفتي،<br />
            <span className="text-gradient">بل يتحقق.</span>
          </h1>
          <p className="hero-subtitle" style={{ fontSize: '1.25rem', marginTop: '24px' }}>
            محرك ذكي للتحقق من المحتوى الإسلامي الرقمي، يربط كل ادعاء بالدليل والمصدر، ويَمتنع عن الإجابة عندما لا يتوفر دليل كافٍ.
          </p>
          
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '40px' }}>
            <Link to="/register" className="btn btn-primary btn-lg" style={{ fontSize: '1.1rem', padding: '14px 32px' }}>
              ابدأ التحقق الآن
            </Link>
            <Link to="/login" className="btn btn-secondary btn-lg" style={{ fontSize: '1.1rem', padding: '14px 32px' }}>
              تسجيل الدخول
            </Link>
          </div>
        </section>

        {/* Process Section */}
        <section className="container" style={{ padding: '80px 0', borderTop: '1px solid var(--color-border)' }}>
          <div style={{ textAlign: 'center', marginBottom: '64px' }}>
            <h2 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '16px' }}>كيف يعمل مُسنَد؟</h2>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto' }}>
              منهجية علمية صارمة تمر بـ 6 مراحل لضمان الموثوقية
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
            {[
              { num: '01', title: 'Claim', desc: 'تحليل النص واستخراج الادعاءات الأساسية بدقة.' },
              { num: '02', title: 'Retrieval', desc: 'البحث الشامل داخل قواعد المعرفة الإسلامية الموثوقة.' },
              { num: '03', title: 'Evidence', desc: 'العثور على الأدلة والنصوص المطابقة للادعاء.' },
              { num: '04', title: 'Source', desc: 'تحديد الكتاب، المؤلف، ورقم الصفحة بشكل قاطع.' },
              { num: '05', title: 'Deterministic Status', desc: 'إصدار الحكم عبر محرك قواعد لا يمكن تخطيه.' },
              { num: '06', title: 'Abstention', desc: 'الامتناع الآمن عند غياب الأدلة الكافية.' }
            ].map((step, i) => (
              <div key={i} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <span style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--color-primary-bright)', opacity: 0.8 }}>{step.num}</span>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 700 }}>{step.title}</h3>
                <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section className="container" style={{ padding: '80px 0', borderTop: '1px solid var(--color-border)' }}>
          <div style={{ textAlign: 'center', marginBottom: '64px' }}>
            <h2 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '16px' }}>مميزات النظام</h2>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto' }}>
              بنية تحتية مصممة للتحقق وليس للتخمين
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
            <div className="card">
              <Search size={32} style={{ color: 'var(--color-primary)', marginBottom: '16px' }} />
              <h3 style={{ fontSize: '1.2rem', marginBottom: '8px' }}>Hybrid Search</h3>
              <p style={{ color: 'var(--color-text-secondary)' }}>دمج بين المطابقة النصية الدقيقة والبحث الدلالي المتقدم لضمان الدقة.</p>
            </div>
            <div className="card">
              <CheckCircle size={32} style={{ color: 'var(--color-primary)', marginBottom: '16px' }} />
              <h3 style={{ fontSize: '1.2rem', marginBottom: '8px' }}>Deterministic Verification</h3>
              <p style={{ color: 'var(--color-text-secondary)' }}>الحكم النهائي مستمد من قواعد صلبة، وليس بناءً على هلوسات النموذج اللغوي.</p>
            </div>
            <div className="card">
              <Shield size={32} style={{ color: 'var(--color-primary)', marginBottom: '16px' }} />
              <h3 style={{ fontSize: '1.2rem', marginBottom: '8px' }}>Safe Abstention</h3>
              <p style={{ color: 'var(--color-text-secondary)' }}>الامتناع الآمن عن إصدار حكم عند عدم توفر أدلة في قاعدة المعرفة المعتمدة.</p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section style={{ background: 'linear-gradient(to right, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.2))', padding: '80px 0', textAlign: 'center' }}>
          <div className="container">
            <h2 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '24px' }}>جاهز للتحقق من المحتوى؟</h2>
            <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
              <Link to="/register" className="btn btn-primary btn-lg">ابدأ باستخدام مُسنَد</Link>
              <Link to="/login" className="btn btn-secondary btn-lg">لدي حساب بالفعل</Link>
            </div>
          </div>
        </section>
      </main>

      <footer style={{ padding: '40px 0', borderTop: '1px solid var(--color-border)', textAlign: 'center', backgroundColor: 'var(--color-bg-elevated)' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
          <div style={{ textAlign: 'right' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-primary-bright)' }}>مُسنَد</h2>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>AI Evidence & Verification Engine</p>
          </div>
          <div style={{ display: 'flex', gap: '24px' }}>
            <Link to="/" style={{ color: 'var(--color-text-secondary)', textDecoration: 'none' }}>الرئيسية</Link>
            <Link to="/login" style={{ color: 'var(--color-text-secondary)', textDecoration: 'none' }}>تسجيل الدخول</Link>
            <Link to="/register" style={{ color: 'var(--color-text-secondary)', textDecoration: 'none' }}>إنشاء حساب</Link>
          </div>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
            &copy; 2026 MUSNAD AI
          </div>
        </div>
      </footer>
    </div>
  );
};
