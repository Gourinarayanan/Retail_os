import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles, ArrowRight, ShoppingCart, CalendarRange,
  RefreshCw, AlertTriangle, FileText, CheckCircle2,
  ChevronDown, ChevronUp,
} from 'lucide-react';
import type { Briefing, Order, InventoryItem } from '../../types';

// ── Helpers ────────────────────────────────────────────────────────────────────

function BriefText({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const lines = text.split('\n').filter(Boolean);
  const preview = lines.slice(0, 5);
  const rest = lines.slice(5);

  const renderLine = (line: string, i: number) => {
    if (line.startsWith('##')) return (
      <p key={i} className="text-sm font-bold text-white mt-3 mb-1">{line.replace(/^#+\s*/, '')}</p>
    );
    if (line.startsWith('- ') || line.startsWith('* ')) return (
      <p key={i} className="flex items-start gap-2 text-xs text-indigo-100">
        <span className="mt-1.5 w-1 h-1 rounded-full shrink-0 bg-indigo-300" />
        <span>{line.slice(2)}</span>
      </p>
    );
    return <p key={i} className="text-xs text-indigo-100 leading-relaxed">{line}</p>;
  };

  return (
    <div className="flex flex-col gap-1">
      {preview.map(renderLine)}
      {expanded && rest.map((line, i) => renderLine(line, i + 5))}
      {rest.length > 0 && (
        <button
          onClick={() => setExpanded(e => !e)}
          className="flex items-center gap-1 text-xs mt-1 self-start text-indigo-200 hover:text-white transition-colors"
        >
          {expanded ? <><ChevronUp size={12} /> Show less</> : <><ChevronDown size={12} /> Read more ({rest.length} lines)</>}
        </button>
      )}
    </div>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────────

interface MorningBriefCardProps {
  briefing:  Briefing | null;
  loading:   boolean;
  onRefresh: () => void;
}

export default function MorningBriefCard({ briefing, loading, onRefresh }: MorningBriefCardProps) {
  const navigate = useNavigate();

  const alerts = briefing?.inventory_alerts ?? [];
  const orders = briefing?.orders ?? [];
  const outOfStock = alerts.filter(a => a.stock_status === 'out_of_stock').length;
  const criticalCount = alerts.filter(a => a.stock_status === 'critical' || a.stock_status === 'out_of_stock').length;
  const nearExpiry = alerts.filter(a => a.days_remaining != null && a.days_remaining <= 7).length;
  const pendingOrders = orders.filter(o => o.status === 'pending_approval').length;

  if (loading) {
    return (
      <div className="bg-indigo-600 rounded-2xl p-6 border border-indigo-700 animate-pulse">
        <div className="h-4 bg-indigo-500 rounded w-32 mb-3" />
        <div className="h-6 bg-indigo-500 rounded w-64 mb-2" />
        <div className="h-3 bg-indigo-500 rounded w-full mb-1" />
        <div className="h-3 bg-indigo-500 rounded w-4/5" />
      </div>
    );
  }

  return (
    <div className="bg-indigo-600 rounded-2xl p-6 text-white shadow-md border border-indigo-700 relative overflow-hidden">
      {/* Decorative glow */}
      <div className="absolute -left-20 -top-20 w-64 h-64 bg-indigo-500 rounded-full blur-3xl opacity-40 select-none pointer-events-none" />

      <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        <div className="space-y-3.5 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="p-1 px-2 rounded bg-indigo-500 text-indigo-100 border border-indigo-400/40 text-[10px] font-bold tracking-widest uppercase">
              Daily Pulse
            </span>
            <span className="text-indigo-200 text-xs font-medium">
              {new Date().toLocaleDateString('en-IN', { weekday: 'long' })} Dashboard Brief
            </span>
          </div>

          <h2 className="text-2xl font-light italic tracking-tight text-white leading-tight">
            Good Morning, Operations.
          </h2>

          {briefing ? (
            <BriefText text={briefing.brief_text} />
          ) : (
            <p className="text-indigo-100 text-sm leading-relaxed">
              Supply networks active. Run the AI briefing pipeline to generate today's analysis and purchase recommendations.
            </p>
          )}

          {/* Tag pills */}
          <div className="flex flex-wrap gap-2.5 pt-2">
            {outOfStock > 0 && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/20 border border-red-400/30 text-[11px] font-semibold text-red-200">
                <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
                {outOfStock} Out of Stock
              </span>
            )}
            {nearExpiry > 0 && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-400/30 text-[11px] font-semibold text-amber-200">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                {nearExpiry} Near Expiry
              </span>
            )}
            {pendingOrders > 0 && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-400/20 border border-indigo-300/30 text-[11px] font-semibold text-indigo-100">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-300" />
                {pendingOrders} Pending Orders
              </span>
            )}
            {criticalCount > 0 && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500/20 border border-orange-400/30 text-[11px] font-semibold text-orange-200">
                <AlertTriangle size={11} />
                {criticalCount} Critical Alerts
              </span>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="w-full lg:w-auto flex flex-col sm:flex-row lg:flex-col gap-3 min-w-[220px]">
          <button
            id="btn-goto-recommendations"
            onClick={() => navigate('/orders')}
            className="flex-1 flex items-center justify-between gap-3 bg-white hover:bg-slate-50 text-indigo-700 py-2.5 px-4 rounded-xl font-bold text-xs tracking-wider uppercase transition-all duration-200 shadow-sm cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <ShoppingCart className="w-4 h-4 text-indigo-600" />
              <span>Restock Terminal</span>
            </div>
            <ArrowRight className="w-4 h-4 text-indigo-600" />
          </button>

          <button
            id="btn-refresh-briefing"
            onClick={onRefresh}
            className="flex-1 flex items-center justify-between gap-3 bg-indigo-500 text-white hover:bg-indigo-400 border border-indigo-400/40 py-2.5 px-4 rounded-xl font-bold text-xs tracking-wider uppercase transition-all duration-200 cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-indigo-200" />
              <span>Refresh Brief</span>
            </div>
            <ArrowRight className="w-4 h-4 text-indigo-200" />
          </button>
        </div>
      </div>
    </div>
  );
}
