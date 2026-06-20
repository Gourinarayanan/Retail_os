import React from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Boxes,
  TrendingUp,
  ShoppingCart,
  Truck,
  Lightbulb,
  BarChart3,
  MessageSquare,
  Settings as SettingsIcon,
  Cpu,
  RefreshCw,
  Zap,
} from 'lucide-react';

interface NavItem {
  to: string;
  label: string;
  icon: React.ElementType;
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard',  label: 'Dashboard',  icon: LayoutDashboard },
  { to: '/inventory',  label: 'Inventory',  icon: Boxes },
  { to: '/forecast',   label: 'Forecast',   icon: TrendingUp },
  { to: '/orders',     label: 'Orders',     icon: ShoppingCart },
  { to: '/suppliers',  label: 'Suppliers',  icon: Truck },
  { to: '/insights',   label: 'Insights',   icon: Lightbulb },
  { to: '/analytics',  label: 'Analytics',  icon: BarChart3 },
  { to: '/chat',       label: 'Chat',       icon: MessageSquare },
  { to: '/settings',   label: 'Settings',   icon: SettingsIcon },
];

export default function Sidebar() {
  const location = useLocation();
  const [isDeploying, setIsDeploying] = React.useState(false);

  const handleDeploy = () => {
    if (isDeploying) return;
    setIsDeploying(true);
    setTimeout(() => setIsDeploying(false), 4000);
  };

  return (
    <nav className="w-64 h-screen fixed left-0 top-0 bg-surface-glass border-r border-border-glass text-on-surface flex flex-col py-6 px-4 z-50 overflow-y-auto">
      {/* Brand */}
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="w-10 h-10 rounded-lg bg-slate-50 flex items-center justify-center border border-slate-200 shadow-sm">
          <Cpu className="w-5 h-5 text-primary stroke-[2px]" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-indigo-600 uppercase">
            Retail_OS
          </h1>
          <p className="text-[10px] text-slate-400 font-semibold tracking-widest uppercase mt-0.5">
            Intelligence Layer
          </p>
        </div>
      </div>

      {/* Nav Links */}
      <ul className="flex-1 flex flex-col gap-1.5">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.to ||
            (item.to !== '/dashboard' && location.pathname.startsWith(item.to));
          return (
            <li key={item.to}>
              <NavLink
                to={item.to}
                id={`nav-${item.label.toLowerCase()}`}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all text-left text-sm ${
                  isActive
                    ? 'bg-slate-50 border-r-4 border-primary text-primary font-bold shadow-sm'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-slate-100/60 hover:translate-x-1'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-primary' : 'text-on-surface-variant'}`} />
                <span>{item.label}</span>
              </NavLink>
            </li>
          );
        })}
      </ul>

      {/* Deploy CTA */}
      <div className="mt-auto pt-6 border-t border-border-glass">
        <button
          id="btn-deploy-update"
          onClick={handleDeploy}
          disabled={isDeploying}
          className="w-full flex items-center justify-center gap-2 bg-primary text-white py-3 px-4 rounded-xl font-semibold text-sm tracking-wide transition-all duration-200 transform hover:scale-[1.01] hover:bg-indigo-700 shadow-md active:scale-95 disabled:opacity-50 disabled:transform-none cursor-pointer"
        >
          {isDeploying ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Optimizing...</span>
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" />
              <span>Deploy Update</span>
            </>
          )}
        </button>
      </div>
    </nav>
  );
}
