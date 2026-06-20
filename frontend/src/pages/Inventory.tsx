import React, { useState, useEffect, useCallback } from 'react';
import {
  Package, AlertTriangle, Search, RefreshCw,
  ChevronDown, ChevronUp, Boxes,
} from 'lucide-react';
import { apiGet, apiPatch } from '../api/client';
import toast from 'react-hot-toast';

interface ExpiryAlert {
  batch_number: string; days_to_expiry: number; quantity: number;
  severity: 'expired' | 'critical_expiry' | 'expiring_soon';
}
interface InventoryBatch {
  id: number; batch_number: string; quantity: number; unit: string;
  purchase_price: number | null; expiry_date: string | null;
  days_to_expiry: number | null; status: string; created_at: string;
}
interface InventoryRow {
  product_id: number; name: string; sku: string; category: string;
  brand: string | null; unit: string; selling_price: number; cost_price: number;
  avg_daily_demand: number; reorder_point_days: number; lead_time_days: number;
  current_stock: number; days_remaining: number;
  stock_status: 'out_of_stock' | 'critical' | 'warning' | 'excess' | 'ok';
  expiry_alerts: ExpiryAlert[]; batches: InventoryBatch[];
}

const STATUS_STYLES: Record<InventoryRow['stock_status'], { label: string; class: string }> = {
  out_of_stock: { label: 'Out of Stock', class: 'bg-red-100 text-red-600 border border-red-200' },
  critical:     { label: 'Critical',     class: 'bg-red-50 text-red-500 border border-red-200' },
  warning:      { label: 'Warning',      class: 'bg-amber-50 text-amber-600 border border-amber-200' },
  excess:       { label: 'Excess',       class: 'bg-sky-50 text-sky-600 border border-sky-200' },
  ok:           { label: 'In Stock',     class: 'bg-emerald-50 text-emerald-600 border border-emerald-200' },
};

function Row({ item }: { item: InventoryRow }) {
  const [open, setOpen]     = useState(false);
  const [qty, setQty]       = useState<{ batchId: number; val: number } | null>(null);
  const [saving, setSaving] = useState(false);
  const s = STATUS_STYLES[item.stock_status];
  const nearestExpiry = item.batches
    .filter(b => b.expiry_date !== null)
    .sort((a, b) => (a.days_to_expiry ?? 999) - (b.days_to_expiry ?? 999))[0] ?? null;

  const saveQty = async () => {
    if (!qty) return;
    setSaving(true);
    try {
      await apiPatch(`/inventory/${qty.batchId}/quantity`, { quantity: qty.val });
      toast.success('Stock updated');
      setQty(null);
    } catch { } finally { setSaving(false); }
  };

  const stockPct = Math.min(100, (item.current_stock / Math.max(item.current_stock * 2, 1)) * 100);

  return (
    <div className="glass-panel rounded-xl overflow-hidden border border-border-glass">
      <div
        className="grid items-center gap-4 px-5 py-4 cursor-pointer hover:bg-surface-container-low transition-colors"
        style={{ gridTemplateColumns: '90px 1fr 110px 100px 100px 100px 32px' }}
        onClick={() => setOpen(v => !v)}
      >
        <span className="font-mono text-xs text-on-surface-variant">{item.sku}</span>
        <div>
          <p className="text-sm font-semibold text-on-surface">{item.name}</p>
          <p className="text-[10px] text-on-surface-variant uppercase tracking-wider mt-0.5">
            {item.category}{item.brand ? ` · ${item.brand}` : ''}
          </p>
        </div>
        <div className="space-y-1">
          <p className={`font-bold font-mono text-sm ${item.stock_status === 'out_of_stock' || item.stock_status === 'critical' ? 'text-error' : 'text-on-surface'}`}>
            {Math.round(item.current_stock)} {item.unit}s
          </p>
          <div className="w-full h-1 bg-surface-container-highest rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${item.stock_status === 'out_of_stock' ? 'bg-error' : item.stock_status === 'critical' || item.stock_status === 'warning' ? 'bg-status-warning' : 'bg-status-success'}`}
              style={{ width: `${stockPct}%` }}
            />
          </div>
        </div>
        <div className="text-right">
          <p className={`font-mono text-sm font-bold ${item.days_remaining < 3 ? 'text-error' : 'text-on-surface-variant'}`}>
            {item.days_remaining >= 999 ? '∞' : `${item.days_remaining}d`}
          </p>
          <p className="text-[10px] text-on-surface-variant/60">remaining</p>
        </div>
        <div className="text-right text-xs text-on-surface-variant">
          {nearestExpiry?.expiry_date
            ? <span className={(nearestExpiry.days_to_expiry ?? 999) <= 5 ? 'text-error font-semibold' : ''}>{nearestExpiry.expiry_date}</span>
            : '—'}
        </div>
        <span className={`text-[10px] font-semibold font-label-xs px-2 py-0.5 rounded-full text-center uppercase ${s.class}`}>
          {s.label}
        </span>
        <span className="text-on-surface-variant">{open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}</span>
      </div>

      {open && (
        <div className="px-5 pb-4 pt-3 border-t border-border-glass bg-surface-container-low/30 flex flex-col gap-2">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-on-surface-variant">Batches</p>
          {item.batches.filter(b => b.status !== 'depleted').map(b => (
            <div key={b.id} className="flex items-center justify-between text-xs px-3 py-2 rounded-lg bg-surface-container-low border border-border-glass gap-4">
              <span className="font-mono text-on-surface-variant">#{b.batch_number}</span>
              {qty?.batchId === b.id ? (
                <div className="flex items-center gap-2">
                  <input type="number" className="nexus-input w-20 py-1 text-xs text-center rounded px-2"
                    value={qty.val} min={0} step={0.1}
                    onChange={e => setQty({ batchId: b.id, val: parseFloat(e.target.value) || 0 })} />
                  <button onClick={saveQty} disabled={saving}
                    className="px-2 py-1 bg-primary text-white text-xs rounded hover:bg-indigo-700 transition-colors font-semibold disabled:opacity-50">
                    {saving ? 'Saving…' : 'Save'}
                  </button>
                  <button onClick={() => setQty(null)}
                    className="px-2 py-1 bg-surface-container-high text-on-surface-variant text-xs rounded hover:bg-surface-container-highest transition-colors">
                    Cancel
                  </button>
                </div>
              ) : (
                <>
                  <span className="font-semibold text-on-surface">{Math.round(b.quantity)} {b.unit}s</span>
                  <span className={(b.days_to_expiry ?? 999) <= 5 ? 'text-error font-semibold' : 'text-on-surface-variant'}>
                    {b.expiry_date ? `Exp: ${b.expiry_date}` : 'No expiry'}
                    {b.days_to_expiry !== null && b.days_to_expiry <= 10 && ` (${b.days_to_expiry}d)`}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${b.status === 'active' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'}`}>
                    {b.status}
                  </span>
                  <button onClick={() => setQty({ batchId: b.id, val: b.quantity })}
                    className="text-[11px] text-primary hover:text-indigo-700 font-semibold transition-colors">
                    Adjust
                  </button>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function InventoryPage() {
  const [items, setItems]           = useState<InventoryRow[]>([]);
  const [loading, setLoading]       = useState(true);
  const [search, setSearch]         = useState('');
  const [statusFilter, setStatusFilter] = useState<InventoryRow['stock_status'] | 'all'>('all');
  const [alertsOnly, setAlertsOnly] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<InventoryRow[]>(alertsOnly ? '/inventory/alerts' : '/inventory');
      setItems(data);
    } catch { } finally { setLoading(false); }
  }, [alertsOnly]);

  useEffect(() => { load(); }, [load]);

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

  const counts = (Object.keys(STATUS_STYLES) as InventoryRow['stock_status'][]).reduce((acc, k) => ({
    ...acc, [k]: items.filter(i => i.stock_status === k).length,
  }), {} as Record<string, number>);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="font-headline-lg text-on-surface">Inventory Command Hub</h3>
          <p className="font-body-md text-on-surface-variant mt-1">
            {items.length} products · {(counts.out_of_stock || 0) + (counts.critical || 0)} critical alerts
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <button
            id="btn-alerts-only"
            onClick={() => setAlertsOnly(v => !v)}
            className={`px-4 py-2 rounded-lg font-label-md text-xs uppercase tracking-wider transition-all border flex items-center gap-1.5 ${alertsOnly ? 'bg-primary/10 text-primary border-primary' : 'bg-surface-container-low text-on-surface-variant border-border-glass hover:bg-surface-container-high'}`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            {alertsOnly ? 'Alerts Only ✓' : 'Alerts Only'}
          </button>
          <button onClick={load} className="p-2 border border-border-glass rounded-lg text-on-surface-variant hover:text-primary hover:border-primary transition-all">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Expiry banners */}
      {expired.length > 0 && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 space-y-1">
          <p className="text-xs font-bold text-red-600">🚨 EXPIRED STOCK — Remove immediately</p>
          {expired.map((e, i) => (
            <p key={i} className="text-xs text-red-500">{e.productName} · Batch #{e.batch_number} · {Math.round(e.quantity)} units EXPIRED</p>
          ))}
        </div>
      )}
      {criticalExpiry.length > 0 && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 space-y-1">
          <p className="text-xs font-bold text-amber-600">⚠️ Expiring within 5 days</p>
          {criticalExpiry.map((e, i) => (
            <p key={i} className="text-xs text-amber-600">{e.productName} · Batch #{e.batch_number} · {Math.round(e.quantity)} units · {e.days_to_expiry}d left</p>
          ))}
        </div>
      )}

      {/* Status filter tabs */}
      <div className="flex flex-wrap items-center gap-2">
        <button onClick={() => setStatusFilter('all')}
          className={`px-4 py-2 rounded-lg font-label-md text-xs uppercase tracking-wider transition-all border ${statusFilter === 'all' ? 'bg-primary/10 text-primary border-primary' : 'bg-surface-container-low text-on-surface-variant border-border-glass hover:bg-surface-container-high'}`}>
          All ({items.length})
        </button>
        {(Object.entries(STATUS_STYLES) as [InventoryRow['stock_status'], typeof STATUS_STYLES[keyof typeof STATUS_STYLES]][]).map(([k, v]) =>
          counts[k] > 0 && (
            <button key={k} onClick={() => setStatusFilter(statusFilter === k ? 'all' : k)}
              className={`px-4 py-2 rounded-lg font-label-md text-xs uppercase tracking-wider transition-all border ${statusFilter === k ? v.class : 'bg-surface-container-low text-on-surface-variant border-border-glass hover:bg-surface-container-high'}`}>
              {v.label} ({counts[k]})
            </button>
          )
        )}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant" />
        <input className="nexus-input w-full pl-10 pr-4 py-2.5 rounded-lg text-sm" placeholder="Search by name or SKU…"
          value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {/* Column headers */}
      <div className="grid text-[10px] font-semibold uppercase tracking-wider px-5 py-2.5 rounded-lg bg-surface-container-low border border-border-glass text-on-surface-variant"
        style={{ gridTemplateColumns: '90px 1fr 110px 100px 100px 100px 32px' }}>
        <span>SKU</span><span>Product</span><span>Stock</span>
        <span className="text-right">Days Left</span><span className="text-right">Exp. Date</span>
        <span>Status</span><span />
      </div>

      {/* Rows */}
      {loading
        ? [0,1,2,3,4].map(i => <div key={i} className="glass-panel h-16 rounded-xl border border-border-glass animate-pulse" />)
        : filtered.length === 0
          ? (
            <div className="glass-panel py-16 flex flex-col items-center gap-3 rounded-xl border border-border-glass">
              <Boxes className="w-8 h-8 text-on-surface-variant/40" />
              <p className="text-on-surface-variant font-medium">No products found</p>
            </div>
          )
          : <div className="flex flex-col gap-3">{filtered.map(item => <Row key={item.product_id} item={item} />)}</div>
      }
    </div>
  );
}
