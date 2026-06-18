import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Cloud, CloudRain, Sun, CloudLightning, Wind, Droplets } from 'lucide-react';
import { apiGet } from '../../api/client';
import type { WeatherDay, FestivalEntry } from '../../types';

// ── Page title map ────────────────────────────────────────────────────────────

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Morning Dashboard',
  '/inventory': 'Inventory Intelligence',
  '/orders':    'Order Management',
  '/forecast':  'Demand Forecast',
  '/suppliers': 'Supplier Comparison',
  '/insights':  'Profit Insights',
  '/analytics': 'Sales Analytics',
  '/chat':      'AI Assistant',
  '/settings':  'Settings',
};

// ── Weather icon helper ───────────────────────────────────────────────────────

function WeatherIcon({ condition, rain_heavy }: { condition: string; rain_heavy: boolean }) {
  const c = condition.toLowerCase();
  if (rain_heavy || c.includes('thunder'))      return <CloudLightning size={14} />;
  if (c.includes('rain') || c.includes('drizzle')) return <CloudRain size={14} />;
  if (c.includes('cloud'))                      return <Cloud size={14} />;
  if (c.includes('clear') || c.includes('sun')) return <Sun size={14} />;
  return <Wind size={14} />;
}

// ── Top-level context fetcher ─────────────────────────────────────────────────

interface ContextResponse {
  date: string;
  context: {
    weather?: { today: WeatherDay; tomorrow: WeatherDay };
    hartal_today?: boolean;
    hartal_tomorrow?: boolean;
    upcoming_festivals?: FestivalEntry[];
    transport_strike?: boolean;
    supply_disruption?: boolean;
  };
  active_scenarios: unknown[];
}

function useTodayContext() {
  const [ctx, setCtx] = useState<ContextResponse['context'] | null>(null);

  useEffect(() => {
    apiGet<ContextResponse>('/context/today')
      .then((data) => setCtx(data.context))
      .catch(() => {/* silent — TopBar is non-critical */});
  }, []);

  return ctx;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function TopBar() {
  const location  = useLocation();
  const ctx       = useTodayContext();
  const businessName = import.meta.env.VITE_BUSINESS_NAME || 'RetailWise Store';

  const now = new Date();
  const dateStr = now.toLocaleDateString('en-IN', {
    weekday: 'long',
    year:    'numeric',
    month:   'long',
    day:     'numeric',
  });

  const pageTitle = PAGE_TITLES[location.pathname] ?? 'RetailWise AI';
  const weather   = ctx?.weather?.today;
  const nearFest  = ctx?.upcoming_festivals?.[0];

  return (
    <header
      id="top-bar"
      className="flex items-center justify-between px-6 py-3 shrink-0"
      style={{
        background:   'var(--bg-card)',
        borderBottom: '1px solid var(--border)',
        height:       '56px',
      }}
      role="banner"
    >
      {/* ── Left: page title ───────────────────────────────────────── */}
      <div className="flex items-center gap-3">
        <h1
          className="text-base font-semibold leading-none"
          style={{ color: 'var(--text-primary)' }}
        >
          {pageTitle}
        </h1>
        <span
          className="text-[11px] px-2 py-0.5 rounded"
          style={{ background: 'var(--border)', color: 'var(--text-muted)' }}
        >
          {dateStr}
        </span>
      </div>

      {/* ── Right: pills ───────────────────────────────────────────── */}
      <div className="flex items-center gap-2">

        {/* Hartal alert */}
        {ctx?.hartal_today && (
          <Pill color="red" id="pill-hartal-today">
            🚨 Hartal Today
          </Pill>
        )}
        {!ctx?.hartal_today && ctx?.hartal_tomorrow && (
          <Pill color="amber" id="pill-hartal-tomorrow">
            ⚠️ Hartal Tomorrow
          </Pill>
        )}

        {/* Upcoming festival */}
        {nearFest && nearFest.days_away <= 10 && (
          <Pill color="violet" id={`pill-fest-${nearFest.festival.toLowerCase()}`}>
            🎉 {nearFest.festival} in {nearFest.days_away}d
          </Pill>
        )}

        {/* Weather pill */}
        {weather && weather.condition !== 'Unknown' && (
          <Pill
            color={weather.rain_heavy ? 'blue' : 'gray'}
            id="pill-weather"
          >
            <span className="flex items-center gap-1">
              <WeatherIcon condition={weather.condition} rain_heavy={weather.rain_heavy} />
              {weather.condition}
              {weather.rain_mm > 0 && (
                <span className="flex items-center gap-0.5">
                  <Droplets size={11} />
                  {weather.rain_mm}mm
                </span>
              )}
              · {weather.temp_max}°C
            </span>
          </Pill>
        )}

        {/* Business name */}
        <div
          className="flex items-center gap-2 rounded-lg px-3 py-1.5 ml-1"
          style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
        >
          <div
            className="h-5 w-5 rounded-full flex items-center justify-center text-[10px] font-bold"
            style={{ background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', color: 'white' }}
            aria-hidden
          >
            {businessName.charAt(0).toUpperCase()}
          </div>
          <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
            {businessName}
          </span>
        </div>
      </div>
    </header>
  );
}

// ── Pill ──────────────────────────────────────────────────────────────────────

type PillColor = 'blue' | 'amber' | 'red' | 'violet' | 'gray';

const PILL_STYLES: Record<PillColor, React.CSSProperties> = {
  blue:   { background: 'rgba(59,130,246,0.12)',  border: '1px solid rgba(59,130,246,0.25)',  color: '#93c5fd' },
  amber:  { background: 'rgba(245,158,11,0.12)',  border: '1px solid rgba(245,158,11,0.25)',  color: '#fcd34d' },
  red:    { background: 'rgba(244,63,94,0.12)',   border: '1px solid rgba(244,63,94,0.25)',   color: '#fda4af' },
  violet: { background: 'rgba(139,92,246,0.12)',  border: '1px solid rgba(139,92,246,0.25)',  color: '#c4b5fd' },
  gray:   { background: 'rgba(100,116,139,0.10)', border: '1px solid rgba(100,116,139,0.2)', color: '#94a3b8' },
};

function Pill({
  color,
  id,
  children,
}: {
  color: PillColor;
  id:    string;
  children: React.ReactNode;
}) {
  return (
    <span
      id={id}
      className="flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold"
      style={PILL_STYLES[color]}
    >
      {children}
    </span>
  );
}
