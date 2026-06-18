import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/layout/Sidebar';
import TopBar  from './components/layout/TopBar';

// ── Lazy-loaded pages ─────────────────────────────────────────────────────────
const DashboardPage    = lazy(() => import('./pages/DashboardPage'));
const InventoryPage    = lazy(() => import('./pages/Inventory'));
const OrdersPage       = lazy(() => import('./pages/OrdersPage'));
const ForecastPage     = lazy(() => import('./pages/ForecastPage'));
const SuppliersPage    = lazy(() => import('./pages/Suppliers'));
const InsightsPage     = lazy(() => import('./pages/InsightsPage'));
const AnalyticsPage    = lazy(() => import('./pages/AnalyticsPage'));
const ChatPage         = lazy(() => import('./pages/ChatPage'));
const SettingsPage     = lazy(() => import('./pages/Settings'));

// ── Loading spinner ───────────────────────────────────────────────────────────
function PageLoader() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div
          className="h-10 w-10 rounded-full border-2 border-blue-500 border-t-transparent animate-spin"
          role="status"
          aria-label="Loading"
        />
        <span style={{ color: 'var(--text-muted)' }} className="text-sm">
          Loading…
        </span>
      </div>
    </div>
  );
}

// ── Auth guard ────────────────────────────────────────────────────────────────
/**
 * In this hackathon build, the app is single-user (the store owner).
 * The guard simply checks for a token in localStorage.
 * Replace with a real auth flow (Supabase, Firebase, etc.) post-hackathon.
 */
function RequireAuth() {
  const token = localStorage.getItem('rw_token');
  // For demo: auto-set a token if missing so the owner can use it immediately
  if (!token) {
    localStorage.setItem('rw_token', 'demo-retailwise-owner');
  }
  return <Outlet />;
}

// ── App layout ────────────────────────────────────────────────────────────────
function AppLayout() {
  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-base)' }}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar />
        <main
          id="main-content"
          className="flex-1 overflow-y-auto p-6 scroll-panel"
          style={{ background: 'var(--bg-base)' }}
        >
          <Suspense fallback={<PageLoader />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  );
}

// ── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <BrowserRouter>
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#111827',
            color: '#f0f4ff',
            border: '1px solid #1e2d45',
            borderRadius: '10px',
            fontSize: '13px',
            maxWidth: '380px',
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#111827' } },
          error:   { iconTheme: { primary: '#f43f5e', secondary: '#111827' } },
        }}
      />

      <Routes>
        {/* Protected routes — wrapped in RequireAuth + AppLayout */}
        <Route element={<RequireAuth />}>
          <Route element={<AppLayout />}>
            {/* Default → Dashboard */}
            <Route index element={<Navigate to="/dashboard" replace />} />

            <Route path="/dashboard"  element={<DashboardPage />} />
            <Route path="/inventory"  element={<InventoryPage />} />
            <Route path="/orders"     element={<OrdersPage />} />
            <Route path="/forecast"   element={<ForecastPage />} />
            <Route path="/suppliers"  element={<SuppliersPage />} />
            <Route path="/insights"   element={<InsightsPage />} />
            <Route path="/analytics"  element={<AnalyticsPage />} />
            <Route path="/chat"       element={<ChatPage />} />
            <Route path="/settings"   element={<SettingsPage />} />

            {/* Fallback → Dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
