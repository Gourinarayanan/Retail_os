import React, { useState, useEffect, useCallback } from 'react';
import { Lightbulb, TrendingUp, Calendar, RefreshCw, IndianRupee, ArrowRight } from 'lucide-react';
import type { Opportunity } from '../types';
import { apiGet } from '../api/client';

// ── Opportunity Card ──────────────────────────────────────────────────────────

function OpportunityCard({ opp, rank }: { opp: Opportunity; rank: number }) {
  const urgencyColor = opp.days_away <= 3 ? '#f43f5e'
                     : opp.days_away <= 7 ? '#fbbf24'
                     : '#c4b5fd';

  return (
    <div
      className="card flex flex-col gap-4 transition-all duration-200 hover:scale-[1.01]"
      style={{
        borderColor: rank === 0 ? 'rgba(139,92,246,0.4)' : 'var(--border)',
        background: rank === 0 ? 'rgba(139,92,246,0.04)' : 'var(--bg-card)',
      }}
    >
      {/* Rank badge */}
      {rank === 0 && (
        <div className="flex items-center gap-1.5">
          <span className="badge-violet text-[10px]">🏆 Top Opportunity</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl text-xl shrink-0"
            style={{ background: 'rgba(139,92,246,0.1)' }}>
            🎉
          </div>
          <div>
            <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{opp.product_name}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className="badge-violet text-[10px]">{opp.festival}</span>
              <span className="flex items-center gap-1 text-xs" style={{ color: urgencyColor }}>
                <Calendar size={10} />
                {opp.days_away}d away · {opp.duration_days}-day event
              </span>
            </div>
          </div>
        </div>

        {/* Profit */}
        <div className="text-right shrink-0">
          <div className="flex items-center gap-0.5 justify-end">
            <IndianRupee size={14} style={{ color: '#34d399' }} />
            <span className="text-xl font-bold mono" style={{ color: '#34d399' }}>
              {Math.round(opp.extra_profit_est).toLocaleString('en-IN')}
            </span>
          </div>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>extra profit est.</p>
        </div>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: 'Demand Uplift',  value: `+${opp.demand_uplift_pct}%`,           color: '#fbbf24' },
          { label: 'Extra Units',    value: `${Math.round(opp.extra_units)} units`,  color: 'var(--text-primary)' },
          { label: 'Extra Revenue',  value: `₹${Math.round(opp.extra_revenue_est).toLocaleString('en-IN')}`, color: '#93c5fd' },
        ].map(({ label, value, color }) => (
          <div key={label} className="rounded-lg px-2.5 py-2 text-center"
            style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
            <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{label}</p>
            <p className="text-sm font-bold mono" style={{ color }}>{value}</p>
          </div>
        ))}
      </div>

      {/* Multiplier bar */}
      <div className="flex items-center gap-3">
        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>×{opp.multiplier.toFixed(2)}</span>
        <div className="flex-1 rounded-full overflow-hidden" style={{ height: 4, background: 'var(--border)' }}>
          <div className="h-full rounded-full" style={{ width: `${Math.min((opp.multiplier - 1) * 100, 100)}%`, background: '#8b5cf6' }} />
        </div>
      </div>

      {/* Gemini narrative */}
      <div className="rounded-lg px-3 py-2.5 text-xs leading-relaxed"
        style={{ background: 'rgba(139,92,246,0.06)', border: '1px solid rgba(139,92,246,0.15)', color: 'var(--text-secondary)', borderLeft: '2px solid rgba(139,92,246,0.4)' }}>
        ✨ {opp.narrative}
      </div>

      {/* Action */}
      <div className="flex items-center gap-2 text-xs font-semibold" style={{ color: '#c4b5fd' }}>
        <ArrowRight size={12} />
        {opp.action}
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function InsightsPage() {
  const [opps,    setOpps]    = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<{ opportunities: Opportunity[]; count: number }>('/profit-insights');
      setOpps(data.opportunities);
    } catch {/* toast */} finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const totalPotential = opps.reduce((s, o) => s + o.extra_profit_est, 0);

  return (
    <div className="page-enter flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Profit Insights</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Festival opportunities · {opps.length} found
            {totalPotential > 0 && ` · ₹${Math.round(totalPotential).toLocaleString('en-IN')} total potential`}
          </p>
        </div>
        <button onClick={load} className="btn-ghost p-2"><RefreshCw size={14} /></button>
      </div>

      {/* Total potential banner */}
      {totalPotential > 0 && (
        <div className="rounded-xl px-5 py-4 flex items-center justify-between"
          style={{ background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)' }}>
          <div className="flex items-center gap-2">
            <Lightbulb size={18} style={{ color: '#c4b5fd' }} />
            <span className="text-sm font-semibold" style={{ color: '#c4b5fd' }}>
              Total Festival Opportunity
            </span>
          </div>
          <div className="flex items-center gap-1">
            <IndianRupee size={20} style={{ color: '#c4b5fd' }} />
            <span className="text-2xl font-bold mono" style={{ color: '#c4b5fd' }}>
              {Math.round(totalPotential).toLocaleString('en-IN')}
            </span>
          </div>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-2 gap-4">{[0,1,2,3].map((i) => <div key={i} className="skeleton h-64 rounded-xl" />)}</div>
      ) : opps.length === 0 ? (
        <div className="card py-16 flex flex-col items-center gap-3" style={{ borderStyle: 'dashed' }}>
          <Lightbulb size={32} style={{ color: 'var(--text-muted)' }} />
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>No opportunities above ₹500</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            Run morning briefing when a festival is within 14 days
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {opps.map((opp, i) => <OpportunityCard key={`${opp.product_id}-${opp.festival}`} opp={opp} rank={i} />)}
        </div>
      )}
    </div>
  );
}
