import React, { useState, useEffect, useCallback } from 'react';
import {
  ShoppingCart, CheckCircle2, Clock, XCircle,
  Send, Loader2, Filter, RefreshCw, AlertTriangle
} from 'lucide-react';
import toast from 'react-hot-toast';
import type { Order, OrderCycle, OrderStatus } from '../types';
import { apiGet, apiPost } from '../api/client';
import OrderCard from '../components/recommendations/OrderCard';

// ── Filter config ─────────────────────────────────────────────────────────────

const CYCLE_FILTERS: { value: OrderCycle | 'all'; label: string }[] = [
  { value: 'all',       label: 'All Orders'  },
  { value: 'emergency', label: '🚨 Emergency' },
  { value: 'daily',     label: '📅 Daily'    },
  { value: 'weekly',    label: '📆 Weekly'   },
  { value: 'monthly',   label: '🗓 Monthly'  },
];

// ── Stat pill ─────────────────────────────────────────────────────────────────

function StatPill({
  count, label, color, icon,
}: { count: number; label: string; color: string; icon: React.ReactNode }) {
  return (
    <div
      className="flex items-center gap-2 rounded-xl px-4 py-3"
      style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
    >
      <span style={{ color }}>{icon}</span>
      <div>
        <p className="text-xl font-bold mono leading-none" style={{ color }}>{count}</p>
        <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>{label}</p>
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function OrdersPage() {
  const [orders,     setOrders]     = useState<Order[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [approveAll, setApproveAll] = useState(false);
  const [cycleFilter,setCycleFilter]= useState<OrderCycle | 'all'>('all');
  const [showHistory,setShowHistory]= useState(false);

  // ── Load orders ─────────────────────────────────────────────────────
  const loadOrders = useCallback(async () => {
    setLoading(true);
    try {
      const endpoint = showHistory ? '/orders/history' : '/orders/pending';
      const data = await apiGet<Order[]>(endpoint);
      setOrders(data);
    } catch {
      // toast by interceptor
    } finally {
      setLoading(false);
    }
  }, [showHistory]);

  useEffect(() => { loadOrders(); }, [loadOrders]);

  // ── Approve all ─────────────────────────────────────────────────────
  const handleApproveAll = useCallback(async () => {
    const pending = orders.filter((o) => o.status === 'pending_approval');
    if (!pending.length) return;

    setApproveAll(true);
    try {
      const result = await apiPost<{ message: string; results: { order_id: number; whatsapp_sent: boolean }[] }>(
        '/orders/approve-all'
      );
      const sentCount = result.results.filter((r) => r.whatsapp_sent).length;
      toast.success(
        `${pending.length} orders approved! ${sentCount} WhatsApp messages sent. 🎉`,
        {
          duration: 6000,
          style: {
            background: '#052e16',
            color: '#6ee7b7',
            border: '1px solid rgba(52,211,153,0.3)',
            fontSize: '14px',
            fontWeight: '600',
            padding: '14px 18px',
            borderRadius: '12px',
          },
          icon: '📲',
        }
      );
      await loadOrders();
    } catch {
      // toast by interceptor
    } finally {
      setApproveAll(false);
    }
  }, [orders, loadOrders]);

  // ── Local state mutations ────────────────────────────────────────────
  const handleUpdated = useCallback((updated: Order) => {
    setOrders((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
  }, []);

  const handleRejected = useCallback((id: number) => {
    setOrders((prev) =>
      prev.map((o) => (o.id === id ? { ...o, status: 'rejected' as OrderStatus } : o))
    );
  }, []);

  // ── Filtered + sorted orders ─────────────────────────────────────────
  const filtered = orders
    .filter((o) => cycleFilter === 'all' || o.order_cycle === cycleFilter)
    .sort((a, b) => {
      const priority = { emergency: 0, daily: 1, weekly: 2, monthly: 3 };
      return (priority[a.order_cycle] ?? 4) - (priority[b.order_cycle] ?? 4);
    });

  // ── Stats ────────────────────────────────────────────────────────────
  const pending   = orders.filter((o) => o.status === 'pending_approval');
  const sent      = orders.filter((o) => o.status === 'sent_whatsapp');
  const emergency = orders.filter((o) => o.order_cycle === 'emergency');
  const totalCost = pending.reduce((s, o) => s + (o.total_cost || 0), 0);

  return (
    <div className="page-enter flex flex-col gap-6">

      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Order Recommendations
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            AI-drafted orders from this morning's pipeline — review, edit, and approve
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            id="btn-refresh-orders"
            onClick={loadOrders}
            className="btn-ghost py-2 px-3"
            title="Refresh"
          >
            <RefreshCw size={14} />
          </button>
          {pending.length > 0 && (
            <button
              id="btn-approve-all"
              onClick={handleApproveAll}
              disabled={approveAll}
              className="btn-success disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {approveAll
                ? <><Loader2 size={14} className="animate-spin" /> Approving…</>
                : <><Send size={14} /> Approve All ({pending.length})</>
              }
            </button>
          )}
        </div>
      </div>

      {/* ── Stats row ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
        <StatPill count={pending.length}   label="Pending Approval" color="#fbbf24" icon={<Clock size={16} />} />
        <StatPill count={sent.length}      label="Sent via WhatsApp" color="#34d399" icon={<CheckCircle2 size={16} />} />
        <StatPill count={emergency.length} label="Emergency Orders"  color="#f43f5e" icon={<AlertTriangle size={16} />} />
        <div
          className="flex items-center gap-2 rounded-xl px-4 py-3"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
        >
          <span style={{ color: '#6ee7b7' }}>₹</span>
          <div>
            <p className="text-xl font-bold mono leading-none" style={{ color: '#6ee7b7' }}>
              {Math.round(totalCost).toLocaleString('en-IN')}
            </p>
            <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
              Pending order value
            </p>
          </div>
        </div>
      </div>

      {/* ── Filters ─────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter size={13} style={{ color: 'var(--text-muted)' }} />
          {CYCLE_FILTERS.map((f) => (
            <button
              key={f.value}
              id={`filter-cycle-${f.value}`}
              onClick={() => setCycleFilter(f.value as any)}
              className="text-xs px-3 py-1.5 rounded-lg font-medium transition-all"
              style={{
                background: cycleFilter === f.value ? 'rgba(59,130,246,0.15)' : 'var(--bg-card)',
                border:     cycleFilter === f.value ? '1px solid rgba(59,130,246,0.3)' : '1px solid var(--border)',
                color:      cycleFilter === f.value ? '#93c5fd' : 'var(--text-secondary)',
              }}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* History toggle */}
        <button
          id="btn-toggle-history"
          onClick={() => setShowHistory((s) => !s)}
          className="text-xs flex items-center gap-1.5"
          style={{ color: showHistory ? '#60a5fa' : 'var(--text-muted)' }}
        >
          <ShoppingCart size={12} />
          {showHistory ? 'Showing History' : 'Show History'}
        </button>
      </div>

      {/* ── Loading ──────────────────────────────────────────────── */}
      {loading && (
        <div className="flex flex-col gap-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="card h-48 skeleton" />
          ))}
        </div>
      )}

      {/* ── Empty state ──────────────────────────────────────────── */}
      {!loading && filtered.length === 0 && (
        <div
          className="card flex flex-col items-center justify-center gap-3 py-16"
          style={{ borderStyle: 'dashed' }}
        >
          <ShoppingCart size={28} style={{ color: 'var(--text-muted)' }} />
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
            {orders.length === 0
              ? 'No orders yet — run the morning briefing to generate recommendations'
              : 'No orders match the selected filter'}
          </p>
          {orders.length === 0 && (
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              Go to Dashboard → click <strong>Run Briefing</strong>
            </p>
          )}
        </div>
      )}

      {/* ── Order cards ──────────────────────────────────────────── */}
      {!loading && filtered.length > 0 && (
        <div className="flex flex-col gap-4">
          {filtered.map((order) => (
            <OrderCard
              key={order.id}
              order={order}
              onUpdated={handleUpdated}
              onRejected={handleRejected}
            />
          ))}
        </div>
      )}
    </div>
  );
}
