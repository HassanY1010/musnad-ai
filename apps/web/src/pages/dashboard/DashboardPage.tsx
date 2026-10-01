import React, { useState } from 'react';
import { Shield, Clock, Loader2 } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { Header } from '../../components/layout/Header';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { createAnalysis } from '../../lib/api';
import toast from 'react-hot-toast';

export const DashboardPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [content, setContent] = useState('');

  const mutation = useMutation({
    mutationFn: createAnalysis,
    onSuccess: (data) => {
      navigate(`/analysis/${data.analysis_id}`);
    },
    onError: (err: Error) => {
      toast.error(err.message || 'تعذر إجراء التحليل. يرجى المحاولة مرة أخرى.');
    },
  });

  const handleSubmit = () => {
    const trimmed = content.trim();
    if (!trimmed) {
      toast.error('يرجى إدخال نص للتحقق منه');
      return;
    }
    if (trimmed.length < 10) {
      toast.error('النص قصير جداً (أقل من 10 أحرف). يرجى إدخال نص أو حديث أطول للتحقق');
      return;
    }
    mutation.mutate(trimmed);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header />

      <main className="container" style={{ flex: 1, padding: '40px 0' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '32px' }}>
          
          <section>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '24px' }}>تحقق من محتوى</h1>
            <div className="card" style={{ padding: '32px' }}>
              <div className="input-group" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <label style={{ fontSize: '1.1rem', fontWeight: 700 }}>أدخل النص أو الادعاء الذي تريد التحقق منه...</label>
                <textarea 
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="analysis-input-area" 
                  style={{ width: '100%', minHeight: '160px', padding: '16px', borderRadius: '12px', border: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-input)', color: 'white', outline: 'none', resize: 'vertical' }}
                  placeholder="مثال: قال رسول الله صلى الله عليه وسلم: خيركم من تعلم القرآن وعلمه"
                ></textarea>
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px' }}>
                  <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={mutation.isPending}>
                    {mutation.isPending ? <Loader2 className="animate-spin" /> : 'تحقق الآن'}
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={20} />
              عمليات التحقق السابقة
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="card" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '48px', color: 'var(--color-text-muted)' }}>
                لا توجد عمليات تحقق سابقة بعد.
              </div>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
};
