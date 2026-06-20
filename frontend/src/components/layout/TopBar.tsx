import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Search, MapPin, Bell, Menu, X,
  AlertTriangle, CalendarDays, Cloud, CloudLightning, CloudRain, Sun, Wind,
} from 'lucide-react';
import { apiGet } from '../../api/client';
import type { FestivalEntry, WeatherDay } from '../../types';

const PAGE_LABELS: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/inventory': 'Inventory',
  '/orders': 'Orders',
  '/forecast': 'Forecast',
  '/suppliers': 'Suppliers',
  '/insights': 'Insights',
  '/analytics': 'Analytics',
  '/chat': 'Chat',
  '/settings': 'System Settings',
};

interface ContextResponse {
  context: {
    weather?: { today: WeatherDay; tomorrow: WeatherDay };
    hartal_today?: boolean;
    hartal_tomorrow?: boolean;
    upcoming_festivals?: FestivalEntry[];
  };
}

function WeatherIcon({ day }: { day: WeatherDay }) {
  const c = day.condition.toLowerCase();
  if (day.rain_heavy || c.includes('thunder')) return <CloudLightning size={14} />;
  if (c.includes('rain') || c.includes('drizzle')) return <CloudRain size={14} />;
  if (c.includes('cloud')) return <Cloud size={14} />;
  if (c.includes('clear') || c.includes('sun')) return <Sun size={14} />;
  return <Wind size={14} />;
}

interface TopBarProps {
  onMenuToggle?: () => void;
  isMobileMenuOpen?: boolean;
}

export default function TopBar({ onMenuToggle, isMobileMenuOpen }: TopBarProps) {
  const location = useLocation();
  const [ctx, setCtx] = useState<ContextResponse['context'] | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    apiGet<ContextResponse>('/context/today')
      .then((data) => setCtx(data.context))
      .catch(() => undefined);
  }, []);

  const pageLabel = PAGE_LABELS[location.pathname] ?? 'RetailWise OS';
  const weather = ctx?.weather?.today;
  const festival = ctx?.upcoming_festivals?.[0];
  const location_name = import.meta.env.VITE_LOCATION || 'Palakkad, Kerala';

  return (
    <header className="sticky top-0 w-full z-40 bg-surface-glass backdrop-blur-xl border-b border-border-glass flex items-center justify-between px-6 md:px-8 h-16 text-on-surface">
      <div className="flex items-center gap-4">
        {/* Mobile toggle */}
        <button
          id="btn-mobile-menu"
          onClick={onMenuToggle}
          className="md:hidden text-on-surface-variant hover:text-primary transition-colors p-1 rounded-md hover:bg-surface-container-low"
        >
          {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        {/* Breadcrumb */}
        <div className="flex items-center gap-1.5 md:gap-2">
          <h2 className="text-sm text-slate-400 font-semibold tracking-wider uppercase hidden sm:block">
            Operations Overview
          </h2>
          <span className="text-slate-300 mx-1.5 hidden sm:block">/</span>
          <h2 className="text-sm font-bold text-indigo-600 uppercase tracking-tight">
            {pageLabel}
          </h2>
        </div>
      </div>

      <div className="flex items-center gap-3 md:gap-5">
        {/* Search */}
        <div className="relative hidden lg:block group">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant group-focus-within:text-primary transition-colors" />
          <input
            id="g-search-input"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search parameters..."
            className="nexus-input w-60 pl-10 pr-4 py-1.5 rounded-full text-sm font-medium placeholder-slate-400 shadow-sm"
          />
        </div>

        {/* Context pills */}
        {ctx?.hartal_today && (
          <div className="hidden sm:flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-red-50 text-red-600 border border-red-200">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Hartal today</span>
          </div>
        )}
        {!ctx?.hartal_today && ctx?.hartal_tomorrow && (
          <div className="hidden sm:flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-50 text-amber-600 border border-amber-200">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Hartal tmrw</span>
          </div>
        )}
        {festival && festival.days_away <= 10 && (
          <div className="hidden sm:flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-violet-50 text-violet-600 border border-violet-200">
            <CalendarDays className="w-3.5 h-3.5" />
            <span>{festival.festival} in {festival.days_away}d</span>
          </div>
        )}
        {weather && weather.condition !== 'Unknown' && (
          <div className="hidden sm:flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-sky-50 text-sky-600 border border-sky-200">
            <WeatherIcon day={weather} />
            <span>{weather.condition} {weather.temp_max}°C</span>
          </div>
        )}

        {/* Location */}
        <div className="hidden sm:flex items-center gap-1.5 text-slate-500 text-xs font-semibold uppercase tracking-wider">
          <MapPin className="w-3.5 h-3.5 text-primary" />
          <span>{location_name}</span>
        </div>

        {/* Notifications */}
        <button
          id="btn-notifications"
          className="relative text-slate-400 hover:text-indigo-600 transition-colors p-2 rounded-lg hover:bg-slate-50"
        >
          <Bell className="w-[18px] h-[18px]" />
          <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white" />
        </button>

        {/* Avatar */}
        <div className="w-8 h-8 rounded-lg border border-slate-200 overflow-hidden cursor-pointer hover:border-indigo-400 hover:scale-105 transition-all shadow-sm bg-indigo-100 flex items-center justify-center">
          <span className="text-xs font-bold text-indigo-600">
            {(import.meta.env.VITE_BUSINESS_NAME || 'R').charAt(0).toUpperCase()}
          </span>
        </div>
      </div>
    </header>
  );
}
