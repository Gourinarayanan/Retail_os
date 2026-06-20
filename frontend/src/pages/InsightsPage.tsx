import React, { useState, useEffect, useCallback } from 'react';
import { Lightbulb, Calendar, RefreshCw, IndianRupee, ArrowRight, Sparkles } from 'lucide-react';
import type { Opportunity } from '../types';
import { apiGet } from '../api/client';

function OpportunityCard({ opp, rank }: { opp: Opportunity; rank: number }) {
  const isTop = rank === 0;
  const isUrgent = opp.days_away <= 7;

  return (
    <div className={`glass-panel rounded-2xl p-5 md:p-6 transition-all duration-300 relative overflow-hidden border group hover:-translate-y-1 hover:shadow-lg flex flex-col gap-6 ${
      isTop ? 'border-violet-500/40 shadow-[0_0_15px_rgba(139,92,246,0.1)]' : 'border-border-glass'
    }`}>
      {isTop && <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/10 rounded-full blur-3xl pointer-events-none group-hover:scale-125 transition-transform duration-700" />}

      {/* Header */}
      <div className="flex items-start justify-between gap-4 relative z-10">
        <div className="flex items-start gap-4">
          <div className={`flex items-center justify-center w-12 h-12 rounded-xl shrink-0 border shadow-sm text-xl ${
            isTop ? 'bg-violet-500/10 border-violet-500/20' : 'bg-surface-container border-border-glass'
          }`}>
            🎉
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-headline-sm text-base font-bold text-on-surface">{opp.product_name}</h3>
              {isTop && (
                <span className="font-label-xs text-[9px] uppercase tracking-wider px-2 py-0.5 rounded bg-violet-500 text-white font-bold shadow-sm flex items-center gap-1">
                  🏆 Top Pick
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-label-xs text-[10px] px-2 py-1 rounded bg-surface-container-high border border-border-glass text-on-surface-variant uppercase tracking-wider font-bold">
                {opp.festival}
              </span>
              <span className={`flex items-center gap-1 text-[11px] font-medium ${isUrgent ? 'text-error' : 'text-primary'}`}>
                <Calendar className="w-3.5 h-3.5" />
                {opp.days_away}d away · {opp.duration_days}d event
              </span>
            </div>
          </div>
        </div>

        <div className="text-right shrink-0 bg-surface-container-low px-3 py-2 rounded-xl border border-border-glass">
          <div className="flex items-center gap-0.5 justify-end text-emerald-500">
            <IndianRupee className="w-4 h-4" />
            <span className="text-xl font-bold font-mono tracking-tight">{Math.round(opp.extra_profit_est).toLocaleString('en-IN')}</span>
          </div>
          <p className="font-label-xs text-[9px] uppercase tracking-wider text-on-surface-variant mt-0.5">Est. Extra Profit</p>
        </div>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 relative z-10">
        {[
          { label: 'Demand Uplift', value: `+${opp.demand_uplift_pct}%`, colorClass: 'text-amber-500' },
          { label: 'Extra Units', value: `${Math.round(opp.extra_units)}`, colorClass: 'text-on-surface' },
          { label: 'Extra Revenue', value: `₹${Math.round(opp.extra_revenue_est).toLocaleString('en-IN')}`, colorClass: 'text-primary' },
        ].map(({ label, value, colorClass }) => (
          <div key={label} className="rounded-xl p-3 bg-surface-container-low border border-border-glass text-center">
            <p className="font-label-xs text-[9px] uppercase tracking-wider text-on-surface-variant">{label}</p>
            <p className={`font-headline-sm font-bold font-mono mt-1 ${colorClass}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Multiplier bar */}
      <div className="flex items-center gap-4 relative z-10">
        <span className="font-mono text-xs font-bold text-violet-500 w-12 text-right shrink-0">×{opp.multiplier.toFixed(2)}</span>
        <div className="flex-1 h-1.5 rounded-full bg-surface-container-high border border-border-glass overflow-hidden">
          <div className="h-full rounded-full bg-violet-500" style={{ width: `${Math.min((opp.multiplier - 1) * 100, 100)}%` }} />
        </div>
      </div>

      {/* Narrative & Action */}
      <div className="mt-auto space-y-4 relative z-10">
        <div className="rounded-xl p-4 bg-violet-500/5 border border-violet-500/10 flex gap-3 text-sm text-on-surface-variant leading-relaxed">
          <Sparkles className="w-4 h-4 text-violet-500 shrink-0 mt-0.5" />
          <p>{opp.narrative}</p>
        </div>
        <button className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-surface-container hover:bg-violet-50 hover:text-violet-600 border border-border-glass hover:border-violet-200 text-on-surface font-bold text-xs uppercase tracking-wider transition-all">
          <span>{opp.action}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

export default function InsightsPage() {
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<{ opportunities: Opportunity[]; count: number }>('/profit-insights');
      setOpps(data.opportunities);
    } catch { } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const totalPotential = opps.reduce((s, o) => s + o.extra_profit_est, 0);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h1 className="font-headline-lg text-xl font-bold text-on-surface">Profit Insights</h1>
          <p className="font-body-md text-on-surface-variant mt-1">
            AI-identified festival opportunities · {opps.length} active alerts
          </p>
        </div>
        <button onClick={load} className="p-2 border border-border-glass rounded-lg text-on-surface-variant hover:text-primary hover:border-primary transition-all shrink-0">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {totalPotential > 0 && (
        <div className="glass-panel p-6 rounded-2xl border border-violet-500/30 bg-violet-500/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative overflow-hidden group">
          <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-48 h-48 bg-violet-500/10 rounded-full blur-3xl pointer-events-none group-hover:scale-150 transition-transform duration-1000" />
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-500 shrink-0">
              <Lightbulb className="w-6 h-6" />
            </div>
            <div>
              <h2 className="font-headline-sm font-bold text-violet-600">Total Festival Opportunity</h2>
              <p className="text-xs text-violet-500/80 font-medium mt-0.5">Estimated additional profit potential</p>
            </div>
          </div>
          <div className="flex items-center gap-1 text-violet-600 relative z-10 bg-white/50 px-4 py-2 rounded-xl border border-violet-500/20">
            <IndianRupee className="w-6 h-6" />
            <span className="font-headline-lg font-bold font-mono tracking-tight text-3xl">
              {Math.round(totalPotential).toLocaleString('en-IN')}
            </span>
          </div>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {[0,1,2,3].map(i => <div key={i} className="glass-panel h-80 rounded-2xl border border-border-glass animate-pulse" />)}
        </div>
      ) : opps.length === 0 ? (
        <div className="glass-panel py-16 flex flex-col items-center gap-4 rounded-2xl border border-border-glass border-dashed">
          <div className="w-16 h-16 rounded-2xl bg-surface-container flex items-center justify-center border border-border-glass">
            <Lightbulb className="w-8 h-8 text-on-surface-variant/40" />
          </div>
          <div className="text-center">
            <p className="text-sm font-bold text-on-surface">No opportunities above ₹500</p>
            <p className="text-xs text-on-surface-variant mt-1">Run the morning briefing when a festival is within 14 days.</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {opps.map((opp, i) => <OpportunityCard key={`${opp.product_id}-${opp.festival}`} opp={opp} rank={i} />)}
        </div>
      )}
    </div>
  );
}
