import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  TrendingUp,
  Truck,
  Lightbulb,
  BarChart3,
  MessageSquare,
  Sparkles,
  Settings2,
  Zap,
} from 'lucide-react';

// ── Nav config ────────────────────────────────────────────────────────────────

interface NavItem {
  to:    string;
  icon:  React.ReactNode;
  label: string;
  badge?: string;
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', icon: <LayoutDashboard size={17} />, label: 'Dashboard' },
  { to: '/inventory', icon: <Package       size={17} />, label: 'Inventory' },
  { to: '/orders',    icon: <ShoppingCart  size={17} />, label: 'Orders' },
  { to: '/forecast',  icon: <TrendingUp    size={17} />, label: 'Forecast' },
  { to: '/suppliers', icon: <Truck         size={17} />, label: 'Suppliers' },
  { to: '/insights',  icon: <Lightbulb     size={17} />, label: 'Profit Insights' },
  { to: '/analytics', icon: <BarChart3     size={17} />, label: 'Analytics' },
  { to: '/chat',      icon: <MessageSquare size={17} />, label: 'AI Assistant' },
  { to: '/settings',  icon: <Settings2     size={17} />, label: 'Settings' },
];

// ── Component ─────────────────────────────────────────────────────────────────

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside
      className="flex flex-col shrink-0 h-screen overflow-y-auto"
      style={{
        width: 'var(--sidebar-width)',
        background: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border)',
      }}
      aria-label="Main navigation"
    >
      {/* ── Logo ─────────────────────────────────────────────────────── */}
      <div
        className="flex items-center gap-2.5 px-5 py-5"
        style={{ borderBottom: '1px solid var(--border)' }}
      >
        <div
          className="flex h-8 w-8 items-center justify-center rounded-lg shrink-0"
          style={{
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            boxShadow: '0 0 16px rgba(59,130,246,0.4)',
          }}
        >
          <Zap size={16} className="text-white" />
        </div>
        <div>
          <p className="text-sm font-bold leading-none" style={{ color: 'var(--text-primary)' }}>
            RetailWise
          </p>
          <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
            AI
          </p>
        </div>
      </div>

      {/* ── AI Status pill ───────────────────────────────────────────── */}
      <div className="px-4 pt-4 pb-2">
        <div
          className="flex items-center gap-2 rounded-lg px-3 py-2"
          style={{
            background: 'rgba(16,185,129,0.08)',
            border: '1px solid rgba(16,185,129,0.2)',
          }}
        >
          <span className="dot-green dot-pulse" />
          <span className="text-[11px] font-medium" style={{ color: '#6ee7b7' }}>
            AI Pipeline Ready
          </span>
        </div>
      </div>

      {/* ── Nav items ────────────────────────────────────────────────── */}
      <nav className="flex-1 px-3 py-2" aria-label="Page navigation">
        <p className="section-title px-2 pt-2">Navigation</p>
        <ul className="space-y-0.5" role="list">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.to ||
              (item.to !== '/dashboard' && location.pathname.startsWith(item.to));

            return (
              <li key={item.to} role="listitem">
                <NavLink
                  to={item.to}
                  id={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                  className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all duration-150 group relative"
                  style={{
                    color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                    background: isActive
                      ? 'rgba(59,130,246,0.12)'
                      : 'transparent',
                    border: isActive
                      ? '1px solid rgba(59,130,246,0.2)'
                      : '1px solid transparent',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.04)';
                      (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      (e.currentTarget as HTMLElement).style.background = 'transparent';
                      (e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)';
                    }
                  }}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {/* Active indicator bar */}
                  {isActive && (
                    <span
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r"
                      style={{ background: 'var(--accent-blue)' }}
                    />
                  )}

                  {/* Icon */}
                  <span
                    style={{
                      color: isActive ? '#93c5fd' : 'var(--text-muted)',
                      transition: 'color 150ms',
                    }}
                  >
                    {item.icon}
                  </span>

                  {/* Label */}
                  <span className="font-medium flex-1">{item.label}</span>

                  {/* Optional badge */}
                  {item.badge && (
                    <span className="badge-blue text-[10px] px-1.5 py-0.5">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <div
        className="px-4 py-4"
        style={{ borderTop: '1px solid var(--border)' }}
      >
        <div
          className="flex items-center gap-2 rounded-lg px-3 py-2"
          style={{ background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.15)' }}
        >
          <Sparkles size={13} style={{ color: '#c4b5fd' }} />
          <div>
            <p className="text-[11px] font-medium" style={{ color: '#c4b5fd' }}>
              Powered by Gemini
            </p>
            <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
              gemini-1.5-flash
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
