import React, { useState } from 'react';
import {
  FileText, RefreshCw, CheckCircle2, AlertTriangle,
  ShoppingCart, Lightbulb, ChevronDown, ChevronUp, Sparkles
} from 'lucide-react';
import type { Briefing, Order, InventoryItem } from '../../types';

// ── Helpers ───────────────────────────────────────────────────────────────────

const ALERT_COLORS: Record<string, { badge: string; dot: string }> = {
  out_of_stock: { badge: 'badge-red',   dot: 'dot-red'   },
  critical:     { badge: 'badge-red',   dot: 'dot-red'   },
  warning:      { badge: 'badge-amber', dot: 'dot-amber' },
  excess:       { badge: 'badge-gray',  dot: 'dot-gray'  },
  ok:           { badge: 'badge-green', dot: 'dot-green' },
};

// ── Sub-components ────────────────────────────────────────────────────────────

function BriefText({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const lines = text.split('\n').filter(Boolean);
  const preview = lines.slice(0, 6);
  const rest    = lines.slice(6);

  const renderLine = (line: string, i: number) => {
    if (line.startsWith('###')) {
      return (
        <p key={i} className="text-xs font-bold uppercase tracking-wider mt-3 mb-1" style={{ color: '#93c5fd' }}>
          {line.replace(/^#+\s*/, '')}
        </p>
      );
    }
    if (line.startsWith('##')) {
      return (
        <p key={i} className="text-sm font-bold mt-4 mb-1.5" style={{ color: 'var(--text-primary)' }}>
          {line.replace(/^#+\s*/, '')}
        </p>
      );
    }
    if (line.startsWith('#')) {
      return (
        <p key={i} className="text-base font-bold mt-2 mb-2" style={{ color: 'var(--text-primary)' }}>
          {line.replace(/^#+\s*/, '')}
        </p>
      );
    }
    if (line.startsWith('- ') || line.startsWith('* ')) {
      return (
        <p key={i} className="flex items-start gap-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
          <span className="mt-1.5 w-1 h-1 rounded-full shrink-0" style={{ background: '#3b82f6' }} />
          <span>{line.slice(2)}</span>
        </p>
      );
    }
    if (line.startsWith('**') && line.endsWith('**')) {
      return (
        <p key={i} className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>
          {line.replace(/\*\*/g, '')}
        </p>
      );
    }
    return (
      <p key={i} className="text-xs" style={{ color: 'var(--text-secondary)' }}>
        {line}
      </p>
    );
  };

  return (
    <div className="flex flex-col gap-1">
      {preview.map(renderLine)}
      {expanded && rest.map((line, i) => renderLine(line, i + 6))}
      {rest.length > 0 && (
        <button
          onClick={() => setExpanded((e) => !e)}
          className="flex items-center gap-1 text-xs mt-2 self-start"
          style={{ color: '#60a5fa' }}
        >
          {expanded
            ? <><ChevronUp size={12} /> Show less</>
            : <><ChevronDown size={12} /> Read full briefing ({rest.length} more lines)</>
          }
        </button>
      )}
    </div>
  );
}

function AlertsStrip({ alerts }: { alerts: InventoryItem[] }) {
  if (!alerts?.length) return null;
  const sorted = [...alerts].sort((a, b) => {
    const order: Record<string, number> = { out_of_stock: 0, critical: 1, warning: 2, excess: 3, ok: 4 };
    return (order[a.stock_status] ?? 5) - (order[b.stock_status] ?? 5);
  });

  function fmtDays(d: number | null | undefined): string {
    if (d == null || !isFinite(d) || d >= 999) return '∞';
    return `${d.toFixed(1)}d`;
  }

  return (
    <div>
      <p className="section-title flex items-center gap-1.5">
        <AlertTriangle size={11} /> Inventory Alerts ({alerts.length})
      </p>
      <div className="flex flex-col gap-1.5 max-h-40 overflow-y-auto scroll-panel">
        {sorted.map((item) => {
          const status = item.stock_status ?? 'ok';
          const colors = ALERT_COLORS[status] ?? ALERT_COLORS.ok;
          return (
            <div
              key={item.product_id}
              className="flex items-center justify-between text-xs px-3 py-2 rounded-lg"
              style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
            >
              <div className="flex items-center gap-2">
                <span className={colors.dot} />
                <span style={{ color: 'var(--text-primary)' }}>{item.name}</span>
                <span className="mono" style={{ color: 'var(--text-muted)' }}>{item.sku}</span>
              </div>
              <div className="flex items-center gap-2">
                <span style={{ color: 'var(--text-secondary)' }}>
                  {fmtDays(item.days_remaining)} remaining
                </span>
                <span className={colors.badge}>{status.replace('_', ' ')}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PendingOrdersStrip({ orders }: { orders: Order[] }) {
  if (!orders.length) return null;
  const pending = orders.filter((o) => o.status === 'pending_approval');
  if (!pending.length) return null;

  return (
    <div>
      <p className="section-title flex items-center gap-1.5">
        <ShoppingCart size={11} /> Pending Orders ({pending.length})
      </p>
      <div className="flex flex-col gap-1.5">
        {pending.slice(0, 4).map((o) => (
          <div
            key={o.id}
            className="flex items-center justify-between text-xs px-3 py-2 rounded-lg"
            style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
          >
            <div className="flex items-center gap-2">
              <span className="badge-amber text-[10px]">{o.order_cycle}</span>
              <span style={{ color: 'var(--text-primary)' }}>{o.product_name}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="mono" style={{ color: 'var(--text-secondary)' }}>
                {Math.round(o.final_qty)} {o.unit}s
              </span>
              <span className="mono font-semibold" style={{ color: '#6ee7b7' }}>
                ₹{o.total_cost.toLocaleString()}
              </span>
            </div>
          </div>
        ))}
        {pending.length > 4 && (
          <p className="text-xs text-center" style={{ color: 'var(--text-muted)' }}>
            +{pending.length - 4} more orders → go to Orders tab
          </p>
        )}
      </div>
    </div>
  );
}

// ── Stat Bar ──────────────────────────────────────────────────────────────────

function StatBar({ briefing }: { briefing: Briefing }) {
  const alerts  = briefing.inventory_alerts ?? [];
  const orders  = briefing.orders ?? [];
  const opps    = briefing.opportunities ?? [];
  const critical = alerts.filter((a) => a.stock_status === 'critical' || a.stock_status === 'out_of_stock').length;
  const pending  = orders.filter((o) => o.status === 'pending_approval').length;
  const totalCost = orders.reduce((s, o) => s + (o.total_cost || 0), 0);

  return (
    <div className="grid grid-cols-4 gap-3">
      {[
        { label: 'Critical Alerts', value: critical, color: critical > 0 ? '#f43f5e' : '#6ee7b7', badge: critical > 0 ? 'badge-red' : 'badge-green' },
        { label: 'Pending Orders',  value: pending,  color: '#fcd34d', badge: 'badge-amber' },
        { label: 'Order Value',     value: `₹${Math.round(totalCost).toLocaleString()}`, color: '#6ee7b7', badge: 'badge-green' },
        { label: 'Opportunities',   value: opps.length, color: '#c4b5fd', badge: 'badge-violet' },
      ].map(({ label, value, color, badge }) => (
        <div
          key={label}
          className="rounded-lg px-3 py-2.5 flex flex-col gap-0.5"
          style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
        >
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{label}</p>
          <p className="text-xl font-bold mono" style={{ color }}>{value}</p>
        </div>
      ))}
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

interface MorningBriefCardProps {
  briefing:  Briefing | null;
  loading:   boolean;
  onRefresh: () => void;
}

export default function MorningBriefCard({ briefing, loading, onRefresh }: MorningBriefCardProps) {
  if (loading) {
    return (
      <div className="card flex flex-col gap-4">
        <div className="skeleton h-5 w-48 rounded" />
        <div className="skeleton h-3 w-full rounded" />
        <div className="skeleton h-3 w-4/5 rounded" />
        <div className="skeleton h-3 w-3/4 rounded" />
        <div className="grid grid-cols-4 gap-3">
          {[0,1,2,3].map((i) => <div key={i} className="skeleton h-14 rounded-lg" />)}
        </div>
      </div>
    );
  }

  if (!briefing) {
    return (
      <div
        className="card flex flex-col items-center justify-center gap-3 py-10"
        style={{ borderStyle: 'dashed' }}
      >
        <div
          className="flex h-12 w-12 items-center justify-center rounded-xl"
          style={{ background: 'rgba(139,92,246,0.1)' }}
        >
          <Sparkles size={22} style={{ color: '#c4b5fd' }} />
        </div>
        <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
          No briefing for today
        </p>
        <p className="text-xs text-center max-w-xs" style={{ color: 'var(--text-muted)' }}>
          Click <strong>Run Briefing</strong> above to generate your AI morning report
        </p>
      </div>
    );
  }

  return (
    <div className="card flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-2">
          <div
            className="flex h-8 w-8 items-center justify-center rounded-lg shrink-0 mt-0.5"
            style={{ background: 'rgba(139,92,246,0.15)' }}
          >
            <FileText size={16} style={{ color: '#c4b5fd' }} />
          </div>
          <div>
            <h2 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
              Morning Brief
            </h2>
            <div className="flex items-center gap-1.5 mt-0.5">
              <CheckCircle2 size={11} style={{ color: '#10b981' }} />
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {new Date(briefing.date).toLocaleDateString('en-IN', {
                  weekday: 'long', day: 'numeric', month: 'long'
                })}
              </p>
            </div>
          </div>
        </div>
        <button
          id="btn-refresh-briefing"
          onClick={onRefresh}
          className="btn-ghost text-xs py-1.5"
          title="Re-fetch briefing"
        >
          <RefreshCw size={12} />
        </button>
      </div>

      {/* Stat bar */}
      <StatBar briefing={briefing} />

      {/* AI-generated text */}
      <div
        className="rounded-xl px-4 py-4"
        style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
      >
        <div className="flex items-center gap-1.5 mb-3">
          <Sparkles size={12} style={{ color: '#c4b5fd' }} />
          <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: '#c4b5fd' }}>
            Gemini Analysis
          </span>
        </div>
        <BriefText text={briefing.brief_text} />
      </div>

      {/* Inventory alerts */}
      <AlertsStrip alerts={briefing.inventory_alerts ?? []} />

      {/* Pending orders */}
      <PendingOrdersStrip orders={briefing.orders ?? []} />
    </div>
  );
}
