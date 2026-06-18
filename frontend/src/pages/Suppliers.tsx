import React, { useState, useEffect, useCallback } from 'react';
import { Search, RefreshCw, Truck, Star, MapPin, Phone } from 'lucide-react';
import { apiGet } from '../api/client';

// ── Exact backend response shapes (from suppliers.py _supplier_summary) ───────

interface SupplierSummary {
  id:                   number;
  name:                 string;
  contact_name:         string;
  whatsapp_number:      string;
  email:                string | null;
  region:               string;
  supply_categories:    string[];   // already split by backend
  notes:                string | null;
  is_active:            boolean;
  on_time_rate_pct:     number;
  avg_rating:           number;
  total_deliveries_90d: number;
}

// ── Scoring helpers ───────────────────────────────────────────────────────────

function reliabilityColor(pct: number) {
  return pct >= 90 ? '#34d399' : pct >= 75 ? '#fbbf24' : '#f43f5e';
}

function ReliabilityBar({ value }: { value: number }) {
  const color = reliabilityColor(value);
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 rounded-full overflow-hidden" style={{ height: 5, background: 'var(--border)' }}>
        <div className="h-full rounded-full transition-all duration-700"
          style={{ width: `${value}%`, background: color }} />
      </div>
      <span className="mono text-xs font-bold w-10 text-right" style={{ color }}>{value.toFixed(0)}%</span>
    </div>
  );
}

function StarRow({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1,2,3,4,5].map(n => (
        <Star key={n} size={10}
          fill={n <= Math.round(value) ? '#fbbf24' : 'none'}
          style={{ color: '#fbbf24' }} />
      ))}
      <span className="mono text-[11px] ml-1" style={{ color: 'var(--text-muted)' }}>{value.toFixed(1)}</span>
    </div>
  );
}

// ── SupplierScoreCard ─────────────────────────────────────────────────────────

function SupplierScoreCard({ supplier, rank }: { supplier: SupplierSummary; rank: number }) {
  // Composite score: 50% reliability + 30% rating (normalised) + 20% regional (70 default)
  const reliabilityScore = supplier.on_time_rate_pct;
  const ratingScore      = (supplier.avg_rating / 5) * 100;
  const regionalScore    = 70; // no per-product context here — display as context info
  const composite        = reliabilityScore * 0.50 + ratingScore * 0.30 + regionalScore * 0.20;

  const borderColor = rank === 0 ? 'rgba(52,211,153,0.4)' : 'var(--border)';

  return (
    <div id={`supplier-card-${supplier.id}`}
      className="card flex flex-col gap-4 transition-all duration-200"
      style={{ borderColor }}>

      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl font-bold text-lg shrink-0"
            style={{ background: 'rgba(59,130,246,0.1)', color: '#60a5fa' }}>
            {supplier.name.charAt(0)}
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{supplier.name}</h3>
              {rank === 0 && <span className="badge-green text-[10px]">🏆 Top Supplier</span>}
            </div>
            <div className="flex items-center gap-2 mt-0.5 flex-wrap text-xs" style={{ color: 'var(--text-muted)' }}>
              <span className="flex items-center gap-1"><MapPin size={9} /> {supplier.region}</span>
              <span className="flex items-center gap-1"><Phone size={9} /> {supplier.whatsapp_number}</span>
            </div>
          </div>
        </div>

        {/* Composite score */}
        <div className="text-right shrink-0">
          <p className="text-2xl font-bold mono" style={{ color: reliabilityColor(composite) }}>
            {composite.toFixed(0)}
          </p>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>composite</p>
        </div>
      </div>

      {/* Category badges */}
      <div className="flex flex-wrap gap-1.5">
        {supplier.supply_categories.map(c => (
          <span key={c} className="badge-blue text-[10px]">Best for {c.trim()}</span>
        ))}
      </div>

      {/* Score breakdown */}
      <div className="rounded-lg px-3 py-3 flex flex-col gap-3"
        style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
        <p className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
          Score Breakdown
        </p>

        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs">
            <span style={{ color: 'var(--text-secondary)' }}>Reliability (×0.50)</span>
            <span className="mono font-semibold" style={{ color: reliabilityColor(reliabilityScore) }}>
              {reliabilityScore.toFixed(1)}
            </span>
          </div>
          <ReliabilityBar value={reliabilityScore} />

          <div className="flex items-center justify-between text-xs mt-1">
            <span style={{ color: 'var(--text-secondary)' }}>Rating (×0.30)</span>
            <StarRow value={supplier.avg_rating} />
          </div>
          <div className="w-full rounded-full overflow-hidden" style={{ height: 5, background: 'var(--border)' }}>
            <div className="h-full rounded-full" style={{ width: `${ratingScore}%`, background: '#fbbf24' }} />
          </div>

          <div className="flex items-center justify-between text-xs mt-1">
            <span style={{ color: 'var(--text-secondary)' }}>Regional (×0.20)</span>
            <span className="mono text-xs" style={{ color: 'var(--text-muted)' }}>
              {supplier.region} · {regionalScore}/100
            </span>
          </div>

          <div className="flex items-center justify-between text-xs mt-2 pt-2" style={{ borderTop: '1px solid var(--border)' }}>
            <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>Composite Score</span>
            <span className="mono font-bold" style={{ color: reliabilityColor(composite) }}>
              {composite.toFixed(1)} / 100
            </span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
        <div className="rounded-lg px-3 py-2 text-center"
          style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
          <p style={{ color: 'var(--text-muted)' }}>Deliveries (90d)</p>
          <p className="font-bold mono text-sm mt-0.5" style={{ color: 'var(--text-primary)' }}>
            {supplier.total_deliveries_90d}
          </p>
        </div>
        <div className="rounded-lg px-3 py-2 text-center"
          style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
          <p style={{ color: 'var(--text-muted)' }}>Contact</p>
          <p className="font-semibold mt-0.5 truncate" style={{ color: 'var(--text-primary)' }}>
            {supplier.contact_name}
          </p>
        </div>
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<SupplierSummary[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [search,    setSearch]    = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      // GET /api/suppliers → SupplierSummary[]
      const data = await apiGet<SupplierSummary[]>('/suppliers');
      setSuppliers(data);
    } catch { /* toast */ } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  // Sort by composite score: 50% reliability + 30% rating/5*100 + 20% regional(70)
  const ranked = [...suppliers]
    .filter(s => !search || s.name.toLowerCase().includes(search.toLowerCase()) || s.region.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      const score = (s: SupplierSummary) =>
        s.on_time_rate_pct * 0.50 + (s.avg_rating / 5) * 100 * 0.30 + 70 * 0.20;
      return score(b) - score(a);
    });

  return (
    <div className="page-enter flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Supplier Rankings</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            {suppliers.length} active suppliers · ranked by composite score (50% reliability + 30% rating + 20% regional)
          </p>
        </div>
        <button onClick={load} className="btn-ghost p-2"><RefreshCw size={13} /></button>
      </div>

      <div className="relative">
        <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
        <input className="input pl-9" placeholder="Search by name or region…"
          value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {loading
        ? <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">{[0,1,2,3].map(i => <div key={i} className="skeleton h-72 rounded-xl" />)}</div>
        : ranked.length === 0
          ? <div className="card py-12 flex flex-col items-center gap-2" style={{ borderStyle: 'dashed' }}>
              <Truck size={26} style={{ color: 'var(--text-muted)' }} />
              <p style={{ color: 'var(--text-muted)' }}>No suppliers found</p>
            </div>
          : <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              {ranked.map((s, i) => <SupplierScoreCard key={s.id} supplier={s} rank={i} />)}
            </div>
      }
    </div>
  );
}
