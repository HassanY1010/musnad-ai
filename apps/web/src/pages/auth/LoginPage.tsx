import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ShieldAlert, Mail, Lock, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('يرجى تعبئة جميع الحقول');
      return;
    }
    
    setIsSubmitting(true);
    try {
      await login({ email, password });
      navigate('/app');
    } catch (err: any) {
      toast.error(err.response?.data?.detail?.message || 'تعذر تسجيل الدخول، يرجى التأكد من بياناتك');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-layout" style={{ minHeight: '100vh', display: 'flex' }}>
      <div className="auth-sidebar" style={{ flex: 1, backgroundColor: 'var(--color-bg-elevated)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: '40px', borderLeft: '1px solid var(--color-border)' }}>
        <div className="hero-badge" style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldAlert size={20} />
          <span>الذكاء الاصطناعي الآمن</span>
        </div>
        <h1 className="hero-title" style={{ fontSize: '2.5rem', marginBottom: '16px' }}>مُسنَد</h1>
        <p className="hero-subtitle" style={{ textAlign: 'center' }}>محرك ذكي للتحقق من المحتوى الإسلامي الرقمي</p>
      </div>
      <div className="auth-content" style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
        <div className="card" style={{ width: '100%', maxWidth: '420px', padding: '40px' }}>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '8px' }}>مرحباً بعودتك</h2>
          <p style={{ color: 'var(--color-text-secondary)', marginBottom: '32px' }}>سجل دخولك للمتابعة إلى مُسنَد</p>
          
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="input-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.9rem', fontWeight: 600 }}>البريد الإلكتروني</label>
              <div style={{ position: 'relative' }}>
                <Mail size={18} style={{ position: 'absolute', right: '16px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="analysis-input-area" 
                  style={{ width: '100%', padding: '12px 42px 12px 16px', borderRadius: '12px', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-input)', color: 'white', marginBottom: 0, outline: 'none' }}
                  placeholder="name@example.com"
                  dir="ltr"
                />
              </div>
            </div>
            
            <div className="input-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.9rem', fontWeight: 600 }}>كلمة المرور</label>
              <div style={{ position: 'relative' }}>
                <Lock size={18} style={{ position: 'absolute', right: '16px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="analysis-input-area" 
                  style={{ width: '100%', padding: '12px 42px 12px 16px', borderRadius: '12px', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-input)', color: 'white', marginBottom: 0, outline: 'none' }}
                  placeholder="••••••••"
                  dir="ltr"
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary btn-lg" disabled={isSubmitting} style={{ width: '100%', marginTop: '12px' }}>
              {isSubmitting ? <Loader2 className="animate-spin" /> : 'تسجيل الدخول'}
            </button>
          </form>

          <div style={{ marginTop: '32px', textAlign: 'center', borderTop: '1px solid var(--color-border)', paddingTop: '24px' }}>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>
              ليس لديك حساب؟ <Link to="/register" style={{ color: 'var(--color-primary-bright)', textDecoration: 'none', fontWeight: 600 }}>إنشاء حساب جديد</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
