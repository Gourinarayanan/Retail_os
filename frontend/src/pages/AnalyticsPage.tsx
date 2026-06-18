import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, ChevronDown } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  LineChart, Line,
  AreaChart, Area,
  Cell,
} from 'recharts';
import type {
  SalesTrendPoint, TopProduct,
  SupplierPerformance, InventoryHealthItem,
  ForecastDay,
} from '../types';
import { apiGet } from '../api/client';

// ── Types for forecast list endpoint ─────────────────────────────────────────

interface ForecastSummary {
  product_id:       number;
  sku:              string;
  name:             string;
  category:         string;
  avg_daily_demand: number;
}

interface ForecastDetail {
  product_id:              number;
  sku:                     string;
  name:                    string;
  recharts_data:           ForecastDay[];
  baseline_daily:          number;
  scenario_adjusted_daily: number;
  multiplier:              number;
  reasons:                 string[];
  data_source:             string;
}

// ── Colour helpers ────────────────────────────────────────────────────────────

const CAT_COLORS: Record<string, string> = {
  dairy:         '#60a5fa',
  staples:       '#34d399',
  snacks:        '#fbbf24',
  beverages:     '#f87171',
  spices:        '#c084fc',
  cleaning:      '#38bdf8',
  personal_care: '#fb923c',
};
const fallback = (i: number) => ['#60a5fa','#34d399','#fbbf24','#f87171','#c084fc','#38bdf8'][i % 6];

function reliabilityColor(v: number) {
  return v >= 90 ? '#34d399' : v >= 75 ? '#fbbf24' : '#f87171';
}

// ── Shared custom tooltip ─────────────────────────────────────────────────────

function Tip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl px-3 py-2 text-xs flex flex-col gap-1"
      style={{ background: '#0d1526', border: '1px solid var(--border)', minWidth: 140 }}>
      <p className="font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex justify-between gap-6">
          <span style={{ color: p.color || p.stroke || '#94a3b8' }}>{p.name}</span>
          <span className="mono font-bold" style={{ color: 'var(--text-primary)' }}>
            {typeof p.value === 'number'
              ? (p.name?.includes('%') || p.name?.toLowerCase().includes('rate')
                  ? `${p.value.toFixed(1)}%`
                  : p.value.toFixed(1))
              : p.value}
          </span>
        </div>
      ))}
    </div>
  );
}

// ── Tab 1: Demand Forecast ────────────────────────────────────────────────────

function DemandForecastTab() {
  const [skus,      setSkus]      = useState<ForecastSummary[]>([]);
  const [selected,  setSelected]  = useState<string>('');
  const [detail,    setDetail]    = useState<ForecastDetail | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // GET /api/forecast/all → ForecastSummary[]
  useEffect(() => {
    apiGet<ForecastSummary[]>('/forecast/all')
      .then(data => {
        setSkus(data);
        if (data.length > 0) setSelected(data[0].sku);
      })
      .catch(() => {})
      .finally(() => setLoadingList(false));
  }, []);

  // GET /api/forecast/{sku} → ForecastDetail
  useEffect(() => {
    if (!selected) return;
    setLoadingDetail(true);
    apiGet<ForecastDetail>(`/forecast/${selected}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setLoadingDetail(false));
  }, [selected]);

  const tickEvery = Math.max(1, Math.ceil((detail?.recharts_data.length ?? 14) / 7));

  return (
    <div className="flex flex-col gap-5">
      {/* SKU selector */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="relative">
          <select
            id="forecast-sku-select"
            className="input pr-8 text-sm appearance-none"
            value={selected}
            onChange={e => setSelected(e.target.value)}
            disabled={loadingList}
          >
            {skus.map(s => (
              <option key={s.sku} value={s.sku}>{s.name} ({s.sku})</option>
            ))}
          </select>
          <ChevronDown size={12} className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"
            style={{ color: 'var(--text-muted)' }} />
        </div>
        {detail && (
          <div className="flex items-center gap-2 flex-wrap">
            <span className="badge-blue text-[10px]">
              Baseline {detail.baseline_daily.toFixed(1)}/day
            </span>
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
              detail.multiplier > 1.1 ? 'badge-green' : detail.multiplier < 0.9 ? 'badge-red' : 'badge-gray'
            }`}>
              ×{detail.multiplier.toFixed(2)} scenario
            </span>
            <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
              {detail.data_source}
            </span>
          </div>
        )}
      </div>

      {/* Chart */}
      <div className="card flex flex-col gap-4">
        <div>
          <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>
            14-Day Prophet Forecast — {detail?.name ?? '…'}
          </h3>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Baseline vs scenario-adjusted demand · shaded band = confidence interval
          </p>
        </div>
        {loadingDetail || !detail ? (
          <div className="skeleton h-64 rounded-lg" />
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={detail.recharts_data} margin={{ top: 8, right: 12, bottom: 0, left: -10 }}>
              <defs>
                <linearGradient id="confBand" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.03} />
                </linearGradient>
                <linearGradient id="adjGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#34d399" stopOpacity={0.12} />
                  <stop offset="95%" stopColor="#34d399" stopOpacity={0.01} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#64748b' }}
                tickFormatter={(v, i) => i % tickEvery === 0
                  ? new Date(v).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''} />
              <YAxis tick={{ fontSize: 9, fill: '#64748b' }} />
              <Tooltip content={<Tip />} />
              <Legend wrapperStyle={{ fontSize: 10 }} />
              {/* Confidence band: area between lower and upper */}
              <Area type="monotone" dataKey="upper" name="Upper bound"
                stroke="transparent" fill="url(#confBand)" legendType="none" />
              <Area type="monotone" dataKey="lower" name="Lower bound"
                stroke="transparent" fill="white" fillOpacity={0} legendType="none" />
              {/* Baseline */}
              <Line type="monotone" dataKey="baseline" name="Baseline"
                stroke="#60a5fa" strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
              {/* Scenario-adjusted */}
              <Line type="monotone" dataKey="adjusted" name="Scenario adjusted"
                stroke="#34d399" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {/* Scenario reasons */}
        {detail && detail.reasons.length > 0 && (
          <div className="flex flex-col gap-1 pt-2" style={{ borderTop: '1px solid var(--border)' }}>
            <p className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
              Scenario drivers
            </p>
            {detail.reasons.map((r, i) => (
              <p key={i} className="text-xs" style={{ color: 'var(--text-secondary)' }}>· {r}</p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Tab 2: Sales Trends ───────────────────────────────────────────────────────

function SalesTrendsTab() {
  const [days,       setDays]       = useState(30);
  const [data,       setData]       = useState<SalesTrendPoint[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading,    setLoading]    = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    apiGet<{ data: SalesTrendPoint[]; categories: string[]; days: number }>(
      `/analytics/sales-trend?days=${days}`
    )
      .then(r => { setData(r.data); setCategories(r.categories); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [days]);

  useEffect(() => { load(); }, [load]);

  const tickEvery = Math.max(1, Math.ceil(data.length / 8));

  return (
    <div className="card flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>Revenue by Category</h3>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Daily revenue · last {days} days</p>
        </div>
        <div className="flex gap-1">
          {[7, 30, 90].map(d => (
            <button key={d} onClick={() => setDays(d)}
              className="text-xs px-2.5 py-1 rounded-lg font-medium"
              style={{
                background: days === d ? 'rgba(59,130,246,0.15)' : 'var(--bg-base)',
                border: days === d ? '1px solid rgba(59,130,246,0.3)' : '1px solid var(--border)',
                color: days === d ? '#93c5fd' : 'var(--text-secondary)',
              }}>
              {d}d
            </button>
          ))}
        </div>
      </div>
      {loading ? <div className="skeleton h-56 rounded-lg" /> : (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }} barSize={6}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#64748b' }}
              tickFormatter={(v, i) => i % tickEvery === 0
                ? new Date(v).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''} />
            <YAxis tick={{ fontSize: 9, fill: '#64748b' }}
              tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
            <Tooltip content={<Tip />} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            {categories.map((cat, i) => (
              <Bar key={cat} dataKey={cat} name={cat} stackId="a"
                fill={CAT_COLORS[cat] ?? fallback(i)}
                radius={i === categories.length - 1 ? [3, 3, 0, 0] : [0, 0, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

// ── Tab 3: Weather & Event Impact ─────────────────────────────────────────────
// The backend aggregates revenue by event_tag (normal/hartal_pre/hartal/onam/rainy)
// at the SalesRecord DB level. There's no dedicated endpoint yet — Tab shows top products
// split by category as a proxy, with an honest note.

function EventImpactTab() {
  const [best,    setBest]    = useState<TopProduct[]>([]);
  const [worst,   setWorst]   = useState<TopProduct[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<{ best: TopProduct[]; worst: TopProduct[] }>('/analytics/top-products?days=30&limit=8')
      .then(r => { setBest(r.best); setWorst(r.worst); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const combined = [...best, ...worst.filter(w => !best.find(b => b.product_id === w.product_id))];
  const maxRev = Math.max(...combined.map(p => p.total_revenue), 1);

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-xl px-4 py-3"
        style={{ background: 'rgba(59,130,246,0.06)', border: '1px solid rgba(59,130,246,0.15)' }}>
        <p className="text-xs" style={{ color: '#93c5fd' }}>
          <strong>Note:</strong> Event-tag scatter (hartal/onam/rainy vs revenue) requires a dedicated
          <code className="mono mx-1">GET /api/analytics/event-impact</code> endpoint. 
          Showing 30-day top &amp; bottom products by revenue instead — all figures from DB.
        </p>
      </div>

      {loading ? <div className="skeleton h-64 rounded-lg" /> : (
        <div className="card flex flex-col gap-4">
          <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>
            Product Revenue — last 30 days
          </h3>
          <ResponsiveContainer width="100%" height={Math.max(combined.length * 28, 120)}>
            <BarChart data={combined} layout="vertical"
              margin={{ top: 0, right: 12, bottom: 0, left: 110 }} barSize={12}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.04)" />
              <XAxis type="number" tick={{ fontSize: 9, fill: '#64748b' }}
                tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#94a3b8' }} width={108} />
              <Tooltip content={<Tip />} />
              <Bar dataKey="total_revenue" name="Revenue (₹)" radius={[0, 4, 4, 0]}>
                {combined.map((entry, i) => (
                  <Cell key={i} fill={
                    entry.total_revenue / maxRev > 0.7 ? '#34d399'
                    : entry.total_revenue / maxRev > 0.4 ? '#60a5fa'
                    : '#f87171'
                  } />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

// ── Tab 4: Supplier Performance ───────────────────────────────────────────────

function SupplierTab() {
  const [data,    setData]    = useState<SupplierPerformance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<SupplierPerformance[]>('/analytics/supplier-performance')
      .then(setData).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="card flex flex-col gap-4">
      <div>
        <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>
          On-Time Delivery Rate
        </h3>
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Last 180 days · all active suppliers</p>
      </div>
      {loading ? <div className="skeleton h-52 rounded-lg" /> : (
        <>
          <ResponsiveContainer width="100%" height={Math.max(data.length * 36, 120)}>
            <BarChart data={data} layout="vertical"
              margin={{ top: 0, right: 12, bottom: 0, left: 100 }} barSize={14}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.04)" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 9, fill: '#64748b' }}
                tickFormatter={v => `${v}%`} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#94a3b8' }} width={98} />
              <Tooltip content={<Tip />} />
              <Bar dataKey="on_time_rate_pct" name="On-time %" radius={[0, 4, 4, 0]}>
                {data.map((entry, i) => (
                  <Cell key={i} fill={reliabilityColor(entry.on_time_rate_pct)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Summary table */}
          <div className="flex flex-col gap-0 overflow-hidden rounded-lg"
            style={{ border: '1px solid var(--border)' }}>
            <div className="grid text-[10px] font-semibold uppercase px-4 py-2"
              style={{ gridTemplateColumns: '1fr 80px 70px 80px', background: 'var(--bg-base)', color: 'var(--text-muted)' }}>
              <span>Supplier</span><span className="text-right">On-time</span>
              <span className="text-right">Rating</span><span className="text-right">Deliveries</span>
            </div>
            {data.map((s, i) => (
              <div key={s.supplier_id} className="grid text-xs px-4 py-2.5"
                style={{
                  gridTemplateColumns: '1fr 80px 70px 80px',
                  borderTop: i > 0 ? '1px solid var(--border)' : 'none',
                }}>
                <span style={{ color: 'var(--text-primary)' }}>{s.name}</span>
                <span className="text-right mono font-semibold"
                  style={{ color: reliabilityColor(s.on_time_rate_pct) }}>
                  {s.on_time_rate_pct.toFixed(1)}%
                </span>
                <span className="text-right mono" style={{ color: '#fbbf24' }}>
                  ★ {s.avg_rating.toFixed(1)}
                </span>
                <span className="text-right mono" style={{ color: 'var(--text-muted)' }}>
                  {s.total_deliveries}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// ── Tab 5: Inventory Health ───────────────────────────────────────────────────

function InventoryHealthTab() {
  const [data,    setData]    = useState<InventoryHealthItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<InventoryHealthItem[]>('/analytics/inventory-health')
      .then(setData).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const statusColor: Record<string, string> = {
    out_of_stock: '#f43f5e', critical: '#f43f5e', warning: '#fbbf24', excess: '#94a3b8', ok: '#34d399',
  };
  const statusLabel: Record<string, string> = {
    out_of_stock: 'Out', critical: 'Crit', warning: 'Warn', excess: 'Excess', ok: 'OK',
  };

  const displayData = data.slice(0, 20).map(d => ({
    ...d,
    days_remaining: d.days_remaining >= 999 ? null : d.days_remaining,
  }));

  return (
    <div className="card flex flex-col gap-4">
      <div>
        <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>
          Inventory Health — Days Remaining
        </h3>
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
          Sorted by urgency · red = critical / out of stock
        </p>
      </div>
      {loading ? <div className="skeleton h-64 rounded-lg" /> : (
        <>
          <ResponsiveContainer width="100%" height={Math.max(displayData.length * 26, 120)}>
            <BarChart data={displayData} layout="vertical"
              margin={{ top: 0, right: 50, bottom: 0, left: 110 }} barSize={10}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.04)" />
              <XAxis type="number" tick={{ fontSize: 9, fill: '#64748b' }}
                tickFormatter={v => `${v}d`} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 9, fill: '#94a3b8' }} width={108} />
              <Tooltip content={<Tip />} />
              <Bar dataKey="days_remaining" name="Days remaining" radius={[0, 4, 4, 0]}>
                {displayData.map((entry, i) => (
                  <Cell key={i} fill={statusColor[entry.status] ?? '#34d399'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Legend */}
          <div className="flex flex-wrap gap-2">
            {Object.entries(statusLabel).map(([k, v]) => (
              <span key={k} className="flex items-center gap-1.5 text-[10px]" style={{ color: 'var(--text-muted)' }}>
                <span className="w-2.5 h-2.5 rounded-sm inline-block" style={{ background: statusColor[k] }} />
                {v} ({data.filter(d => d.status === k).length})
              </span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

const TABS = [
  { id: 'forecast',  label: 'Demand Forecast' },
  { id: 'sales',     label: 'Sales Trends'    },
  { id: 'events',    label: 'Event Impact'    },
  { id: 'suppliers', label: 'Suppliers'       },
  { id: 'inventory', label: 'Inventory Health'},
] as const;

type TabId = typeof TABS[number]['id'];

export default function AnalyticsPage() {
  const [tab, setTab] = useState<TabId>('forecast');

  return (
    <div className="page-enter flex flex-col gap-5">
      <div>
        <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Analytics</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
          Demand forecast · sales trends · supplier reliability · inventory health
        </p>
      </div>

      {/* Tab bar */}
      <div className="flex items-center gap-1 flex-wrap"
        style={{ borderBottom: '1px solid var(--border)', paddingBottom: '0' }}>
        {TABS.map(t => (
          <button
            key={t.id}
            id={`tab-analytics-${t.id}`}
            onClick={() => setTab(t.id)}
            className="text-xs px-4 py-2.5 font-medium transition-all relative"
            style={{
              color: tab === t.id ? '#93c5fd' : 'var(--text-muted)',
              background: 'transparent',
              borderBottom: tab === t.id ? '2px solid #3b82f6' : '2px solid transparent',
              marginBottom: -1,
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex flex-col gap-4">
        {tab === 'forecast'  && <DemandForecastTab />}
        {tab === 'sales'     && <SalesTrendsTab />}
        {tab === 'events'    && <EventImpactTab />}
        {tab === 'suppliers' && <SupplierTab />}
        {tab === 'inventory' && <InventoryHealthTab />}
      </div>
    </div>
  );
}
