import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AuthGuard, GuestGuard } from './components/layout/AuthGuard';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import AnalysisPage from './pages/AnalysisPage';
import SourcesPage from './pages/SourcesPage';
import LimitationsPage from './pages/LimitationsPage';
import { Toaster } from 'react-hot-toast';

function App() {
  return (
    <AuthProvider>
        <Routes>
          {/* Public Routes (Guest Only) */}
          <Route element={<GuestGuard />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>

          {/* Public/Shared Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/sources" element={<SourcesPage />} />
          <Route path="/limitations" element={<LimitationsPage />} />

          {/* Protected Routes */}
          <Route element={<AuthGuard />}>
            <Route path="/app" element={<DashboardPage />} />
            <Route path="/analysis/:id" element={<AnalysisPage />} />
          </Route>
        </Routes>
        <Toaster position="top-center" toastOptions={{ style: { background: 'var(--color-bg-elevated)', color: '#fff', border: '1px solid var(--color-border)' } }} />
      </AuthProvider>
  );
}

export default App;
