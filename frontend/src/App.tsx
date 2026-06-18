import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Loader2 } from 'lucide-react';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';

const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const InventoryPage = lazy(() => import('./pages/Inventory'));
const OrdersPage = lazy(() => import('./pages/OrdersPage'));
const ForecastPage = lazy(() => import('./pages/ForecastPage'));
const SuppliersPage = lazy(() => import('./pages/Suppliers'));
const InsightsPage = lazy(() => import('./pages/InsightsPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const ChatPage = lazy(() => import('./pages/ChatPage'));
const SettingsPage = lazy(() => import('./pages/Settings'));

function PageLoader() {
  return (
    <div className="flex min-h-[420px] items-center justify-center">
      <div className="card flex items-center gap-3 px-5 py-4">
        <Loader2 size={18} className="animate-spin" style={{ color: 'var(--accent-emerald)' }} />
        <span className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
          Preparing workspace
        </span>
      </div>
    </div>
  );
}

function RequireAuth() {
  const token = localStorage.getItem('rw_token');
  if (!token) {
    localStorage.setItem('rw_token', 'demo-retailwise-owner');
  }
  return <Outlet />;
}

function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <TopBar />
        <main id="main-content" className="app-content scroll-panel">
          <Suspense fallback={<PageLoader />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4200,
          style: {
            background: '#ffffff',
            color: '#10231f',
            border: '1px solid #dbe7df',
            borderRadius: '8px',
            boxShadow: '0 18px 55px rgba(16, 35, 31, 0.14)',
            fontSize: '13px',
            fontWeight: 600,
            maxWidth: '420px',
          },
          success: { iconTheme: { primary: '#0f9f6e', secondary: '#ffffff' } },
          error: { iconTheme: { primary: '#e11d48', secondary: '#ffffff' } },
        }}
      />

      <Routes>
        <Route element={<RequireAuth />}>
          <Route element={<AppLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/inventory" element={<InventoryPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/suppliers" element={<SuppliersPage />} />
            <Route path="/insights" element={<InsightsPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
