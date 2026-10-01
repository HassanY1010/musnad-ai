import { Link, useLocation } from 'react-router-dom'
import { Shield } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

export const Header = () => {
  const location = useLocation()
  const { user, logout } = useAuth()

  const navLinks = [
    { to: '/', label: 'الرئيسية' },
    { to: '/sources', label: 'قاعدة المعرفة' },
    { to: '/limitations', label: 'الشفافية' },
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

        {/* Center Navigation */}
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

        {/* Right Auth Section */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {user ? (
            <>
              <span style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>
                {user.name}
              </span>
              <Link to="/app" className="btn btn-primary btn-sm">
                لوحة التحكم
              </Link>
              <button onClick={logout} className="btn btn-ghost btn-sm" style={{ color: 'var(--color-conflict)' }}>
                خروج
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost btn-sm">
                دخول
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                إنشاء حساب
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

