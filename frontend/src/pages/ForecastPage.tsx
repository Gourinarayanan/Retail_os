import React, { useState, useEffect, useCallback } from 'react';
import { Search, TrendingUp, RefreshCw, Info, Calendar, Database } from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ReferenceLine
} from 'recharts';
import type { ForecastResult } from '../types';
import { apiGet } from '../api/client';

function ForecastTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const date = new Date(label).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' });
  return (
    <div className="rounded-xl px-4 py-3 text-xs flex flex-col gap-2 bg-surface-container-high border border-border-glass shadow-lg min-w-[160px]">
      <p className="font-semibold text-on-surface border-b border-border-glass/60 pb-1">{date}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex justify-between gap-6 items-center">
          <span className="font-medium" style={{ color: p.color }}>{p.name}</span>
          <span className="font-mono font-bold text-on-surface">
            {p.value?.toFixed(1)}
          </span>
        </div>
      ))}
    </div>
  );
}

function ForecastCard({ result }: { result: ForecastResult }) {
  const uplift = result.multiplier > 1.0;
  const pct = Math.round((result.multiplier - 1) * 100);
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="glass-panel rounded-2xl p-5 md:p-6 transition-all duration-300 relative overflow-hidden border border-border-glass group hover:-translate-y-1 hover:shadow-lg flex flex-col h-full">
      {uplift && (
        <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-3xl pointer-events-none group-hover:scale-125 transition-transform duration-700" />
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-6 relative z-10">
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-headline-sm text-base font-bold text-on-surface">{result.name}</h3>
            {uplift && (
              <span className="font-label-xs text-[9px] uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500 text-white font-bold shadow-sm flex items-center gap-1">
                +{pct}% Uplift
              </span>
            )}
          </div>
          <p className="font-mono text-[11px] text-on-surface-variant/80 bg-surface-container px-1.5 py-0.5 rounded border border-border-glass inline-block">
            {result.sku}
          </p>
        </div>
        <div className="text-right shrink-0 bg-surface-container-low px-3 py-2 rounded-xl border border-border-glass">
          <p className={`text-2xl font-bold font-mono tracking-tight ${uplift ? 'text-amber-500' : 'text-emerald-500'}`}>
            {result.scenario_adjusted_daily.toFixed(1)}
          </p>
          <p className="font-label-xs text-[9px] uppercase tracking-wider text-on-surface-variant mt-0.5">Adj. Daily</p>
        </div>
      </div>

      {/* Chart */}
      <div className="h-[200px] mb-6 relative z-10 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={result.recharts_data} margin={{ top: 15, right: 10, bottom: 0, left: -25 }}>
            <defs>
              <linearGradient id={`g-adj-${result.sku}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={uplift ? "#f59e0b" : "#10b981"} stopOpacity={0.4} />
                <stop offset="100%" stopColor={uplift ? "#f59e0b" : "#10b981"} stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id={`g-base-${result.sku}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.15} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="var(--border)" strokeOpacity={0.3} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
              tickFormatter={(v) => new Date(v).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
              axisLine={false} tickLine={false} dy={12}
              minTickGap={20}
            />
            <YAxis 
              tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} 
              axisLine={false} tickLine={false} dx={-10} 
              domain={['dataMin - (dataMin * 0.1)', 'dataMax + (dataMax * 0.1)']}
            />
            <Tooltip content={<ForecastTooltip />} cursor={{ stroke: 'var(--border)', strokeWidth: 1, strokeDasharray: '4 4' }} />
            
            <Area type="monotone" dataKey="baseline" stroke="#3b82f6" strokeWidth={2} fill={`url(#g-base-${result.sku})`} dot={false} name="Baseline" strokeDasharray="5 5" />
            <Area type="monotone" dataKey="adjusted" stroke={uplift ? "#f59e0b" : "#10b981"} strokeWidth={3} fill={`url(#g-adj-${result.sku})`} dot={false} name="Scenario Adj" activeDot={{ r: 6, strokeWidth: 0, fill: uplift ? "#f59e0b" : "#10b981" }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-auto space-y-4 relative z-10">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { label: 'Baseline/Day', value: result.baseline_daily.toFixed(1), icon: <TrendingUp className="w-3 h-3" /> },
            { label: 'Multiplier', value: `×${result.multiplier.toFixed(2)}`, icon: <TrendingUp className="w-3 h-3" /> },
            { label: 'Source Model', value: result.data_source.includes('Holt-Winters') ? 'Holt-Winters' : 'Fallback', icon: <Database className="w-3 h-3" /> },
          ].map(({ label, value, icon }) => (
            <div key={label} className="rounded-xl p-3 bg-surface-container-low border border-border-glass text-center flex flex-col items-center justify-center">
              <p className="font-label-xs text-[9px] uppercase tracking-wider text-on-surface-variant flex items-center gap-1">
                {icon} {label}
              </p>
              <p className="font-headline-sm font-bold font-mono text-on-surface mt-1.5">{value}</p>
            </div>
          ))}
        </div>

        {result.reasons?.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-2 border-t border-border-glass/60">
            {result.reasons.map((r, i) => (
              <span key={i} className="font-label-xs text-[10px] px-2 py-1 rounded bg-amber-500/10 text-amber-600 border border-amber-500/20 uppercase tracking-wider font-bold">
                {r}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ForecastPage() {
  const [results, setResults] = useState<ForecastResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'multiplier'>('multiplier');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const products = await apiGet<{ sku: string; name: string }[]>('/forecast/all');
      const forecasts = await Promise.allSettled(
        products.map((p) => apiGet<ForecastResult>(`/forecast/${p.sku}`))
      );
      const ok = forecasts
        .filter((r): r is PromiseFulfilledResult<ForecastResult> => r.status === 'fulfilled')
        .map((r) => r.value);
      setResults(ok);
    } catch { } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = results
    .filter((r) => !search || r.name.toLowerCase().includes(search.toLowerCase()) || r.sku.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => sortBy === 'multiplier' ? b.multiplier - a.multiplier : a.name.localeCompare(b.name));

  const withUplift = results.filter((r) => r.multiplier > 1.0);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h3 className="font-headline-lg text-on-surface">Demand Forecast</h3>
          <p className="font-body-md text-on-surface-variant mt-1">
            Holt-Winters 14-day models · <strong className="text-amber-500">{withUplift.length} items</strong> with scenario uplift
          </p>
        </div>
        <button onClick={load} className="p-2 border border-border-glass rounded-lg text-on-surface-variant hover:text-primary hover:border-primary transition-all shrink-0">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
        <div className="relative flex-1 max-w-xl">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            className="nexus-input w-full pl-10 pr-4 py-2.5 rounded-lg text-sm"
            placeholder="Search SKUs or product names…"
            value={search} onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2 bg-surface-container rounded-lg p-1 border border-border-glass self-start sm:self-auto">
          {(['multiplier', 'name'] as const).map((s) => (
            <button key={s} onClick={() => setSortBy(s)}
              className={`px-4 py-1.5 rounded-md font-label-md text-xs tracking-wider uppercase transition-colors ${
                sortBy === s ? 'bg-surface-container-high text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {s === 'multiplier' ? '⬆ Impact' : 'A–Z'}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {[0,1,2,3].map((i) => <div key={i} className="glass-panel h-[420px] rounded-2xl border border-border-glass animate-pulse" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-panel py-16 flex flex-col items-center gap-4 rounded-2xl border border-border-glass border-dashed">
          <div className="w-16 h-16 rounded-2xl bg-surface-container flex items-center justify-center border border-border-glass">
            <TrendingUp className="w-8 h-8 text-on-surface-variant/40" />
          </div>
          <p className="text-sm font-bold text-on-surface">No forecast data generated</p>
          <p className="text-xs text-on-surface-variant">Run the morning briefing on the dashboard to trigger the ML models.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {filtered.map((r) => <ForecastCard key={r.sku} result={r} />)}
        </div>
      )}
    </div>
  );
}
