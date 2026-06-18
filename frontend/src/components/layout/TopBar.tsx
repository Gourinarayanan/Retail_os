import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import {
  AlertTriangle,
  CalendarDays,
  Cloud,
  CloudLightning,
  CloudRain,
  MapPin,
  Search,
  Sun,
  Wind,
} from 'lucide-react';
import { apiGet } from '../../api/client';
import type { FestivalEntry, WeatherDay } from '../../types';

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': { title: 'Today', subtitle: 'Morning brief, context, and agent flow' },
  '/inventory': { title: 'Inventory', subtitle: 'Stock health, expiry, and batch controls' },
  '/orders': { title: 'Orders', subtitle: 'Review AI quantities and send supplier orders' },
  '/forecast': { title: 'Forecast', subtitle: 'Prophet demand forecasts with scenario lift' },
  '/suppliers': { title: 'Suppliers', subtitle: 'Reliability, rating, and regional risk' },
  '/insights': { title: 'Opportunities', subtitle: 'Festival profit actions from live data' },
  '/analytics': { title: 'Analytics', subtitle: 'Charts for sales, stock, and supplier performance' },
  '/chat': { title: 'Ask AI', subtitle: 'Gemini assistant with RAG context' },
  '/settings': { title: 'Settings', subtitle: 'Business info and API readiness' },
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
  if (day.rain_heavy || c.includes('thunder')) return <CloudLightning size={15} />;
  if (c.includes('rain') || c.includes('drizzle')) return <CloudRain size={15} />;
  if (c.includes('cloud')) return <Cloud size={15} />;
  if (c.includes('clear') || c.includes('sun')) return <Sun size={15} />;
  return <Wind size={15} />;
}

function useTodayContext() {
  const [ctx, setCtx] = useState<ContextResponse['context'] | null>(null);

  useEffect(() => {
    apiGet<ContextResponse>('/context/today')
      .then((data) => setCtx(data.context))
      .catch(() => undefined);
  }, []);

  return ctx;
}

export default function TopBar() {
  const location = useLocation();
  const ctx = useTodayContext();
  const businessName = import.meta.env.VITE_BUSINESS_NAME || 'RetailWise Store';
  const page = PAGE_TITLES[location.pathname] ?? { title: 'RetailWise AI', subtitle: 'Retail operations workspace' };
  const weather = ctx?.weather?.today;
  const festival = ctx?.upcoming_festivals?.[0];

  const date = new Date().toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });

  return (
    <header id="top-bar" className="topbar" role="banner">
      <div className="topbar-title">
        <div>
          <h1>{page.title}</h1>
          <p>{page.subtitle}</p>
        </div>
      </div>

      <div className="topbar-actions">
        <div className="topbar-search">
          <Search size={14} />
          <span>Scan products, orders, suppliers</span>
        </div>

        <div className="context-pill">
          <CalendarDays size={14} />
          <span>{date}</span>
        </div>

        {ctx?.hartal_today && (
          <div className="context-pill danger">
            <AlertTriangle size={14} />
            <span>Hartal today</span>
          </div>
        )}

        {!ctx?.hartal_today && ctx?.hartal_tomorrow && (
          <div className="context-pill warning">
            <AlertTriangle size={14} />
            <span>Hartal tomorrow</span>
          </div>
        )}

        {festival && festival.days_away <= 10 && (
          <div className="context-pill violet">
            <CalendarDays size={14} />
            <span>{festival.festival} in {festival.days_away}d</span>
          </div>
        )}

        {weather && weather.condition !== 'Unknown' && (
          <div className={weather.rain_heavy ? 'context-pill info' : 'context-pill'}>
            <WeatherIcon day={weather} />
            <span>{weather.condition} {weather.temp_max}C</span>
          </div>
        )}

        <div className="store-chip">
          <span className="store-avatar">{businessName.charAt(0).toUpperCase()}</span>
          <span className="store-name">{businessName}</span>
          <MapPin size={13} />
        </div>
      </div>
    </header>
  );
}
