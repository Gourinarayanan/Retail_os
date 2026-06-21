import React, { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Search, MapPin, Bell, Menu, X,
  AlertTriangle, CalendarDays, Cloud, CloudLightning, CloudRain, Sun, Wind, Package
} from 'lucide-react';
import { apiGet } from '../../api/client';
import type { FestivalEntry, WeatherDay } from '../../types';
import { useSearch } from '../../context/SearchContext';

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

interface AlertItem {
  product_id: number;
  name: string;
  stock_status: string;
  days_remaining: number;
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
  const { searchQuery, setSearchQuery } = useSearch();

  // Location State
  const [locationName, setLocationName] = useState(import.meta.env.VITE_LOCATION || 'Palakkad, Kerala');

  // Notifications State
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 1. Fetch Context
    apiGet<ContextResponse>('/context/today')
      .then((data) => setCtx(data.context))
      .catch(() => undefined);

    // 2. Fetch Alerts
    apiGet<AlertItem[]>('/inventory/alerts')
      .then((data) => setAlerts(data))
      .catch(() => undefined);

    // 3. Fetch Location from Settings
    apiGet<{ weather_city: string }>('/settings')
      .then((data) => {
        if (data && data.weather_city) {
          setLocationName(data.weather_city.toUpperCase());
        }
      })
      .catch(() => undefined);
  }, []);

  // Close notifications if clicked outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const pageLabel = PAGE_LABELS[location.pathname] ?? 'RetailWise OS';
  const weather = ctx?.weather?.today;
  const festival = ctx?.upcoming_festivals?.[0];

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
          <span>{locationName}</span>
        </div>

        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <button
            id="btn-notifications"
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative text-slate-400 hover:text-indigo-600 transition-colors p-2 rounded-lg hover:bg-slate-50 focus:outline-none"
          >
            <Bell className="w-[18px] h-[18px]" />
            {alerts.length > 0 && (
              <span className="absolute top-1 right-1 flex h-3 w-3 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white border-2 border-white">
                {alerts.length}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-surface-container-lowest border border-border-glass rounded-xl shadow-xl overflow-hidden animate-fade-in z-50">
              <div className="px-4 py-3 border-b border-border-glass flex justify-between items-center bg-surface-container-low">
                <h3 className="font-bold text-sm text-on-surface">Inventory Alerts</h3>
                <span className="text-xs font-medium bg-red-100 text-red-600 px-2 py-0.5 rounded-full">{alerts.length} active</span>
              </div>
              <div className="max-h-80 overflow-y-auto">
                {alerts.length === 0 ? (
                  <div className="p-6 text-center text-sm text-on-surface-variant font-medium">
                    No active alerts. All stock levels are healthy!
                  </div>
                ) : (
                  alerts.map((alert) => (
                    <div key={alert.product_id} className="p-4 border-b border-border-glass last:border-b-0 hover:bg-surface-container-low transition-colors">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-semibold text-sm text-on-surface truncate pr-2">{alert.name}</span>
                        <span className={`text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded border ${
                          alert.stock_status === 'out_of_stock' || alert.stock_status === 'critical' ? 'bg-red-50 text-red-600 border-red-200' : 'bg-amber-50 text-amber-600 border-amber-200'
                        }`}>
                          {alert.stock_status.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-on-surface-variant font-medium">
                        <Package className="w-3.5 h-3.5" />
                        {alert.days_remaining <= 0 ? 'Stock depleted' : `${alert.days_remaining} days remaining`}
                      </div>
                    </div>
                  ))
                )}
              </div>
              <div className="p-3 border-t border-border-glass text-center">
                <a href="/inventory" className="text-xs font-bold text-primary hover:text-indigo-700 transition-colors">View All Inventory</a>
              </div>
            </div>
          )}
        </div>

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
