import React, { lazy, Suspense, useState } from 'react';
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Loader2 } from 'lucide-react';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';

const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const InventoryPage  = lazy(() => import('./pages/Inventory'));
const OrdersPage     = lazy(() => import('./pages/OrdersPage'));
const ForecastPage   = lazy(() => import('./pages/ForecastPage'));
const SuppliersPage  = lazy(() => import('./pages/Suppliers'));
const InsightsPage   = lazy(() => import('./pages/InsightsPage'));
const AnalyticsPage  = lazy(() => import('./pages/AnalyticsPage'));
const ChatPage       = lazy(() => import('./pages/ChatPage'));
const SettingsPage   = lazy(() => import('./pages/Settings'));

function PageLoader() {
  return (
    <div className="flex min-h-[420px] items-center justify-center">
      <div className="glass-panel flex items-center gap-3 px-5 py-4 rounded-xl">
        <Loader2 size={18} className="animate-spin text-primary" />
        <span className="text-sm font-semibold text-on-surface-variant">
          Preparing workspace...
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
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="font-sans min-h-screen flex bg-background-obsidian text-on-surface select-none relative">
      {/* Desktop Sidebar */}
      <div className="hidden md:block shrink-0">
        <Sidebar />
      </div>

      {/* Mobile Drawer */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setIsMobileMenuOpen(false)}
          />
          <div className="relative animate-slide-right-mobile">
            <Sidebar />
          </div>
        </div>
      )}

      {/* Main canvas */}
      <div className="flex-1 min-w-0 md:ml-64 flex flex-col min-h-screen">
        <TopBar
          onMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          isMobileMenuOpen={isMobileMenuOpen}
        />
        <main id="main-content" className="flex-1 p-6 md:p-8 overflow-y-auto pb-12">
          <Suspense fallback={<PageLoader />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  );
}

import { SearchProvider } from './context/SearchContext';

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4200,
          style: {
            background: '#ffffff',
            color: '#0f172a',
            border: '1px solid #e2e8f0',
            borderRadius: '12px',
            boxShadow: '0 10px 30px rgba(15,23,42,0.08)',
            fontSize: '13px',
            fontWeight: 600,
            maxWidth: '420px',
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#ffffff' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: '#ffffff' } },
        }}
      />

      <SearchProvider>
        <Routes>
          <Route element={<RequireAuth />}>
            <Route element={<AppLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/inventory"  element={<InventoryPage />} />
              <Route path="/orders"     element={<OrdersPage />} />
              <Route path="/forecast"   element={<ForecastPage />} />
              <Route path="/suppliers"  element={<SuppliersPage />} />
              <Route path="/insights"   element={<InsightsPage />} />
              <Route path="/analytics"  element={<AnalyticsPage />} />
              <Route path="/chat"       element={<ChatPage />} />
              <Route path="/settings"   element={<SettingsPage />} />
              <Route path="*"           element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Route>
        </Routes>
      </SearchProvider>
    </BrowserRouter>
  );
}
