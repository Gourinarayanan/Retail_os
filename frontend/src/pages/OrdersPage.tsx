import React, { useState, useEffect, useCallback } from 'react';
import {
  ShoppingCart, CheckCircle2, Clock, XCircle,
  Send, Loader2, Filter, RefreshCw, AlertTriangle, Layers
} from 'lucide-react';
import toast from 'react-hot-toast';
import type { Order, OrderCycle, OrderStatus } from '../types';
import { apiGet, apiPost } from '../api/client';
import OrderCard from '../components/recommendations/OrderCard';
import { useSearch } from '../context/SearchContext';

const CYCLE_FILTERS: { value: OrderCycle | 'all'; label: string }[] = [
  { value: 'all',       label: 'All Orders'  },
  { value: 'emergency', label: '🚨 Emergency' },
  { value: 'daily',     label: '📅 Daily'    },
  { value: 'weekly',    label: '📆 Weekly'   },
  { value: 'monthly',   label: '🗓 Monthly'  },
];

function StatPill({ count, label, colorClass, icon, bgClass }: { count: number; label: string; colorClass: string; icon: React.ReactNode; bgClass: string }) {
  return (
    <div className="glass-panel p-5 rounded-xl border border-border-glass relative overflow-hidden group">
      <div className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full blur-2xl pointer-events-none transition-all duration-500 group-hover:scale-125 ${bgClass}`} />
      <div className="flex items-center gap-4 relative z-10">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border border-border-glass bg-surface-container`}>
          <span className={colorClass}>{icon}</span>
        </div>
        <div>
          <p className={`font-headline-lg font-bold font-mono ${colorClass}`}>{count}</p>
          <p className="font-label-xs text-xs uppercase tracking-wider text-on-surface-variant mt-0.5">{label}</p>
        </div>
      </div>
    </div>
  );
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [approveAll, setApproveAll] = useState(false);
  const [cycleFilter, setCycleFilter] = useState<OrderCycle | 'all'>('all');
  const [showHistory, setShowHistory] = useState(false);

  const { searchQuery } = useSearch();

  const loadOrders = useCallback(async () => {
    setLoading(true);
    try {
      const endpoint = showHistory ? '/orders/history' : '/orders/pending';
      const data = await apiGet<Order[]>(endpoint);
      setOrders(data);
    } catch { } finally { setLoading(false); }
  }, [showHistory]);

  useEffect(() => { loadOrders(); }, [loadOrders]);

  const handleApproveAll = useCallback(async () => {
    const pending = orders.filter(o => o.status === 'pending_approval');
    if (!pending.length) return;

    setApproveAll(true);
    try {
      const result = await apiPost<{ message: string; results: { order_id: number; whatsapp_sent: boolean }[] }>('/orders/approve-all');
      const sentCount = result.results.filter(r => r.whatsapp_sent).length;
      toast.success(`${pending.length} orders approved! ${sentCount} WhatsApp messages sent. 🎉`, {
        duration: 6000,
        style: { background: '#052e16', color: '#6ee7b7', border: '1px solid rgba(52,211,153,0.3)', borderRadius: '12px' },
        icon: '📲',
      });
      await loadOrders();
    } catch { } finally { setApproveAll(false); }
  }, [orders, loadOrders]);

  const handleUpdated = useCallback((updated: Order) => {
    setOrders(prev => prev.map(o => (o.id === updated.id ? updated : o)));
  }, []);

  const handleRejected = useCallback((id: number) => {
    setOrders(prev => prev.map(o => (o.id === id ? { ...o, status: 'rejected' as OrderStatus } : o)));
  }, []);

  const filtered = orders
    .filter(o => cycleFilter === 'all' || o.order_cycle === cycleFilter)
    .filter(o => {
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      // Safely access properties as any to avoid strict type errors if some fields are missing
      const orderAny = o as any;
      return (orderAny.product_name?.toLowerCase().includes(q) ||
              orderAny.supplier_name?.toLowerCase().includes(q) ||
              orderAny.product_sku?.toLowerCase().includes(q));
    })
    .sort((a, b) => {
      const priority = { emergency: 0, daily: 1, weekly: 2, monthly: 3 };
      return (priority[a.order_cycle] ?? 4) - (priority[b.order_cycle] ?? 4);
    });

  const pending = orders.filter(o => o.status === 'pending_approval');
  const sent = orders.filter(o => o.status === 'sent_whatsapp');
  const emergency = orders.filter(o => o.order_cycle === 'emergency');
  const totalCost = pending.reduce((s, o) => s + (o.total_cost || 0), 0);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h3 className="font-headline-lg text-on-surface">Order Recommendations</h3>
          <p className="font-body-md text-on-surface-variant mt-1">
            AI-drafted orders from this morning's pipeline — review, edit, and approve
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <button onClick={loadOrders} className="p-2 border border-border-glass rounded-lg text-on-surface-variant hover:text-primary hover:border-primary transition-all">
            <RefreshCw className="w-4 h-4" />
          </button>
          {pending.length > 0 && (
            <button
              onClick={handleApproveAll}
              disabled={approveAll}
              className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-label-md text-xs tracking-wider uppercase transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {approveAll ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Approving…</> : <><Send className="w-3.5 h-3.5" /> Approve All ({pending.length})</>}
            </button>
          )}
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatPill count={pending.length} label="Pending Approval" colorClass="text-amber-500" icon={<Clock className="w-5 h-5" />} bgClass="bg-amber-500/10" />
        <StatPill count={sent.length} label="Sent via WhatsApp" colorClass="text-emerald-500" icon={<CheckCircle2 className="w-5 h-5" />} bgClass="bg-emerald-500/10" />
        <StatPill count={emergency.length} label="Emergency Orders" colorClass="text-error" icon={<AlertTriangle className="w-5 h-5" />} bgClass="bg-error/10" />
        <div className="glass-panel p-5 rounded-xl border border-border-glass relative overflow-hidden group">
          <div className="absolute -right-4 -bottom-4 w-24 h-24 rounded-full blur-2xl pointer-events-none transition-all duration-500 group-hover:scale-125 bg-primary/10" />
          <div className="flex items-center gap-4 relative z-10">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border border-border-glass bg-surface-container text-primary">
              <span className="text-xl font-bold font-mono">₹</span>
            </div>
            <div>
              <p className="font-headline-lg font-bold font-mono text-primary">{Math.round(totalCost).toLocaleString('en-IN')}</p>
              <p className="font-label-xs text-xs uppercase tracking-wider text-on-surface-variant mt-0.5">Pending Value</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-2">
        <div className="flex flex-wrap items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center border border-border-glass">
            <Filter className="w-4 h-4 text-on-surface-variant" />
          </div>
          {CYCLE_FILTERS.map(f => (
            <button
              key={f.value}
              onClick={() => setCycleFilter(f.value as any)}
              className={`px-4 py-2 rounded-lg font-label-md text-xs uppercase tracking-wider transition-all border ${
                cycleFilter === f.value ? 'bg-primary/10 text-primary border-primary' : 'bg-surface-container-low text-on-surface-variant border-border-glass hover:bg-surface-container-high'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        <button
          onClick={() => setShowHistory(s => !s)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-label-md text-xs uppercase tracking-wider transition-all border ${
            showHistory ? 'bg-primary text-white border-primary shadow-sm' : 'bg-surface-container-low text-on-surface-variant border-border-glass hover:bg-surface-container-high'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          {showHistory ? 'Showing History' : 'Show History'}
        </button>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="space-y-4">
          {[0, 1, 2].map(i => <div key={i} className="glass-panel h-48 rounded-2xl border border-border-glass animate-pulse" />)}
        </div>
      )}

      {/* Empty state */}
      {!loading && filtered.length === 0 && (
        <div className="glass-panel py-16 flex flex-col items-center gap-4 rounded-2xl border border-border-glass border-dashed">
          <div className="w-16 h-16 rounded-2xl bg-surface-container flex items-center justify-center border border-border-glass">
            <ShoppingCart className="w-8 h-8 text-on-surface-variant/40" />
          </div>
          <div className="text-center">
            <p className="text-sm font-bold text-on-surface">
              {orders.length === 0 ? 'No orders yet' : 'No orders match filter'}
            </p>
            {orders.length === 0 && (
              <p className="text-xs text-on-surface-variant mt-1">
                Run the morning briefing on the dashboard to generate recommendations.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Orders List */}
      {!loading && filtered.length > 0 && (
        <div className="space-y-6">
          {filtered.map(order => (
            <OrderCard key={order.id} order={order} onUpdated={handleUpdated} onRejected={handleRejected} />
          ))}
        </div>
      )}
    </div>
  );
}
