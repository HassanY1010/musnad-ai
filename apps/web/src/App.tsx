import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Header from './components/layout/Header'
import HomePage from './pages/HomePage'
import AnalysisPage from './pages/AnalysisPage'
import SourcesPage from './pages/SourcesPage'
import LimitationsPage from './pages/LimitationsPage'

export default function App() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: '#162035',
            color: '#FFFFFF',
            border: '1px solid rgba(56, 75, 107, 0.8)',
            fontFamily: 'var(--font-arabic)',
            fontSize: '0.92rem',
            boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
          },
          success: {
            iconTheme: {
              primary: '#10B981',
              secondary: '#FFFFFF',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#FFFFFF',
            },
          },
        }}
      />
      <Header />
      <main style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analysis/:id" element={<AnalysisPage />} />
          <Route path="/sources" element={<SourcesPage />} />
          <Route path="/limitations" element={<LimitationsPage />} />
        </Routes>
      </main>
      <footer
        style={{
          borderTop: '1px solid var(--color-border)',
          padding: '24px 0',
          textAlign: 'center',
          color: 'var(--color-text-muted)',
          fontSize: '0.85rem',
        }}
      >
        <div className="container">
          مُسنَد (MUSNAD AI) — محرك التحقق من المحتوى الرقمي الإسلامي بالأدلة والمصادر &copy; {new Date().getFullYear()}
        </div>
      </footer>
    </div>
  )
}
