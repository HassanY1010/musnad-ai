import { Link, useLocation } from 'react-router-dom'
import { Shield, BookOpen, AlertTriangle, CheckCircle, Database } from 'lucide-react'

export default function Header() {
  const location = useLocation()

  const navLinks = [
    { to: '/', label: 'الرئيسية والتحقق' },
    { to: '/sources', label: 'المصادر وقاعدة المعرفة' },
    { to: '/limitations', label: 'حدود النموذج والشفافية' },
  ]

  return (
    <header
      style={{
        borderBottom: '1px solid var(--color-border)',
        backgroundColor: 'rgba(7, 11, 20, 0.85)',
        backdropFilter: 'blur(16px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '74px',
        }}
      >
        <Link
          to="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            textDecoration: 'none',
          }}
        >
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #10B981 0%, #047857 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 18px rgba(16, 185, 129, 0.35)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
            }}
          >
            <Shield size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{
              fontWeight: 900,
              fontSize: '1.45rem',
              letterSpacing: '-0.5px',
              color: '#FFFFFF',
              lineHeight: 1.1,
            }}>
              مُـسْـنَـد
            </div>
            <div style={{
              fontSize: '0.68rem',
              color: 'var(--color-primary-bright)',
              letterSpacing: '0.8px',
              fontWeight: 700,
            }}>
              MUSNAD AI VERIFICATION
            </div>
          </div>
        </Link>

        {/* Center / Right Navigation */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <nav style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {navLinks.map((link) => {
              const isActive = location.pathname === link.to
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  style={{
                    padding: '8px 18px',
                    borderRadius: '10px',
                    textDecoration: 'none',
                    fontSize: '0.92rem',
                    fontWeight: isActive ? 700 : 500,
                    color: isActive ? '#FFFFFF' : 'var(--color-text-secondary)',
                    backgroundColor: isActive ? 'rgba(16, 185, 129, 0.18)' : 'transparent',
                    border: isActive ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid transparent',
                    boxShadow: isActive ? '0 0 14px rgba(16, 185, 129, 0.15)' : 'none',
                    transition: 'all 0.2s ease',
                  }}
                >
                  {link.label}
                </Link>
              )
            })}
          </nav>

          {/* Engine Status Badge */}
          <div
            style={{
              display: 'none', // Shown on desktop via media or inline
              alignItems: 'center',
              gap: '8px',
              padding: '6px 12px',
              borderRadius: '999px',
              backgroundColor: 'rgba(16, 185, 129, 0.08)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              fontSize: '0.78rem',
              color: 'var(--color-primary-bright)',
              fontWeight: 600,
            }}
            className="engine-status-pill"
          >
            <div
              style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                backgroundColor: '#10B981',
                boxShadow: '0 0 8px #10B981',
              }}
            />
            <span>المحرك نشط (KB-002)</span>
          </div>
        </div>
      </div>
    </header>
  )
}
