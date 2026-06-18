import React, { useState, useEffect, useCallback } from 'react';
import { Package, AlertTriangle, Search, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';
import { apiGet, apiPatch } from '../api/client';
import toast from 'react-hot-toast';

// ── Exact backend response shapes (from inventory.py _product_stock_status) ──

interface ExpiryAlert {
  batch_number:   string;
  days_to_expiry: number;
  quantity:       number;
  severity:       'expired' | 'critical_expiry' | 'expiring_soon';
}

interface InventoryBatch {
  id:               number;
  batch_number:     string;
  quantity:         number;
  unit:             string;
  purchase_price:   number | null;
  expiry_date:      string | null;
  days_to_expiry:   number | null;
  status:           string;
  created_at:       string;
}

interface InventoryRow {
  product_id:         number;
  name:               string;
  sku:                string;
  category:           string;
  brand:              string | null;
  unit:               string;
  selling_price:      number;
  cost_price:         number;
  avg_daily_demand:   number;
  reorder_point_days: number;
  lead_time_days:     number;
  current_stock:      number;
  days_remaining:     number;
  stock_status:       'out_of_stock' | 'critical' | 'warning' | 'excess' | 'ok';
  expiry_alerts:      ExpiryAlert[];
  batches:            InventoryBatch[];
}

// ── Badge config ──────────────────────────────────────────────────────────────

const STATUS: Record<InventoryRow['stock_status'], { label: string; color: string; bg: string; border: string }> = {
  out_of_stock: { label: 'Out of Stock', color: '#f43f5e', bg: 'rgba(244,63,94,0.1)',  border: 'rgba(244,63,94,0.3)'  },
  critical:     { label: 'Critical',     color: '#f43f5e', bg: 'rgba(244,63,94,0.07)', border: 'rgba(244,63,94,0.2)'  },
  warning:      { label: 'Warning',      color: '#f59e0b', bg: 'rgba(245,158,11,0.08)',border: 'rgba(245,158,11,0.25)' },
  excess:       { label: 'Excess',       color: '#60a5fa', bg: 'rgba(59,130,246,0.08)',border: 'rgba(59,130,246,0.2)'  },
  ok:           { label: 'OK',           color: '#34d399', bg: 'rgba(52,211,153,0.07)',border: 'rgba(52,211,153,0.2)'  },
};

// ── Expandable row ────────────────────────────────────────────────────────────

function Row({ item }: { item: InventoryRow }) {
  const [open,   setOpen]   = useState(false);
  const [qty,    setQty]    = useState<{ batchId: number; val: number } | null>(null);
  const [saving, setSaving] = useState(false);
  const s = STATUS[item.stock_status];

  const nearestExpiry = item.batches
    .filter(b => b.expiry_date !== null)
    .sort((a, b) => (a.days_to_expiry ?? 999) - (b.days_to_expiry ?? 999))[0] ?? null;

  const saveQty = async () => {
    if (!qty) return;
    setSaving(true);
    try {
      // PATCH /api/inventory/{batch_id}/quantity  { quantity: float }
      await apiPatch(`/inventory/${qty.batchId}/quantity`, { quantity: qty.val });
      toast.success('Stock updated');
      setQty(null);
    } catch { /* toast by interceptor */ } finally { setSaving(false); }
  };

  return (
    <div className="rounded-xl overflow-hidden" style={{ border: '1px solid var(--border)', background: 'var(--bg-card)' }}>
      {/* Main row */}
      <div
        className="grid items-center gap-3 px-4 py-3 cursor-pointer select-none"
        style={{ gridTemplateColumns: '90px 1fr 90px 100px 110px 90px 28px' }}
        onClick={() => setOpen(v => !v)}
      >
        <span className="mono text-[11px]" style={{ color: 'var(--text-muted)' }}>{item.sku}</span>
        <div>
          <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{item.name}</p>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{item.category}{item.brand ? ` · ${item.brand}` : ''}</p>
        </div>
        <div className="text-right">
          <p className="font-bold mono text-sm" style={{ color: s.color }}>{Math.round(item.current_stock)}</p>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{item.unit}s</p>
        </div>
        <div className="text-right">
          <p className="mono text-sm" style={{ color: item.days_remaining < 3 ? '#f43f5e' : 'var(--text-secondary)' }}>
            {item.days_remaining >= 999 ? '∞' : `${item.days_remaining}d`}
          </p>
          <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>remaining</p>
        </div>
        <div className="text-right text-xs" style={{ color: 'var(--text-muted)' }}>
          {nearestExpiry?.expiry_date
            ? <span style={{ color: (nearestExpiry.days_to_expiry ?? 999) <= 5 ? '#f43f5e' : 'var(--text-muted)' }}>
                {nearestExpiry.expiry_date}
              </span>
            : '—'}
        </div>
        <span
          className="text-[10px] font-semibold px-2 py-0.5 rounded-full text-center"
          style={{ background: s.bg, color: s.color, border: `1px solid ${s.border}` }}
        >
          {s.label}
        </span>
        <span style={{ color: 'var(--text-muted)' }}>{open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}</span>
      </div>

      {/* Expanded: batches */}
      {open && (
        <div className="px-4 pb-4 flex flex-col gap-2" style={{ borderTop: '1px solid var(--border)' }}>
          <p className="text-[10px] font-semibold uppercase tracking-wider pt-3" style={{ color: 'var(--text-muted)' }}>Batches</p>
          {item.batches.filter(b => b.status !== 'depleted').map(b => (
            <div key={b.id} className="flex items-center justify-between text-xs px-3 py-2 rounded-lg gap-4"
              style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
              <span className="mono" style={{ color: 'var(--text-muted)' }}>#{b.batch_number}</span>
              {qty?.batchId === b.id ? (
                <div className="flex items-center gap-2">
                  <input type="number" className="input w-24 py-1 text-xs" value={qty.val} min={0} step={0.1}
                    onChange={e => setQty({ batchId: b.id, val: parseFloat(e.target.value) || 0 })} />
                  <button onClick={saveQty} disabled={saving} className="btn-success text-xs py-1 px-2">
                    {saving ? 'Saving…' : 'Save'}
                  </button>
                  <button onClick={() => setQty(null)} className="btn-ghost text-xs py-1 px-2">Cancel</button>
                </div>
              ) : (
                <>
                  <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {Math.round(b.quantity)} {b.unit}s
                  </span>
                  <span style={{ color: (b.days_to_expiry ?? 999) <= 5 ? '#f43f5e' : 'var(--text-muted)' }}>
                    {b.expiry_date ? `Exp: ${b.expiry_date}` : 'No expiry'}
                    {b.days_to_expiry !== null && b.days_to_expiry <= 10 && ` (${b.days_to_expiry}d)`}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded" style={{
                    background: b.status === 'active' ? 'rgba(52,211,153,0.08)' : 'rgba(245,158,11,0.08)',
                    color: b.status === 'active' ? '#34d399' : '#f59e0b',
                  }}>{b.status}</span>
                  <button onClick={() => setQty({ batchId: b.id, val: b.quantity })}
                    className="text-[11px]" style={{ color: '#60a5fa' }}>Adjust</button>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function InventoryPage() {
  const [items,      setItems]      = useState<InventoryRow[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [search,     setSearch]     = useState('');
  const [statusFilter, setStatusFilter] = useState<InventoryRow['stock_status'] | 'all'>('all');
  const [alertsOnly, setAlertsOnly] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      // GET /api/inventory or GET /api/inventory/alerts
      const data = await apiGet<InventoryRow[]>(alertsOnly ? '/inventory/alerts' : '/inventory');
      setItems(data);
    } catch { /* toast */ } finally { setLoading(false); }
  }, [alertsOnly]);

  useEffect(() => { load(); }, [load]);

  // Expiry alert banner — batches expiring in ≤ 5 days across all products
  const criticalExpiry = items.flatMap(i =>
    i.expiry_alerts.filter(a => a.days_to_expiry <= 5 && a.days_to_expiry > 0)
      .map(a => ({ ...a, productName: i.name }))
  );
  const expired = items.flatMap(i =>
    i.expiry_alerts.filter(a => a.days_to_expiry <= 0).map(a => ({ ...a, productName: i.name }))
  );

  const filtered = items
    .filter(i => statusFilter === 'all' || i.stock_status === statusFilter)
    .filter(i => !search || i.name.toLowerCase().includes(search.toLowerCase()) || i.sku.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      const pri: Record<string, number> = { out_of_stock: 0, critical: 1, warning: 2, excess: 3, ok: 4 };
      return (pri[a.stock_status] ?? 5) - (pri[b.stock_status] ?? 5);
    });

  const counts = Object.keys(STATUS).reduce((acc, k) => ({
    ...acc,
    [k]: items.filter(i => i.stock_status === k).length,
  }), {} as Record<string, number>);

  return (
    <div className="page-enter flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Inventory</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            {items.length} products · {counts.out_of_stock + counts.critical} critical alerts
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setAlertsOnly(v => !v)}
            className={alertsOnly ? 'btn-primary text-xs' : 'btn-ghost text-xs'}>
            <AlertTriangle size={12} /> {alertsOnly ? 'Alerts Only ✓' : 'Alerts Only'}
          </button>
          <button onClick={load} className="btn-ghost p-2"><RefreshCw size={13} /></button>
        </div>
      </div>

      {/* ── Expiry banners ─────────────────────────────────────────────── */}
      {expired.length > 0 && (
        <div className="rounded-xl px-4 py-3 flex flex-col gap-1"
          style={{ background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.3)' }}>
          <p className="text-xs font-bold" style={{ color: '#f43f5e' }}>🚨 EXPIRED STOCK — Remove immediately</p>
          {expired.map((e, i) => (
            <p key={i} className="text-xs" style={{ color: '#fca5a5' }}>
              {e.productName} · Batch #{e.batch_number} · {Math.round(e.quantity)} units EXPIRED
            </p>
          ))}
        </div>
      )}
      {criticalExpiry.length > 0 && (
        <div className="rounded-xl px-4 py-3 flex flex-col gap-1"
          style={{ background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.25)' }}>
          <p className="text-xs font-bold" style={{ color: '#f59e0b' }}>⚠️ Expiring within 5 days</p>
          {criticalExpiry.map((e, i) => (
            <p key={i} className="text-xs" style={{ color: '#fde68a' }}>
              {e.productName} · Batch #{e.batch_number} · {Math.round(e.quantity)} units · {e.days_to_expiry}d left
            </p>
          ))}
        </div>
      )}

      {/* ── Status filter chips ──────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-2">
        <button onClick={() => setStatusFilter('all')}
          className="text-xs px-3 py-1.5 rounded-xl font-medium"
          style={{ background: statusFilter === 'all' ? 'rgba(59,130,246,0.15)' : 'var(--bg-card)', border: '1px solid ' + (statusFilter === 'all' ? 'rgba(59,130,246,0.3)' : 'var(--border)'), color: statusFilter === 'all' ? '#93c5fd' : 'var(--text-secondary)' }}>
          All ({items.length})
        </button>
        {(Object.entries(STATUS) as [InventoryRow['stock_status'], typeof STATUS[keyof typeof STATUS]][]).map(([k, v]) => counts[k] > 0 && (
          <button key={k} onClick={() => setStatusFilter(statusFilter === k ? 'all' : k)}
            className="text-xs px-3 py-1.5 rounded-xl font-medium"
            style={{ background: statusFilter === k ? v.bg : 'var(--bg-card)', border: `1px solid ${statusFilter === k ? v.border : 'var(--border)'}`, color: statusFilter === k ? v.color : 'var(--text-secondary)' }}>
            {v.label} ({counts[k]})
          </button>
        ))}
      </div>

      {/* ── Search ──────────────────────────────────────────────────────── */}
      <div className="relative">
        <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
        <input className="input pl-9" placeholder="Search by name or SKU…" value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {/* ── Column headers ──────────────────────────────────────────────── */}
      <div className="grid text-[10px] font-semibold uppercase tracking-wider px-4 py-2 rounded-lg"
        style={{ gridTemplateColumns: '90px 1fr 90px 100px 110px 90px 28px', color: 'var(--text-muted)', background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
        <span>SKU</span><span>Product</span><span className="text-right">Stock</span>
        <span className="text-right">Days Left</span><span className="text-right">Nearest Expiry</span>
        <span>Status</span><span />
      </div>

      {/* ── Rows ────────────────────────────────────────────────────────── */}
      {loading
        ? [0,1,2,3,4].map(i => <div key={i} className="skeleton h-14 rounded-xl" />)
        : filtered.length === 0
          ? <div className="card py-12 flex flex-col items-center gap-2" style={{ borderStyle: 'dashed' }}>
              <Package size={26} style={{ color: 'var(--text-muted)' }} />
              <p style={{ color: 'var(--text-muted)' }}>No products found</p>
            </div>
          : <div className="flex flex-col gap-2">{filtered.map(item => <Row key={item.product_id} item={item} />)}</div>
      }
    </div>
  );
}
