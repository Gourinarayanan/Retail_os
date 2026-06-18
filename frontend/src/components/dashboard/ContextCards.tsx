import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Cloud, Sun, CloudRain, CloudLightning, Wind,
  Calendar, AlertTriangle, CheckCircle2, Flame,
  RefreshCw, ChevronRight, Zap, Droplets
} from 'lucide-react';
import type { WeatherDay, FestivalEntry, ActiveScenario } from '../../types';

// ── Props ─────────────────────────────────────────────────────────────────────

interface ContextCardsProps {
  context: {
    weather?: { today: WeatherDay; tomorrow: WeatherDay };
    hartal_today?: boolean;
    hartal_tomorrow?: boolean;
    hartal_day_after?: boolean;
    hartal_source?: string | null;
    transport_strike?: boolean;
    supply_disruption?: boolean;
    upcoming_festivals?: FestivalEntry[];
    sources?: string[];
  } | null;
  scenarios: ActiveScenario[];
  loading: boolean;
}

// ── Weather helpers ───────────────────────────────────────────────────────────

function getWeatherIcon(condition: string, rain_heavy: boolean, size = 20) {
  const c = condition.toLowerCase();
  if (rain_heavy || c.includes('thunder')) return <CloudLightning size={size} />;
  if (c.includes('rain') || c.includes('drizzle')) return <CloudRain size={size} />;
  if (c.includes('cloud')) return <Cloud size={size} />;
  if (c.includes('clear') || c.includes('sun')) return <Sun size={size} />;
  return <Wind size={size} />;
}

function getWeatherColor(condition: string, rain_heavy: boolean) {
  if (rain_heavy) return { icon: '#60a5fa', bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.2)' };
  const c = condition.toLowerCase();
  if (c.includes('clear') || c.includes('sun')) return { icon: '#fbbf24', bg: 'rgba(251,191,36,0.08)', border: 'rgba(251,191,36,0.2)' };
  if (c.includes('cloud')) return { icon: '#94a3b8', bg: 'rgba(100,116,139,0.08)', border: 'rgba(100,116,139,0.2)' };
  return { icon: '#60a5fa', bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.2)' };
}

// ── Skeleton ──────────────────────────────────────────────────────────────────

function CardSkeleton() {
  return (
    <div className="card flex flex-col gap-3 min-h-[160px]">
      <div className="skeleton h-4 w-24 rounded" />
      <div className="skeleton h-8 w-32 rounded" />
      <div className="skeleton h-3 w-full rounded" />
      <div className="skeleton h-3 w-3/4 rounded" />
    </div>
  );
}

// ── Weather Card ──────────────────────────────────────────────────────────────

function WeatherCard({ weather }: { weather?: { today: WeatherDay; tomorrow: WeatherDay } }) {
  if (!weather || !weather.today.condition || weather.today.condition === 'Unknown') {
    return (
      <div className="card flex flex-col gap-3 min-h-[160px]">
        <p className="section-title">Weather</p>
        <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
          <Cloud size={16} />
          <span className="text-sm">No weather data — check API key</span>
        </div>
      </div>
    );
  }

  const today    = weather.today;
  const tomorrow = weather.tomorrow;
  const colors   = getWeatherColor(today.condition, today.rain_heavy);

  return (
    <div
      className="card flex flex-col gap-4"
      style={{ borderColor: colors.border }}
    >
      <div className="flex items-center justify-between">
        <p className="section-title">Weather</p>
        <span className="badge-blue text-[10px]">[OpenWeather]</span>
      </div>

      {/* Today */}
      <div className="flex items-start gap-3">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl shrink-0"
          style={{ background: colors.bg, color: colors.icon }}
        >
          {getWeatherIcon(today.condition, today.rain_heavy, 20)}
        </div>
        <div>
          <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>
            {today.condition}
          </p>
          <div className="flex items-center gap-3 mt-0.5">
            <span className="stat-number text-xl">{today.temp_max}°C</span>
            {today.rain_mm > 0 && (
              <span className="flex items-center gap-1 text-xs" style={{ color: '#93c5fd' }}>
                <Droplets size={11} /> {today.rain_mm}mm
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Tomorrow */}
      {tomorrow && tomorrow.condition !== 'Unknown' && (
        <div
          className="flex items-center justify-between rounded-lg px-3 py-2 text-xs"
          style={{
            background: tomorrow.rain_heavy
              ? 'rgba(59,130,246,0.1)'
              : 'rgba(255,255,255,0.03)',
            border: `1px solid ${tomorrow.rain_heavy ? 'rgba(59,130,246,0.25)' : 'var(--border)'}`,
          }}
        >
          <span style={{ color: 'var(--text-muted)' }}>Tomorrow</span>
          <div className="flex items-center gap-2">
            <span style={{ color: tomorrow.rain_heavy ? '#93c5fd' : 'var(--text-secondary)' }}>
              {tomorrow.condition}
            </span>
            {tomorrow.rain_heavy && (
              <span className="badge-blue text-[10px]">⚠️ Heavy Rain</span>
            )}
            <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
              {tomorrow.temp_max}°C
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Hartal Card ───────────────────────────────────────────────────────────────

function HartalCard({
  hartal_today,
  hartal_tomorrow,
  hartal_day_after,
  hartal_source,
  transport_strike,
  supply_disruption,
}: {
  hartal_today?: boolean;
  hartal_tomorrow?: boolean;
  hartal_day_after?: boolean;
  hartal_source?: string | null;
  transport_strike?: boolean;
  supply_disruption?: boolean;
}) {
  const isCritical = hartal_today || hartal_tomorrow;
  const isWarning  = !isCritical && (hartal_day_after || transport_strike);
  const isOk       = !isCritical && !isWarning;

  const borderColor = isCritical ? 'rgba(244,63,94,0.35)'
                    : isWarning  ? 'rgba(245,158,11,0.3)'
                    : 'rgba(16,185,129,0.2)';
  const bgColor     = isCritical ? 'rgba(244,63,94,0.06)'
                    : isWarning  ? 'rgba(245,158,11,0.06)'
                    : 'rgba(16,185,129,0.05)';

  return (
    <div className="card flex flex-col gap-4" style={{ borderColor, background: `var(--bg-card) !important` }}>
      <div className="flex items-center justify-between">
        <p className="section-title">Hartal Status</p>
        <span className="badge-gray text-[10px]">[NewsAPI]</span>
      </div>

      {/* Main status */}
      <div className="flex items-start gap-3">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl shrink-0"
          style={{ background: bgColor }}
        >
          {isOk
            ? <CheckCircle2 size={20} style={{ color: '#6ee7b7' }} />
            : isCritical
            ? <Flame size={20} style={{ color: '#f43f5e' }} />
            : <AlertTriangle size={20} style={{ color: '#f59e0b' }} />
          }
        </div>
        <div>
          {hartal_today && (
            <>
              <p className="font-bold" style={{ color: '#f43f5e' }}>Hartal TODAY</p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>Near-zero sales expected</p>
            </>
          )}
          {!hartal_today && hartal_tomorrow && (
            <>
              <p className="font-bold" style={{ color: '#fcd34d' }}>Hartal TOMORROW</p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>Pre-buy rush expected today</p>
            </>
          )}
          {!hartal_today && !hartal_tomorrow && hartal_day_after && (
            <>
              <p className="font-semibold" style={{ color: '#fcd34d' }}>Hartal in 2 Days</p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>Begin stocking today</p>
            </>
          )}
          {isOk && (
            <>
              <p className="font-semibold" style={{ color: '#6ee7b7' }}>No Hartal</p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>Normal operating day</p>
            </>
          )}
        </div>
      </div>

      {/* Source */}
      {hartal_source && (
        <p className="text-[11px] italic truncate" style={{ color: 'var(--text-muted)' }}>
          Source: {hartal_source}
        </p>
      )}

      {/* Flags */}
      <div className="flex flex-wrap gap-1.5">
        {transport_strike  && <span className="badge-amber">🚛 Transport Strike</span>}
        {supply_disruption && <span className="badge-red">⚠️ Supply Risk</span>}
        {!transport_strike && !supply_disruption && isOk && (
          <span className="badge-green">✓ Supply chains normal</span>
        )}
      </div>
    </div>
  );
}

// ── Festival Card ─────────────────────────────────────────────────────────────

function FestivalCard({ festivals }: { festivals?: FestivalEntry[] }) {
  const near = festivals?.filter((f) => f.days_away <= 14) ?? [];
  const next = near[0];

  const urgencyColor =
    !next            ? '#94a3b8'
    : next.days_away <= 3  ? '#f43f5e'
    : next.days_away <= 7  ? '#fcd34d'
    : '#c4b5fd';

  return (
    <div
      className="card flex flex-col gap-4"
      style={{
        borderColor: next && next.days_away <= 7
          ? 'rgba(139,92,246,0.3)' : 'var(--border)',
      }}
    >
      <div className="flex items-center justify-between">
        <p className="section-title">Upcoming Festivals</p>
        <span className="badge-violet text-[10px]">[Google Calendar]</span>
      </div>

      {!next ? (
        <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
          <Calendar size={16} />
          <span className="text-sm">No festivals in next 14 days</span>
        </div>
      ) : (
        <>
          <div className="flex items-center gap-3">
            <div
              className="flex h-10 w-10 items-center justify-center rounded-xl text-lg shrink-0"
              style={{ background: 'rgba(139,92,246,0.1)' }}
            >
              🎉
            </div>
            <div>
              <p className="font-bold" style={{ color: urgencyColor }}>
                {next.festival}
              </p>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                in{' '}
                <span className="font-semibold mono" style={{ color: urgencyColor }}>
                  {next.days_away}
                </span>{' '}
                day{next.days_away !== 1 ? 's' : ''}
                {' '}· {next.duration_days}-day event
              </p>
            </div>
          </div>

          {/* Additional upcoming */}
          {near.slice(1).map((f) => (
            <div
              key={f.festival}
              className="flex items-center justify-between text-xs"
              style={{ color: 'var(--text-muted)' }}
            >
              <span>{f.festival}</span>
              <span className="mono">{f.days_away}d away</span>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

// ── Active Scenarios Strip ────────────────────────────────────────────────────

function ScenariosStrip({ scenarios }: { scenarios: ActiveScenario[] }) {
  if (!scenarios.length) return null;

  const urgencyOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, INFO: 4 };
  const sorted = [...scenarios].sort(
    (a, b) => (urgencyOrder[a.urgency] ?? 5) - (urgencyOrder[b.urgency] ?? 5)
  );

  return (
    <div
      className="rounded-xl px-4 py-3 mb-4"
      style={{
        background: 'rgba(59,130,246,0.05)',
        border: '1px solid rgba(59,130,246,0.15)',
      }}
    >
      <p className="section-title mb-2 flex items-center gap-2">
        <Zap size={12} style={{ color: 'var(--accent-blue)' }} />
        Active Demand Scenarios
      </p>
      <div className="flex flex-wrap gap-2">
        {sorted.map((s) => (
          <div
            key={s.id}
            className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
            title={s.action}
          >
            <span className={`urgency-${s.urgency}`}>{s.urgency}</span>
            <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              {s.name}
            </span>
            <ChevronRight size={10} style={{ color: 'var(--text-muted)' }} />
            <span className="text-[11px] italic truncate max-w-[180px]" style={{ color: 'var(--text-muted)' }}>
              {s.action}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export default function ContextCards({ context, scenarios, loading }: ContextCardsProps) {
  if (loading) {
    return (
      <div>
        <div className="grid grid-cols-3 gap-4 mb-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Scenarios strip */}
      <ScenariosStrip scenarios={scenarios} />

      {/* 3 context cards */}
      <div className="grid grid-cols-3 gap-4">
        <WeatherCard weather={context?.weather} />
        <HartalCard
          hartal_today={context?.hartal_today}
          hartal_tomorrow={context?.hartal_tomorrow}
          hartal_day_after={context?.hartal_day_after}
          hartal_source={context?.hartal_source}
          transport_strike={context?.transport_strike}
          supply_disruption={context?.supply_disruption}
        />
        <FestivalCard festivals={context?.upcoming_festivals} />
      </div>
    </div>
  );
}
