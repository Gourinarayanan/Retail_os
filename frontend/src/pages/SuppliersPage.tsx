import React, { useState, useEffect, useCallback } from 'react';
import { Truck, Star, MapPin, Search, ChevronDown, ChevronUp, Phone, RefreshCw, Shield } from 'lucide-react';
import { ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, Tooltip } from 'recharts';
import type { Supplier, SupplierRanking } from '../types';
import { apiGet } from '../api/client';

// ── Reliability bar ───────────────────────────────────────────────────────────

function ReliabilityBar({ value }: { value: number }) {
  const color = value >= 90 ? '#34d399' : value >= 75 ? '#fbbf24' : '#f43f5e';
  return (
    <div className="flex items-center gap-2 w-full">
      <div className="flex-1 rounded-full overflow-hidden" style={{ height: 6, background: 'var(--border)' }}>
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${value}%`, background: color }} />
      </div>
      <span className="mono text-xs font-bold w-10 text-right" style={{ color }}>{value.toFixed(0)}%</span>
    </div>
  );
}

// ── Star rating ───────────────────────────────────────────────────────────────

function StarRating({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((s) => (
        <Star key={s} size={11} fill={s <= Math.round(value) ? '#fbbf24' : 'none'} style={{ color: '#fbbf24' }} />
      ))}
      <span className="mono text-[11px] ml-1" style={{ color: 'var(--text-muted)' }}>{value.toFixed(1)}</span>
    </div>
  );
}

// ── Supplier Card ─────────────────────────────────────────────────────────────

function SupplierCard({ supplier }: { supplier: Supplier }) {
  const [expanded, setExpanded] = useState(false);
  const [compare,  setCompare]  = useState<SupplierRanking[] | null>(null);

  const radarData = [
    { axis: 'On-Time',    value: supplier.on_time_rate_pct },
    { axis: 'Rating',     value: supplier.avg_rating * 20  },
    { axis: 'Categories', value: Math.min(supplier.supply_categories.length * 20, 100) },
    { axis: 'Experience', value: Math.min(supplier.total_deliveries_90d * 2, 100) },
  ];

  const reliabilityColor = supplier.on_time_rate_pct >= 90 ? '#34d399'
                         : supplier.on_time_rate_pct >= 75 ? '#fbbf24'
                         : '#f43f5e';

  return (
    <div className="card flex flex-col gap-4 transition-all duration-200">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div
            className="flex h-11 w-11 items-center justify-center rounded-xl shrink-0 font-bold text-lg"
            style={{ background: 'rgba(59,130,246,0.1)', color: '#60a5fa' }}
          >
            {supplier.name.charAt(0)}
          </div>
          <div>
            <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{supplier.name}</h3>
            <div className="flex items-center gap-2 mt-0.5 flex-wrap">
              <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-muted)' }}>
                <MapPin size={10} /> {supplier.region}
              </div>
              <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-muted)' }}>
                <Phone size={10} /> {supplier.whatsapp_number}
              </div>
            </div>
            <div className="flex flex-wrap gap-1 mt-1.5">
              {supplier.supply_categories.map((c) => (
                <span key={c} className="badge-blue text-[10px]">{c.trim()}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Score */}
        <div className="text-right shrink-0">
          <div className="text-2xl font-bold mono" style={{ color: reliabilityColor }}>
            {supplier.on_time_rate_pct.toFixed(0)}%
          </div>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>on-time</p>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        <div className="flex flex-col gap-1">
          <p className="section-title">On-Time Rate</p>
          <ReliabilityBar value={supplier.on_time_rate_pct} />
        </div>
        <div className="flex flex-col gap-1">
          <p className="section-title">Rating</p>
          <StarRating value={supplier.avg_rating} />
        </div>
        <div className="flex flex-col gap-1">
          <p className="section-title">Deliveries (90d)</p>
          <span className="mono text-sm font-bold" style={{ color: 'var(--text-primary)' }}>
            {supplier.total_deliveries_90d}
          </span>
        </div>
      </div>

      {/* Expand */}
      <button
        onClick={() => setExpanded((e) => !e)}
        className="flex items-center gap-1.5 text-xs self-start"
        style={{ color: 'var(--text-muted)' }}
      >
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        {expanded ? 'Hide' : 'Show'} delivery history
      </button>

      {expanded && supplier.delivery_history && (
        <div className="flex flex-col gap-1.5">
          <p className="section-title">Last 10 Deliveries</p>
          {supplier.delivery_history.slice(0, 10).map((d) => (
            <div key={d.id} className="flex items-center justify-between text-xs px-3 py-1.5 rounded-lg"
              style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--text-muted)' }}>{d.order_date}</span>
              <span className={d.on_time ? 'badge-green' : 'badge-red'}>{d.on_time ? '✓ On-time' : '✗ Late'}</span>
              {d.rating && <StarRating value={d.rating} />}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [search,    setSearch]    = useState('');
  const [sortBy,    setSortBy]    = useState<'reliability' | 'name'>('reliability');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<Supplier[]>('/suppliers');
      setSuppliers(data);
    } catch {/* toast */} finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = suppliers
    .filter((s) => !search || s.name.toLowerCase().includes(search.toLowerCase()) || s.region.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) =>
      sortBy === 'reliability'
        ? b.on_time_rate_pct - a.on_time_rate_pct
        : a.name.localeCompare(b.name)
    );

  const avgReliability = suppliers.length
    ? (suppliers.reduce((s, x) => s + x.on_time_rate_pct, 0) / suppliers.length).toFixed(0)
    : '—';

  return (
    <div className="page-enter flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Supplier Intelligence</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            {suppliers.length} active suppliers · avg reliability {avgReliability}%
          </p>
        </div>
        <button onClick={load} className="btn-ghost p-2"><RefreshCw size={14} /></button>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input className="input pl-9" placeholder="Search suppliers…" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        {(['reliability', 'name'] as const).map((s) => (
          <button key={s} onClick={() => setSortBy(s)} className="btn-ghost text-xs py-2"
            style={{ color: sortBy === s ? '#93c5fd' : undefined, borderColor: sortBy === s ? 'rgba(59,130,246,0.4)' : undefined }}>
            {s === 'reliability' ? '⬆ Reliability' : 'A–Z'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-2 gap-4">{[0,1,2,3].map((i) => <div key={i} className="skeleton h-48 rounded-xl" />)}</div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {filtered.map((s) => <SupplierCard key={s.id} supplier={s} />)}
        </div>
      )}
    </div>
  );
}
