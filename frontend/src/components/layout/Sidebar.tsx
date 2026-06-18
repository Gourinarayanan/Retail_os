import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  BarChart3,
  LayoutDashboard,
  Lightbulb,
  MessageSquare,
  Package,
  Settings2,
  ShoppingCart,
  Sparkles,
  Store,
  TrendingUp,
  Truck,
  Zap,
} from 'lucide-react';

interface NavItem {
  to: string;
  icon: React.ReactNode;
  label: string;
  short: string;
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', icon: <LayoutDashboard size={18} />, label: 'Today', short: 'Today' },
  { to: '/inventory', icon: <Package size={18} />, label: 'Inventory', short: 'Stock' },
  { to: '/orders', icon: <ShoppingCart size={18} />, label: 'Orders', short: 'Orders' },
  { to: '/forecast', icon: <TrendingUp size={18} />, label: 'Forecast', short: 'Forecast' },
  { to: '/suppliers', icon: <Truck size={18} />, label: 'Suppliers', short: 'Supply' },
  { to: '/insights', icon: <Lightbulb size={18} />, label: 'Opportunities', short: 'Profit' },
  { to: '/analytics', icon: <BarChart3 size={18} />, label: 'Analytics', short: 'Data' },
  { to: '/chat', icon: <MessageSquare size={18} />, label: 'Ask AI', short: 'AI' },
  { to: '/settings', icon: <Settings2 size={18} />, label: 'Settings', short: 'More' },
];

function isRouteActive(pathname: string, to: string) {
  return pathname === to || (to !== '/dashboard' && pathname.startsWith(to));
}

function NavItemLink({ item, compact = false }: { item: NavItem; compact?: boolean }) {
  const location = useLocation();
  const active = isRouteActive(location.pathname, item.to);

  return (
    <NavLink
      to={item.to}
      id={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
      className={compact ? 'mobile-nav-item' : 'side-nav-item'}
      style={{
        color: active ? '#ffffff' : 'rgba(255,255,255,0.68)',
        background: active ? 'rgba(255,255,255,0.12)' : 'transparent',
        borderColor: active ? 'rgba(255,255,255,0.18)' : 'transparent',
      }}
      aria-current={active ? 'page' : undefined}
      title={item.label}
    >
      <span className="side-nav-icon">{item.icon}</span>
      <span className="side-nav-label">{compact ? item.short : item.label}</span>
    </NavLink>
  );
}

export default function Sidebar() {
  return (
    <>
      <aside className="retail-sidebar" aria-label="Main navigation">
        <div className="brand-block">
          <div className="brand-mark">
            <Store size={20} />
          </div>
          <div className="brand-copy">
            <p>RetailWise AI</p>
            <span>Owner command center</span>
          </div>
        </div>

        <div className="pipeline-card">
          <div className="flex items-center justify-between gap-2">
            <span className="flex items-center gap-2">
              <span className="dot-green dot-pulse" />
              Live agent stack
            </span>
            <Zap size={14} />
          </div>
          <p>Gemini, Prophet, inventory, suppliers and WhatsApp in one flow.</p>
        </div>

        <nav className="side-nav" aria-label="Page navigation">
          {NAV_ITEMS.map((item) => (
            <NavItemLink key={item.to} item={item} />
          ))}
        </nav>

        <div className="sidebar-footer">
          <Sparkles size={15} />
          <div>
            <p>Gemini only</p>
            <span>No OpenAI or Anthropic</span>
          </div>
        </div>
      </aside>

      <nav className="mobile-nav" aria-label="Mobile navigation">
        {NAV_ITEMS.slice(0, 5).map((item) => (
          <NavItemLink key={item.to} item={item} compact />
        ))}
      </nav>
    </>
  );
}
