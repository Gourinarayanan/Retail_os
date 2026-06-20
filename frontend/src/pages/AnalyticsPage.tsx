import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, ChevronDown, BarChart2, TrendingUp, AlertTriangle, Package, Truck, Layers } from 'lucide-react';
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

const CAT_COLORS: Record<string, string> = {
  dairy:         '#3b82f6',
  staples:       '#10b981',
  snacks:        '#f59e0b',
  beverages:     '#ef4444',
  spices:        '#8b5cf6',
  cleaning:      '#0ea5e9',
  personal_care: '#f97316',
};
const fallback = (i: number) => ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#0ea5e9'][i % 6];

function reliabilityColorClass(v: number) {
  return v >= 90 ? 'text-emerald-500' : v >= 75 ? 'text-amber-500' : 'text-error';
}
function reliabilityColorHex(v: number) {
  return v >= 90 ? '#10b981' : v >= 75 ? '#f59e0b' : '#ef4444';
}

function Tip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl px-4 py-3 text-xs flex flex-col gap-2 bg-surface-container-high border border-border-glass shadow-lg min-w-[160px]">
      <p className="font-semibold text-on-surface border-b border-border-glass/60 pb-1">{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex justify-between gap-6 items-center">
          <span className="font-medium" style={{ color: p.color || p.stroke || '#94a3b8' }}>{p.name}</span>
          <span className="font-mono font-bold text-on-surface">
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

function DemandForecastTab() {
  const [skus,      setSkus]      = useState<ForecastSummary[]>([]);
  const [selected,  setSelected]  = useState<string>('');
  const [detail,    setDetail]    = useState<ForecastDetail | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    apiGet<ForecastSummary[]>('/forecast/all')
      .then(data => { setSkus(data); if (data.length > 0) setSelected(data[0].sku); })
      .catch(() => {})
      .finally(() => setLoadingList(false));
  }, []);

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
    <div className="flex flex-col gap-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="relative">
          <select
            id="forecast-sku-select"
            className="nexus-input pl-4 pr-10 py-2.5 rounded-lg text-sm appearance-none min-w-[240px] font-medium"
            value={selected}
            onChange={e => setSelected(e.target.value)}
            disabled={loadingList}
          >
            {skus.map(s => <option key={s.sku} value={s.sku}>{s.name} ({s.sku})</option>)}
          </select>
          <ChevronDown className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant" />
        </div>
        {detail && (
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-label-xs text-[10px] px-2.5 py-1 rounded-md bg-primary/10 text-primary border border-primary/20 uppercase tracking-wider font-bold">
              Baseline {detail.baseline_daily.toFixed(1)}/day
            </span>
            <span className={`font-label-xs text-[10px] px-2.5 py-1 rounded-md border uppercase tracking-wider font-bold ${
              detail.multiplier > 1.1 ? 'bg-emerald-50 text-emerald-600 border-emerald-200' :
              detail.multiplier < 0.9 ? 'bg-error/10 text-error border-error/20' :
              'bg-surface-container-high text-on-surface-variant border-border-glass'
            }`}>
              ×{detail.multiplier.toFixed(2)} scenario
            </span>
          </div>
        )}
      </div>

      <div className="glass-panel p-5 md:p-6 rounded-2xl border border-border-glass flex flex-col gap-6">
        <div>
          <h3 className="font-headline-sm text-base font-bold text-on-surface">
            14-Day Prophet Forecast — {detail?.name ?? '…'}
          </h3>
          <p className="font-body-sm text-sm text-on-surface-variant mt-1">
            Baseline vs scenario-adjusted demand · shaded band = confidence interval
          </p>
        </div>
        {loadingDetail || !detail ? (
          <div className="skeleton h-[300px] rounded-xl" />
        ) : (
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={detail.recharts_data} margin={{ top: 8, right: 12, bottom: 0, left: -20 }}>
                <defs>
                  <linearGradient id="confBand" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.03} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" strokeOpacity={0.4} />
                <XAxis dataKey="date" tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
                  tickFormatter={(v, i) => i % tickEvery === 0 ? new Date(v).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''}
                  axisLine={false} tickLine={false} dy={10} />
                <YAxis tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} axisLine={false} tickLine={false} dx={-10} />
                <Tooltip content={<Tip />} cursor={{ stroke: 'var(--border)', strokeWidth: 1, strokeDasharray: '4 4' }} />
                <Legend wrapperStyle={{ fontSize: 11, fontWeight: 500, paddingTop: 10 }} />
                <Area type="monotone" dataKey="upper" name="Upper bound" stroke="transparent" fill="url(#confBand)" legendType="none" />
                <Area type="monotone" dataKey="lower" name="Lower bound" stroke="transparent" fill="var(--bg-card)" fillOpacity={1} legendType="none" />
                <Line type="monotone" dataKey="baseline" name="Baseline" stroke="#3b82f6" strokeWidth={2} dot={false} strokeDasharray="4 4" />
                <Line type="monotone" dataKey="adjusted" name="Scenario adjusted" stroke="#10b981" strokeWidth={2.5} dot={false} activeDot={{ r: 5, strokeWidth: 0, fill: "#10b981" }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {detail && detail.reasons.length > 0 && (
          <div className="flex flex-col gap-2 pt-4 border-t border-border-glass">
            <p className="font-label-xs text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">
              Scenario drivers
            </p>
            <div className="flex flex-wrap gap-2">
              {detail.reasons.map((r, i) => (
                <span key={i} className="px-2.5 py-1 rounded bg-surface-container-low border border-border-glass text-xs font-medium text-on-surface-variant">
                  {r}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function SalesTrendsTab() {
  const [days,       setDays]       = useState(30);
  const [data,       setData]       = useState<SalesTrendPoint[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading,    setLoading]    = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    apiGet<{ data: SalesTrendPoint[]; categories: string[]; days: number }>(`/analytics/sales-trend?days=${days}`)
      .then(r => { setData(r.data); setCategories(r.categories); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [days]);

  useEffect(() => { load(); }, [load]);
  const tickEvery = Math.max(1, Math.ceil(data.length / 8));

  return (
    <div className="glass-panel p-5 md:p-6 rounded-2xl border border-border-glass flex flex-col gap-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h3 className="font-headline-sm text-base font-bold text-on-surface">Revenue by Category</h3>
          <p className="font-body-sm text-sm text-on-surface-variant mt-1">Daily revenue · last {days} days</p>
        </div>
        <div className="flex items-center gap-1 bg-surface-container rounded-lg p-1 border border-border-glass">
          {[7, 30, 90].map(d => (
            <button key={d} onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-md font-label-md text-xs tracking-wider uppercase transition-colors ${
                days === d ? 'bg-surface-container-high text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'
              }`}>
              {d}d
            </button>
          ))}
        </div>
      </div>

      {loading ? <div className="skeleton h-[300px] rounded-xl" /> : (
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }} barSize={8}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" strokeOpacity={0.4} />
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
                tickFormatter={(v, i) => i % tickEvery === 0 ? new Date(v).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''}
                axisLine={false} tickLine={false} dy={10} />
              <YAxis tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
                tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`}
                axisLine={false} tickLine={false} dx={-10} />
              <Tooltip content={<Tip />} cursor={{ fill: 'var(--surface-container-high)', opacity: 0.4 }} />
              <Legend wrapperStyle={{ fontSize: 11, fontWeight: 500, paddingTop: 10 }} />
              {categories.map((cat, i) => (
                <Bar key={cat} dataKey={cat} name={cat} stackId="a" fill={CAT_COLORS[cat] ?? fallback(i)}
                  radius={i === categories.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

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
    <div className="flex flex-col gap-6 animate-fade-in">
      <div className="p-4 rounded-xl bg-primary/10 border border-primary/20 flex items-start gap-3 text-primary">
        <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
        <p className="text-sm">
          <strong>Note:</strong> Event-tag scatter (hartal/onam/rainy vs revenue) requires a dedicated
          <code className="mx-1.5 px-1.5 py-0.5 rounded bg-primary/20 font-mono text-[10px]">GET /api/analytics/event-impact</code> endpoint. 
          Showing 30-day top &amp; bottom products by revenue instead — all figures from DB.
        </p>
      </div>

      {loading ? <div className="skeleton h-[400px] rounded-2xl" /> : (
        <div className="glass-panel p-5 md:p-6 rounded-2xl border border-border-glass flex flex-col gap-6">
          <h3 className="font-headline-sm text-base font-bold text-on-surface">Product Revenue — last 30 days</h3>
          <div className="w-full" style={{ height: Math.max(combined.length * 36, 200) }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={combined} layout="vertical" margin={{ top: 0, right: 12, bottom: 0, left: 110 }} barSize={16}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" strokeOpacity={0.4} />
                <XAxis type="number" tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
                  tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} axisLine={false} tickLine={false} dx={-10} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: 'var(--text-secondary)', fontWeight: 500 }} width={108} axisLine={false} tickLine={false} />
                <Tooltip content={<Tip />} cursor={{ fill: 'var(--surface-container-high)', opacity: 0.4 }} />
                <Bar dataKey="total_revenue" name="Revenue (₹)" radius={[0, 6, 6, 0]}>
                  {combined.map((entry, i) => (
                    <Cell key={i} fill={entry.total_revenue / maxRev > 0.7 ? '#10b981' : entry.total_revenue / maxRev > 0.4 ? '#3b82f6' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

function SupplierTab() {
  const [data,    setData]    = useState<SupplierPerformance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<SupplierPerformance[]>('/analytics/supplier-performance')
      .then(setData).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="glass-panel p-5 md:p-6 rounded-2xl border border-border-glass flex flex-col gap-6 animate-fade-in">
      <div>
        <h3 className="font-headline-sm text-base font-bold text-on-surface">On-Time Delivery Rate</h3>
        <p className="font-body-sm text-sm text-on-surface-variant mt-1">Last 180 days · all active suppliers</p>
      </div>

      {loading ? <div className="skeleton h-[400px] rounded-xl" /> : (
        <div className="space-y-8">
          <div className="w-full" style={{ height: Math.max(data.length * 40, 200) }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} layout="vertical" margin={{ top: 0, right: 12, bottom: 0, left: 100 }} barSize={20}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" strokeOpacity={0.4} />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
                  tickFormatter={v => `${v}%`} axisLine={false} tickLine={false} dx={-10} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: 'var(--text-secondary)', fontWeight: 500 }} width={98} axisLine={false} tickLine={false} />
                <Tooltip content={<Tip />} cursor={{ fill: 'var(--surface-container-high)', opacity: 0.4 }} />
                <Bar dataKey="on_time_rate_pct" name="On-time %" radius={[0, 6, 6, 0]}>
                  {data.map((entry, i) => <Cell key={i} fill={reliabilityColorHex(entry.on_time_rate_pct)} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="overflow-hidden rounded-xl border border-border-glass bg-surface-container-lowest">
            <div className="grid grid-cols-4 font-label-xs text-[10px] uppercase tracking-wider font-bold text-on-surface-variant px-4 py-3 bg-surface-container-low border-b border-border-glass">
              <span className="col-span-1">Supplier</span>
              <span className="text-right">On-time</span>
              <span className="text-right">Rating</span>
              <span className="text-right">Deliveries</span>
            </div>
            {data.map((s, i) => (
              <div key={s.supplier_id} className={`grid grid-cols-4 text-xs px-4 py-3.5 items-center ${i > 0 ? 'border-t border-border-glass/50' : ''}`}>
                <span className="col-span-1 font-semibold text-on-surface truncate">{s.name}</span>
                <span className={`text-right font-mono font-bold ${reliabilityColorClass(s.on_time_rate_pct)}`}>
                  {s.on_time_rate_pct.toFixed(1)}%
                </span>
                <span className="text-right font-mono font-medium text-amber-500">
                  ★ {s.avg_rating.toFixed(1)}
                </span>
                <span className="text-right font-mono font-medium text-on-surface-variant">
                  {s.total_deliveries}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function InventoryHealthTab() {
  const [data,    setData]    = useState<InventoryHealthItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<InventoryHealthItem[]>('/analytics/inventory-health')
      .then(setData).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const statusColor: Record<string, string> = { out_of_stock: '#ef4444', critical: '#ef4444', warning: '#f59e0b', excess: '#8b5cf6', ok: '#10b981' };
  const statusLabel: Record<string, string> = { out_of_stock: 'Out', critical: 'Crit', warning: 'Warn', excess: 'Excess', ok: 'OK' };

  const displayData = data.slice(0, 20).map(d => ({ ...d, days_remaining: d.days_remaining >= 999 ? null : d.days_remaining }));

  return (
    <div className="glass-panel p-5 md:p-6 rounded-2xl border border-border-glass flex flex-col gap-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h3 className="font-headline-sm text-base font-bold text-on-surface">Inventory Health — Days Remaining</h3>
          <p className="font-body-sm text-sm text-on-surface-variant mt-1">Sorted by urgency · Top 20 items</p>
        </div>
        {!loading && (
          <div className="flex flex-wrap gap-2">
            {Object.entries(statusLabel).map(([k, v]) => {
              const count = data.filter(d => d.status === k).length;
              if (count === 0) return null;
              return (
                <span key={k} className="flex items-center gap-1.5 text-[10px] px-2 py-1 rounded-md border bg-surface-container-lowest font-medium uppercase tracking-wider" style={{ borderColor: `${statusColor[k]}40`, color: statusColor[k] }}>
                  <span className="w-1.5 h-1.5 rounded-full" style={{ background: statusColor[k] }} />
                  {v} ({count})
                </span>
              );
            })}
          </div>
        )}
      </div>

      {loading ? <div className="skeleton h-[400px] rounded-xl" /> : (
        <div className="w-full" style={{ height: Math.max(displayData.length * 36, 200) }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={displayData} layout="vertical" margin={{ top: 0, right: 50, bottom: 0, left: 110 }} barSize={14}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" strokeOpacity={0.4} />
              <XAxis type="number" tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
                tickFormatter={v => `${v}d`} axisLine={false} tickLine={false} dx={-10} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: 'var(--text-secondary)', fontWeight: 500 }} width={108} axisLine={false} tickLine={false} />
              <Tooltip content={<Tip />} cursor={{ fill: 'var(--surface-container-high)', opacity: 0.4 }} />
              <Bar dataKey="days_remaining" name="Days remaining" radius={[0, 4, 4, 0]}>
                {displayData.map((entry, i) => <Cell key={i} fill={statusColor[entry.status] ?? '#10b981'} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

const TABS = [
  { id: 'forecast',  label: 'Demand Forecast', icon: <TrendingUp className="w-4 h-4" /> },
  { id: 'sales',     label: 'Sales Trends',    icon: <BarChart2 className="w-4 h-4" /> },
  { id: 'events',    label: 'Event Impact',    icon: <AlertTriangle className="w-4 h-4" /> },
  { id: 'suppliers', label: 'Suppliers',       icon: <Truck className="w-4 h-4" /> },
  { id: 'inventory', label: 'Inventory Health',icon: <Package className="w-4 h-4" /> },
] as const;
type TabId = typeof TABS[number]['id'];

export default function AnalyticsPage() {
  const [tab, setTab] = useState<TabId>('forecast');

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="font-headline-lg text-xl font-bold text-on-surface">Analytics & Intelligence</h1>
        <p className="font-body-md text-on-surface-variant mt-1">
          Deep dives into demand, sales velocity, supplier metrics, and inventory risks.
        </p>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar border-b border-border-glass">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-bold uppercase tracking-wider transition-all whitespace-nowrap border-b-2 ${
              tab === t.id ? 'text-primary border-primary' : 'text-on-surface-variant border-transparent hover:text-on-surface hover:border-border-glass'
            }`}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      <div className="pt-2">
        {tab === 'forecast'  && <DemandForecastTab />}
        {tab === 'sales'     && <SalesTrendsTab />}
        {tab === 'events'    && <EventImpactTab />}
        {tab === 'suppliers' && <SupplierTab />}
        {tab === 'inventory' && <InventoryHealthTab />}
      </div>
    </div>
  );
}
