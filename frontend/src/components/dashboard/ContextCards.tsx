import React from 'react';
import {
  Cloud, Sun, CloudRain, CloudLightning, Wind,
  Calendar, AlertTriangle, CheckCircle2, Flame,
  ShieldCheck, HardDrive, Zap, ChevronRight, Droplets,
} from 'lucide-react';
import type { WeatherDay, FestivalEntry, ActiveScenario } from '../../types';

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

function getWeatherIcon(condition: string, rain_heavy: boolean) {
  const c = condition.toLowerCase();
  if (rain_heavy || c.includes('thunder')) return <CloudLightning className="w-5 h-5" />;
  if (c.includes('rain') || c.includes('drizzle')) return <CloudRain className="w-5 h-5" />;
  if (c.includes('cloud')) return <Cloud className="w-5 h-5" />;
  if (c.includes('clear') || c.includes('sun')) return <Sun className="w-5 h-5" />;
  return <Wind className="w-5 h-5" />;
}

export default function ContextCards({ context, scenarios, loading }: ContextCardsProps) {
  const weather = context?.weather;
  const today = weather?.today;
  const tomorrow = weather?.tomorrow;
  const festivals = context?.upcoming_festivals?.filter(f => f.days_away <= 14) ?? [];
  const nextFestival = festivals[0];
  const hartalToday = context?.hartal_today;
  const hartalTmrw  = context?.hartal_tomorrow;
  const isHartalSoon = hartalToday || hartalTmrw || context?.hartal_day_after;

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[0,1,2].map(i => (
          <div key={i} className="glass-panel p-5 rounded-xl border border-border-glass animate-pulse min-h-[160px]">
            <div className="h-3 bg-slate-200 rounded w-20 mb-3" />
            <div className="h-8 bg-slate-200 rounded w-32 mb-2" />
            <div className="h-2 bg-slate-100 rounded w-full" />
          </div>
        ))}
      </div>
    );
  }

  const items = [
    {
      id: 'ctx-weather',
      title: 'Weather',
      icon: today ? getWeatherIcon(today.condition, today.rain_heavy) : <Cloud className="w-4 h-4" />,
      colorClass: 'text-sky-500',
      details: today && today.condition !== 'Unknown'
        ? [
            { label: 'Today',    value: `${today.condition} · ${today.temp_max}°C` },
            { label: 'Tomorrow', value: tomorrow ? `${tomorrow.condition} · ${tomorrow.temp_max}°C` : '—' },
          ]
        : [{ label: 'Status', value: 'No data available' }],
    },
    {
      id: 'ctx-hartal',
      title: 'Hartal Status',
      icon: isHartalSoon
        ? <AlertTriangle className="w-4 h-4" />
        : <CheckCircle2 className="w-4 h-4" />,
      colorClass: hartalToday ? 'text-red-500' : hartalTmrw ? 'text-amber-500' : 'text-emerald-500',
      details: [
        {
          label: 'Today',
          value: hartalToday ? '🔴 Hartal Active' : '✅ Normal',
        },
        {
          label: 'Tomorrow',
          value: hartalTmrw ? '⚠️ Hartal Expected' : context?.hartal_day_after ? '⚠️ In 2 Days' : '✅ Normal',
        },
        ...(context?.transport_strike ? [{ label: 'Supply', value: '🚛 Transport Strike' }] : []),
      ],
    },
    {
      id: 'ctx-festivals',
      title: 'Upcoming Festivals',
      icon: <Calendar className="w-4 h-4" />,
      colorClass: 'text-violet-500',
      details: nextFestival
        ? [
            { label: nextFestival.festival, value: `in ${nextFestival.days_away}d · ${nextFestival.duration_days}-day event` },
            ...(festivals[1] ? [{ label: festivals[1].festival, value: `in ${festivals[1].days_away}d` }] : []),
          ]
        : [{ label: 'Status', value: 'No festivals in 14 days' }],
    },
  ];

  return (
    <div className="space-y-6">
      {/* Active scenarios */}
      {scenarios.length > 0 && (
        <div className="glass-panel p-5 rounded-xl border border-primary/20 bg-primary/[0.01]">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-4 h-4 text-primary" />
            <span className="font-label-md text-on-surface uppercase tracking-wider text-xs">Active Demand Scenarios</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {scenarios.slice(0, 4).map(s => (
              <div key={s.id} className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-surface-container-low border border-border-glass" title={s.action}>
                <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                  s.urgency === 'CRITICAL' ? 'bg-red-100 text-red-600'
                  : s.urgency === 'HIGH' ? 'bg-amber-100 text-amber-600'
                  : 'bg-primary/10 text-primary'
                }`}>{s.urgency}</span>
                <span className="text-xs text-on-surface-variant">{s.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3 context cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {items.map(item => (
          <div
            key={item.id}
            className="glass-panel p-5 rounded-xl border border-border-glass flex flex-col gap-4 relative overflow-hidden group hover:bg-surface-glass-hover"
          >
            <div className="flex items-center gap-2.5">
              <span className={item.colorClass}>{item.icon}</span>
              <h4 className="font-headline-sm text-sm font-bold text-on-surface">{item.title}</h4>
            </div>

            <div className="space-y-2 text-xs font-mono">
              {item.details.map((detail, idx) => (
                <div key={idx} className="flex justify-between items-center bg-surface-container/30 px-3 py-1.5 rounded border border-border-glass/40">
                  <span className="text-on-surface-variant">{detail.label}</span>
                  <span className="text-on-surface font-semibold text-right max-w-[140px]">{detail.value}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
