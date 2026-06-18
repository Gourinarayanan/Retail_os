import React, { useState, useEffect, useCallback } from 'react';
import {
  Package, AlertTriangle, Search, Filter,
  RefreshCw, Thermometer, ChevronDown, ChevronUp,
  CalendarX, TrendingDown, TrendingUp, BoxIcon
} from 'lucide-react';
import type { InventoryItem, AlertLevel } from '../types';
import { apiGet, apiPatch } from '../api/client';
import toast from 'react-hot-toast';

// ── Helpers ───────────────────────────────────────────────────────────────────

const ALERT_META: Record<AlertLevel, { label: string; color: string; bg: string; border: string }> = {
  out_of_stock: { label: 'Out of Stock', color: '#f43f5e', bg: 'rgba(244,63,94,0.08)',   border: 'rgba(244,63,94,0.25)'   },
  critical:     { label: 'Critical',     color: '#f43f5e', bg: 'rgba(244,63,94,0.06)',   border: 'rgba(244,63,94,0.2)'    },
  warning:      { label: 'Warning',      color: '#fbbf24', bg: 'rgba(245,158,11,0.06)',  border: 'rgba(245,158,11,0.2)'   },
  excess:       { label: 'Excess',       color: '#94a3b8', bg: 'rgba(100,116,139,0.05)', border: 'rgba(100,116,139,0.15)' },
  ok:           { label: 'OK',           color: '#34d399', bg: 'rgba(16,185,129,0.05)',  border: 'rgba(16,185,129,0.15)'  },
};

function DaysBar({ days, max = 21 }: { days: number; max?: number }) {
  const pct = Math.min((days / max) * 100, 100);
  const color = days === 0 ? '#f43f5e'
              : days < 2   ? '#f43f5e'
              : days < 7   ? '#fbbf24'
              : days > 21  ? '#94a3b8'
              : '#34d399';
  return (
    <div className="w-full rounded-full overflow-hidden" style={{ height: 4, background: 'var(--border)' }}>
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{ width: `${pct}%`, background: color }}
      />
    </div>
  );
}

// ── Inventory Row ─────────────────────────────────────────────────────────────

function InventoryRow({ item, onAdjusted }: { item: InventoryItem; onAdjusted: (updated: InventoryItem) => void }) {
  const [expanded, setExpanded] = useState(false);
  const [editBatch, setEditBatch] = useState<{ id: number; qty: number } | null>(null);
  const [saving, setSaving] = useState(false);

  const meta = ALERT_META[item.stock_status];

  const handleAdjust = async () => {
    if (!editBatch) return;
    setSaving(true);
    try {
      await apiPatch(`/inventory/${editBatch.id}/quantity`, { quantity: editBatch.qty });
      toast.success(`Stock adjusted for ${item.name}.`);
      const fresh = await apiGet<InventoryItem>(`/inventory/${item.product_id}`);
      onAdjusted(fresh);
      setEditBatch(null);
    } catch {/* toast by interceptor */} finally { setSaving(false); }
  };

  return (
    <div
      className="rounded-xl overflow-hidden transition-all duration-200"
      style={{ border: `1px solid ${expanded ? meta.border : 'var(--border)'}`, background: 'var(--bg-card)' }}
    >
      {/* ── Main row ─────────────────────────────────────────── */}
      <div
        className="grid items-center gap-3 px-4 py-3 cursor-pointer"
        style={{ gridTemplateColumns: '1fr 90px 110px 120px 100px 80px 36px' }}
        onClick={() => setExpanded((e) => !e)}
      >
        {/* Name + SKU */}
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{item.name}</span>
            {item.expiry_alerts.length > 0 && (
              <span className="badge-red text-[10px]">⚠ Expiry</span>
            )}
          </div>
          <span className="mono text-[11px]" style={{ color: 'var(--text-muted)' }}>{item.sku} · {item.category}</span>
        </div>

        {/* Stock */}
        <div className="text-right">
          <p className="font-bold mono text-sm" style={{ color: meta.color }}>
            {Math.round(item.current_stock)}
          </p>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{item.unit}s</p>
        </div>

        {/* Days bar */}
        <div className="flex flex-col gap-1">
          <DaysBar days={item.days_remaining} />
          <span className="text-[11px] mono" style={{ color: meta.color }}>
            {item.days_remaining.toFixed(1)}d left
          </span>
        </div>

        {/* Daily demand */}
        <div className="text-right">
          <p className="text-sm font-medium mono" style={{ color: 'var(--text-secondary)' }}>
            {item.avg_daily_demand}/day
          </p>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>avg demand</p>
        </div>

        {/* Reorder point */}
        <div className="text-right">
          <p className="text-xs mono" style={{ color: 'var(--text-muted)' }}>
            RP: {item.reorder_point_days}d
          </p>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
            LT: {item.lead_time_days}d
          </p>
        </div>

        {/* Status badge */}
        <div>
          <span
            className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
            style={{ background: meta.bg, color: meta.color, border: `1px solid ${meta.border}` }}
          >
            {meta.label}
          </span>
        </div>

        {/* Expand toggle */}
        <div style={{ color: 'var(--text-muted)' }}>
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </div>

      {/* ── Expanded: batches + adjust ────────────────────────── */}
      {expanded && (
        <div
          className="px-4 pb-4 flex flex-col gap-3"
          style={{ borderTop: '1px solid var(--border)' }}
        >
          {/* Expiry alerts */}
          {item.expiry_alerts.length > 0 && (
            <div className="flex flex-col gap-1.5 pt-3">
              <p className="section-title flex items-center gap-1"><CalendarX size={11} /> Expiry Alerts</p>
              {item.expiry_alerts.map((ea) => (
                <div
                  key={ea.batch_number}
                  className="flex items-center justify-between text-xs px-3 py-2 rounded-lg"
                  style={{ background: 'rgba(244,63,94,0.06)', border: '1px solid rgba(244,63,94,0.2)' }}
                >
                  <span style={{ color: '#fca5a5' }}>Batch {ea.batch_number}</span>
                  <span style={{ color: 'var(--text-secondary)' }}>{Math.round(ea.quantity)} units</span>
                  <span className="badge-red text-[10px]">
                    {ea.days_to_expiry <= 0 ? 'EXPIRED' : `${ea.days_to_expiry}d to expiry`}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Batch list */}
          <div className="pt-2">
            <p className="section-title flex items-center gap-1"><BoxIcon size={11} /> Inventory Batches</p>
            <div className="flex flex-col gap-1.5">
              {item.batches.filter((b) => b.status !== 'depleted').map((b) => (
                <div
                  key={b.id}
                  className="flex items-center justify-between text-xs px-3 py-2 rounded-lg"
                  style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
                >
                  <span className="mono" style={{ color: 'var(--text-muted)' }}>#{b.batch_number}</span>
                  {editBatch?.id === b.id ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        className="input w-24 py-1 text-xs"
                        value={editBatch.qty}
                        onChange={(e) => setEditBatch({ id: b.id, qty: parseFloat(e.target.value) || 0 })}
                      />
                      <button onClick={handleAdjust} disabled={saving} className="btn-success text-xs py-1 px-2">
                        {saving ? 'Saving…' : 'Save'}
                      </button>
                      <button onClick={() => setEditBatch(null)} className="btn-ghost text-xs py-1 px-2">Cancel</button>
                    </div>
                  ) : (
                    <>
                      <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {Math.round(b.quantity)} {item.unit}s
                      </span>
                      <span style={{ color: 'var(--text-muted)' }}>
                        {b.expiry_date ? `Exp: ${b.expiry_date}` : 'No expiry'}
                      </span>
                      <button
                        onClick={(e) => { e.stopPropagation(); setEditBatch({ id: b.id, qty: b.quantity }); }}
                        className="text-[11px]" style={{ color: '#60a5fa' }}
                      >
                        Adjust
                      </button>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function InventoryPage() {
  const [items,      setItems]      = useState<InventoryItem[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [search,     setSearch]     = useState('');
  const [alertFilter,setAlertFilter]= useState<AlertLevel | 'all'>('all');
  const [alertsOnly, setAlertsOnly] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<InventoryItem[]>(alertsOnly ? '/inventory/alerts' : '/inventory');
      setItems(data);
    } catch {/* toast */} finally { setLoading(false); }
  }, [alertsOnly]);

  useEffect(() => { load(); }, [load]);

  const handleAdjusted = useCallback((updated: InventoryItem) => {
    setItems((prev) => prev.map((i) => i.product_id === updated.product_id ? updated : i));
  }, []);

  const filtered = items.filter((i) => {
    const matchSearch = !search || i.name.toLowerCase().includes(search.toLowerCase()) || i.sku.toLowerCase().includes(search.toLowerCase());
    const matchAlert  = alertFilter === 'all' || i.stock_status === alertFilter;
    return matchSearch && matchAlert;
  });

  const counts = {
    out_of_stock: items.filter((i) => i.stock_status === 'out_of_stock').length,
    critical:     items.filter((i) => i.stock_status === 'critical').length,
    warning:      items.filter((i) => i.stock_status === 'warning').length,
    ok:           items.filter((i) => i.stock_status === 'ok').length,
    excess:       items.filter((i) => i.stock_status === 'excess').length,
  };

  return (
    <div className="page-enter flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Inventory Intelligence</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            {items.length} products · {counts.out_of_stock + counts.critical} urgent alerts
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setAlertsOnly((a) => !a)} className={alertsOnly ? 'btn-primary' : 'btn-ghost'}>
            <AlertTriangle size={13} /> {alertsOnly ? 'Showing Alerts Only' : 'Alerts Only'}
          </button>
          <button onClick={load} className="btn-ghost p-2"><RefreshCw size={14} /></button>
        </div>
      </div>

      {/* Status pills */}
      <div className="flex flex-wrap gap-2">
        {(Object.entries(ALERT_META) as [AlertLevel, typeof ALERT_META[AlertLevel]][]).map(([level, meta]) => (
          <button
            key={level}
            onClick={() => setAlertFilter(alertFilter === level ? 'all' : level)}
            className="flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium transition-all"
            style={{
              background: alertFilter === level ? meta.bg : 'var(--bg-card)',
              border:     alertFilter === level ? `1px solid ${meta.border}` : '1px solid var(--border)',
              color:      alertFilter === level ? meta.color : 'var(--text-secondary)',
            }}
          >
            <span className="font-bold text-sm mono">{counts[level]}</span> {meta.label}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
        <input
          type="text"
          className="input pl-9"
          placeholder="Search by name or SKU…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Table header */}
      <div
        className="grid text-[10px] font-semibold uppercase tracking-wider px-4 py-2 rounded-lg"
        style={{ gridTemplateColumns: '1fr 90px 110px 120px 100px 80px 36px', color: 'var(--text-muted)', background: 'var(--bg-card)', border: '1px solid var(--border)' }}
      >
        <span>Product</span><span className="text-right">Stock</span><span>Days Left</span>
        <span className="text-right">Avg Demand</span><span className="text-right">Reorder</span>
        <span>Status</span><span />
      </div>

      {/* Rows */}
      {loading ? (
        <div className="flex flex-col gap-2">{[0,1,2,3,4].map((i) => <div key={i} className="skeleton h-14 rounded-xl" />)}</div>
      ) : filtered.length === 0 ? (
        <div className="card py-12 flex flex-col items-center gap-2" style={{ borderStyle: 'dashed' }}>
          <Package size={28} style={{ color: 'var(--text-muted)' }} />
          <p style={{ color: 'var(--text-muted)' }}>No products found</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {filtered.map((item) => (
            <InventoryRow key={item.product_id} item={item} onAdjusted={handleAdjusted} />
          ))}
        </div>
      )}
    </div>
  );
}
