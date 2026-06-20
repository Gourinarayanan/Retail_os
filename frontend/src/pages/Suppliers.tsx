import React, { useState, useEffect, useCallback } from 'react';
import { Search, RefreshCw, Truck, Star, MapPin, Phone, ShieldCheck } from 'lucide-react';
import { apiGet } from '../api/client';

interface SupplierSummary {
  id:                   number;
  name:                 string;
  contact_name:         string;
  whatsapp_number:      string;
  email:                string | null;
  region:               string;
  supply_categories:    string[];
  notes:                string | null;
  is_active:            boolean;
  on_time_rate_pct:     number;
  avg_rating:           number;
  total_deliveries_90d: number;
}

function reliabilityColorClass(pct: number) {
  return pct >= 90 ? 'text-emerald-500' : pct >= 75 ? 'text-amber-500' : 'text-error';
}
function reliabilityBgClass(pct: number) {
  return pct >= 90 ? 'bg-emerald-500' : pct >= 75 ? 'bg-amber-500' : 'bg-error';
}

function ReliabilityBar({ value }: { value: number }) {
  const bg = reliabilityBgClass(value);
  const text = reliabilityColorClass(value);
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 rounded-full overflow-hidden bg-surface-container-high border border-border-glass">
        <div className={`h-full rounded-full transition-all duration-700 ${bg}`} style={{ width: `${value}%` }} />
      </div>
      <span className={`font-mono text-xs font-bold w-10 text-right ${text}`}>{value.toFixed(0)}%</span>
    </div>
  );
}

function StarRow({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1,2,3,4,5].map(n => (
        <Star key={n} className={`w-3 h-3 ${n <= Math.round(value) ? 'fill-amber-400 text-amber-400' : 'text-surface-container-highest'}`} />
      ))}
      <span className="font-mono text-[11px] ml-1.5 text-on-surface-variant font-medium">{value.toFixed(1)}</span>
    </div>
  );
}

function SupplierScoreCard({ supplier, rank }: { supplier: SupplierSummary; rank: number }) {
  const reliabilityScore = supplier.on_time_rate_pct;
  const ratingScore      = (supplier.avg_rating / 5) * 100;
  const regionalScore    = 70;
  const composite        = reliabilityScore * 0.50 + ratingScore * 0.30 + regionalScore * 0.20;

  const isTop = rank === 0;

  return (
    <div
      id={`supplier-card-${supplier.id}`}
      className={`glass-panel rounded-2xl p-5 md:p-6 transition-all duration-300 relative overflow-hidden border group hover:-translate-y-1 hover:shadow-lg ${
        isTop ? 'border-primary/40' : 'border-border-glass'
      }`}
    >
      {isTop && (
        <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl pointer-events-none group-hover:scale-125 transition-transform duration-700" />
      )}

      {/* Header */}
      <div className="flex items-start justify-between gap-4 relative z-10">
        <div className="flex items-start gap-4">
          <div className={`flex items-center justify-center w-12 h-12 rounded-xl shrink-0 border ${
            isTop ? 'bg-primary/10 border-primary/20 text-primary shadow-sm' : 'bg-surface-container border-border-glass text-on-surface-variant'
          }`}>
            <span className="text-xl font-bold font-headline-lg">{supplier.name.charAt(0)}</span>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-headline-sm text-base font-bold text-on-surface">{supplier.name}</h3>
              {isTop && (
                <span className="font-label-xs text-[9px] uppercase tracking-wider px-2 py-0.5 rounded bg-primary text-on-primary font-bold shadow-sm flex items-center gap-1">
                  🏆 Top Ranked
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 flex-wrap pt-0.5">
              <span className="flex items-center gap-1 text-[11px] text-on-surface-variant font-medium"><MapPin className="w-3 h-3 text-primary/60" /> {supplier.region}</span>
              <span className="flex items-center gap-1 text-[11px] text-on-surface-variant font-medium"><Phone className="w-3 h-3 text-primary/60" /> {supplier.whatsapp_number}</span>
            </div>
          </div>
        </div>
        <div className="text-right shrink-0 bg-surface-container-low px-3 py-2 rounded-xl border border-border-glass">
          <p className={`text-2xl font-bold font-mono tracking-tight ${reliabilityColorClass(composite)}`}>
            {composite.toFixed(0)}
          </p>
          <p className="font-label-xs text-[9px] uppercase tracking-wider text-on-surface-variant mt-0.5">Composite</p>
        </div>
      </div>

      {/* Category badges */}
      <div className="flex flex-wrap gap-2 mt-5 relative z-10">
        {supplier.supply_categories.map(c => (
          <span key={c} className="font-label-xs text-[10px] px-2 py-1 rounded bg-surface-container-high border border-border-glass text-on-surface-variant uppercase tracking-wider font-bold">
            Best for {c.trim()}
          </span>
        ))}
      </div>

      {/* Score breakdown */}
      <div className="mt-5 rounded-xl p-4 bg-surface-container-lowest border border-border-glass space-y-4 relative z-10">
        <p className="font-label-xs text-[10px] uppercase tracking-wider text-on-surface-variant font-bold border-b border-border-glass/60 pb-2">
          Model Score Breakdown
        </p>

        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-on-surface-variant/80 font-medium">Reliability <span className="text-on-surface-variant/40">(×0.50)</span></span>
              <span className={`font-mono font-bold ${reliabilityColorClass(reliabilityScore)}`}>{reliabilityScore.toFixed(1)}</span>
            </div>
            <ReliabilityBar value={reliabilityScore} />
          </div>

          <div>
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-on-surface-variant/80 font-medium">Rating <span className="text-on-surface-variant/40">(×0.30)</span></span>
              <StarRow value={supplier.avg_rating} />
            </div>
            <div className="flex-1 h-1.5 rounded-full overflow-hidden bg-surface-container-high border border-border-glass">
              <div className="h-full rounded-full bg-amber-400" style={{ width: `${ratingScore}%` }} />
            </div>
          </div>

          <div className="flex items-center justify-between text-xs">
            <span className="text-on-surface-variant/80 font-medium">Regional <span className="text-on-surface-variant/40">(×0.20)</span></span>
            <span className="font-mono text-xs text-on-surface-variant bg-surface-container-high px-1.5 py-0.5 rounded">{supplier.region} · {regionalScore}/100</span>
          </div>
        </div>

        <div className="pt-3 border-t border-border-glass/60 flex items-center justify-between">
          <span className="font-headline-sm text-sm font-bold text-on-surface">Final Composite</span>
          <span className={`font-mono text-lg font-bold tracking-tight ${reliabilityColorClass(composite)}`}>
            {composite.toFixed(1)} <span className="text-xs text-on-surface-variant/60">/ 100</span>
          </span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4 relative z-10">
        <div className="rounded-xl p-3 bg-surface-container-low border border-border-glass text-center">
          <p className="font-label-xs text-[10px] uppercase tracking-wider text-on-surface-variant">Deliveries (90d)</p>
          <p className="font-headline-lg font-bold font-mono text-primary mt-1">{supplier.total_deliveries_90d}</p>
        </div>
        <div className="rounded-xl p-3 bg-surface-container-low border border-border-glass text-center">
          <p className="font-label-xs text-[10px] uppercase tracking-wider text-on-surface-variant">Contact Person</p>
          <p className="font-body-md font-bold text-on-surface mt-1.5 truncate">{supplier.contact_name}</p>
        </div>
      </div>
    </div>
  );
}

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<SupplierSummary[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [search,    setSearch]    = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<SupplierSummary[]>('/suppliers');
      setSuppliers(data);
    } catch { } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const ranked = [...suppliers]
    .filter(s => !search || s.name.toLowerCase().includes(search.toLowerCase()) || s.region.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      const score = (s: SupplierSummary) => s.on_time_rate_pct * 0.50 + (s.avg_rating / 5) * 100 * 0.30 + 70 * 0.20;
      return score(b) - score(a);
    });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h3 className="font-headline-lg text-on-surface">Supplier Intelligence</h3>
          <p className="font-body-md text-on-surface-variant mt-1">
            {suppliers.length} active suppliers · ranked by composite score (reliability, rating, region)
          </p>
        </div>
        <button onClick={load} className="p-2 border border-border-glass rounded-lg text-on-surface-variant hover:text-primary hover:border-primary transition-all shrink-0">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="relative max-w-xl">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant" />
        <input
          className="nexus-input w-full pl-10 pr-4 py-2.5 rounded-lg text-sm"
          placeholder="Search by name or region…"
          value={search} onChange={e => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {[0,1,2,3].map(i => <div key={i} className="glass-panel h-96 rounded-2xl border border-border-glass animate-pulse" />)}
        </div>
      ) : ranked.length === 0 ? (
        <div className="glass-panel py-16 flex flex-col items-center gap-4 rounded-2xl border border-border-glass border-dashed">
          <div className="w-16 h-16 rounded-2xl bg-surface-container flex items-center justify-center border border-border-glass">
            <Truck className="w-8 h-8 text-on-surface-variant/40" />
          </div>
          <p className="text-sm font-bold text-on-surface">No suppliers found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {ranked.map((s, i) => <SupplierScoreCard key={s.id} supplier={s} rank={i} />)}
        </div>
      )}
    </div>
  );
}
