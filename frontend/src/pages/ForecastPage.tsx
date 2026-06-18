import React, { useState, useEffect, useCallback } from 'react';
import { Search, TrendingUp, RefreshCw, Info } from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ReferenceLine
} from 'recharts';
import type { ForecastResult } from '../types';
import { apiGet } from '../api/client';

// ── Custom tooltip ────────────────────────────────────────────────────────────

function ForecastTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const date = new Date(label).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' });
  return (
    <div className="rounded-xl px-3 py-2.5 text-xs flex flex-col gap-1"
      style={{ background: '#0d1526', border: '1px solid var(--border)', minWidth: 140 }}>
      <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>{date}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex justify-between gap-4">
          <span style={{ color: p.color }}>{p.name}</span>
          <span className="mono font-semibold" style={{ color: 'var(--text-primary)' }}>
            {p.value?.toFixed(1)}
          </span>
        </div>
      ))}
    </div>
  );
}

// ── Forecast Card ─────────────────────────────────────────────────────────────

function ForecastCard({ result }: { result: ForecastResult }) {
  const uplift = result.multiplier > 1.0;
  const pct = Math.round((result.multiplier - 1) * 100);
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="card flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{result.name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="mono text-[11px]" style={{ color: 'var(--text-muted)' }}>{result.sku}</span>
            {uplift && (
              <span className="badge-amber text-[10px]">
                +{pct}% scenario uplift
              </span>
            )}
          </div>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold mono" style={{ color: uplift ? '#fbbf24' : '#34d399' }}>
            {result.scenario_adjusted_daily.toFixed(1)}
          </p>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>adj. daily demand</p>
        </div>
      </div>

      {/* Chart */}
      <div style={{ height: 180 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={result.recharts_data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
            <defs>
              <linearGradient id={`g-adj-${result.sku}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#f59e0b" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.02} />
              </linearGradient>
              <linearGradient id={`g-base-${result.sku}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 9 }}
              tickFormatter={(v) => new Date(v).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
            />
            <YAxis tick={{ fontSize: 9 }} />
            <Tooltip content={<ForecastTooltip />} />
            <ReferenceLine x={today} stroke="rgba(255,255,255,0.15)" strokeDasharray="4 2" label={{ value: 'Today', fontSize: 9, fill: '#94a3b8' }} />
            {/* Confidence band */}
            <Area type="monotone" dataKey="upper" stroke="none" fill="rgba(59,130,246,0.08)" name="Upper" />
            <Area type="monotone" dataKey="lower" stroke="none" fill="var(--bg-base)"  name="Lower" />
            {/* Baseline */}
            <Area type="monotone" dataKey="baseline" stroke="#3b82f6" strokeWidth={1.5}
              fill={`url(#g-base-${result.sku})`} dot={false} name="Baseline" strokeDasharray="4 2" />
            {/* Adjusted (scenario) */}
            <Area type="monotone" dataKey="adjusted" stroke="#f59e0b" strokeWidth={2}
              fill={`url(#g-adj-${result.sku})`} dot={false} name="Scenario-Adjusted" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: 'Baseline/day', value: result.baseline_daily.toFixed(1) },
          { label: 'Multiplier',   value: `×${result.multiplier.toFixed(2)}` },
          { label: 'Data source',  value: result.data_source.includes('Prophet') ? 'Prophet' : 'Fallback' },
        ].map(({ label, value }) => (
          <div key={label} className="rounded-lg px-2.5 py-2 text-center"
            style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
            <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{label}</p>
            <p className="text-sm font-bold mono" style={{ color: 'var(--text-primary)' }}>{value}</p>
          </div>
        ))}
      </div>

      {/* Reasons */}
      {result.reasons?.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {result.reasons.map((r, i) => (
            <span key={i} className="badge-amber text-[10px]">{r}</span>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ForecastPage() {
  const [results,  setResults]  = useState<ForecastResult[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [search,   setSearch]   = useState('');
  const [sortBy,   setSortBy]   = useState<'name' | 'multiplier'>('multiplier');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      // Load all SKUs, then fetch individual forecasts
      const products = await apiGet<{ sku: string; name: string }[]>('/forecast/all');
      const forecasts = await Promise.allSettled(
        products.map((p) => apiGet<ForecastResult>(`/forecast/${p.sku}`))
      );
      const ok = forecasts
        .filter((r): r is PromiseFulfilledResult<ForecastResult> => r.status === 'fulfilled')
        .map((r) => r.value);
      setResults(ok);
    } catch {/* toast */} finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = results
    .filter((r) => !search || r.name.toLowerCase().includes(search.toLowerCase()) || r.sku.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) =>
      sortBy === 'multiplier'
        ? b.multiplier - a.multiplier
        : a.name.localeCompare(b.name)
    );

  const withUplift = results.filter((r) => r.multiplier > 1.0);

  return (
    <div className="page-enter flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Demand Forecast</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Prophet 14-day forecast · {withUplift.length} products with scenario uplift
          </p>
        </div>
        <button onClick={load} className="btn-ghost p-2"><RefreshCw size={14} /></button>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input className="input pl-9" placeholder="Search products…" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <div className="flex items-center gap-1.5">
          {(['multiplier', 'name'] as const).map((s) => (
            <button key={s} onClick={() => setSortBy(s)}
              className="btn-ghost text-xs py-2"
              style={{ color: sortBy === s ? '#93c5fd' : undefined, borderColor: sortBy === s ? 'rgba(59,130,246,0.4)' : undefined }}>
              {s === 'multiplier' ? '⬆ Multiplier' : 'A–Z'}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 gap-4">{[0,1,2,3].map((i) => <div key={i} className="skeleton h-72 rounded-xl" />)}</div>
      ) : filtered.length === 0 ? (
        <div className="card py-12 flex flex-col items-center gap-2" style={{ borderStyle: 'dashed' }}>
          <TrendingUp size={28} style={{ color: 'var(--text-muted)' }} />
          <p style={{ color: 'var(--text-muted)' }}>Run morning briefing to generate Prophet forecasts</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {filtered.map((r) => <ForecastCard key={r.sku} result={r} />)}
        </div>
      )}
    </div>
  );
}
