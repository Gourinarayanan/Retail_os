import React, { useState, useRef, useCallback } from 'react';
import {
  Package, CheckCircle2, XCircle,
  Send, Truck, IndianRupee, Zap
} from 'lucide-react';
import type { Order } from '../../types';
import { apiPatch } from '../../api/client';
import EditableQuantityInput from './EditableQuantityInput';
import ReasoningPanel from './ReasoningPanel';
import OrderApprovalModal from '../modals/OrderApprovalModal';

// ── Helpers ───────────────────────────────────────────────────────────────────

const CYCLE_STYLES: Record<string, { badge: string; label: string }> = {
  daily:     { badge: 'badge-blue',   label: '📅 Daily'     },
  weekly:    { badge: 'badge-violet', label: '📆 Weekly'    },
  monthly:   { badge: 'badge-gray',   label: '🗓 Monthly'   },
  emergency: { badge: 'badge-red',    label: '🚨 Emergency' },
};

const STATUS_STYLES: Record<string, { color: string; label: string }> = {
  pending_approval: { color: '#fbbf24', label: 'Pending'        },
  approved:         { color: '#34d399', label: 'Approved'       },
  sent_whatsapp:    { color: '#34d399', label: '✓ Sent'         },
  rejected:         { color: '#f87171', label: 'Rejected'       },
};

// ── OrderCard ─────────────────────────────────────────────────────────────────

interface OrderCardProps {
  order:     Order;
  onUpdated: (updated: Order) => void;
  onRejected:(id: number)    => void;
}

export default function OrderCard({ order, onUpdated, onRejected }: OrderCardProps) {
  const [currentQty,    setCurrentQty]    = useState(order.final_qty);
  const [saving,        setSaving]        = useState(false);
  const [showApproval,  setShowApproval]  = useState(false);
  const [rejected,      setRejected]      = useState(order.status === 'rejected');
  const [ownerModified, setOwnerModified] = useState(order.owner_modified);
  const [note,          setNote]          = useState(order.owner_note ?? '');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const isApproved  = order.status === 'sent_whatsapp' || order.status === 'approved';
  const isPending   = order.status === 'pending_approval' && !rejected;
  const isEmergency = order.order_cycle === 'emergency';

  const cycleStyle  = CYCLE_STYLES[order.order_cycle] ?? CYCLE_STYLES.daily;
  const statusStyle = STATUS_STYLES[order.status] ?? STATUS_STYLES.pending_approval;

  // ── Debounced PATCH on quantity change ───────────────────────────────
  const handleQtyChange = useCallback((newQty: number) => {
    setCurrentQty(newQty);
    setOwnerModified(true);

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      setSaving(true);
      try {
        const updated = await apiPatch<Order>(`/orders/${order.id}`, {
          final_qty: newQty,
          owner_note: note || null,
        });
        onUpdated(updated);
      } catch {
        /* toast shown by interceptor */
      } finally {
        setSaving(false);
      }
    }, 500);
  }, [order.id, note, onUpdated]);

  // ── Reject ─────────────────────────────────────────────────────────
  const handleReject = useCallback(async () => {
    try {
      await apiPatch<void>(`/orders/${order.id}/reject`, { reason: 'Rejected by owner' });
      setRejected(true);
      onRejected(order.id);
    } catch { /* toast by interceptor */ }
  }, [order.id, onRejected]);

  // ── Derived display values ──────────────────────────────────────────
  const costDisplay = (currentQty * order.price_per_unit).toLocaleString('en-IN', {
    maximumFractionDigits: 0,
  });

  return (
    <>
      <div
        id={`order-card-${order.id}`}
        className="card flex flex-col gap-4 transition-all duration-200"
        style={{
          borderColor: isEmergency
            ? 'rgba(244,63,94,0.4)'
            : rejected
            ? 'rgba(100,116,139,0.25)'
            : isApproved
            ? 'rgba(52,211,153,0.25)'
            : 'var(--border)',
          opacity: rejected ? 0.55 : 1,
        }}
      >
        {/* ── Header row ─────────────────────────────────────────── */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            {/* Category icon */}
            <div
              className="flex h-10 w-10 items-center justify-center rounded-xl shrink-0"
              style={{
                background: isEmergency ? 'rgba(244,63,94,0.1)' : 'rgba(59,130,246,0.1)',
              }}
            >
              {isEmergency
                ? <Zap size={18} style={{ color: '#f43f5e' }} />
                : <Package size={18} style={{ color: '#60a5fa' }} />
              }
            </div>

            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>
                  {order.product_name}
                </h3>
                <span className="mono text-[10px]" style={{ color: 'var(--text-muted)' }}>
                  {order.product_sku}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <span className={cycleStyle.badge}>{cycleStyle.label}</span>
                <span
                  className="text-[11px] px-2 py-0.5 rounded-full font-medium"
                  style={{
                    background: 'rgba(0,0,0,0.2)',
                    color: statusStyle.color,
                    border: `1px solid ${statusStyle.color}30`,
                  }}
                >
                  {statusStyle.label}
                </span>
                {saving && (
                  <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                    saving…
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Total cost */}
          <div className="text-right shrink-0">
            <div className="flex items-center gap-0.5 justify-end">
              <IndianRupee size={14} style={{ color: '#6ee7b7' }} />
              <span className="text-lg font-bold mono" style={{ color: '#6ee7b7' }}>
                {costDisplay}
              </span>
            </div>
            <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
              ₹{order.price_per_unit}/{order.unit}
            </p>
          </div>
        </div>

        {/* ── Supplier row ────────────────────────────────────────── */}
        <div
          className="flex items-center gap-3 rounded-lg px-3 py-2.5"
          style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
        >
          <Truck size={13} style={{ color: 'var(--text-muted)' }} />
          <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            {order.supplier_name}
          </span>
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
            · {order.supplier_contact}
          </span>
          <span className="mono text-xs ml-auto" style={{ color: '#60a5fa' }}>
            {order.supplier_whatsapp}
          </span>
        </div>

        {/* ── Quantity input + Reasoning (side by side) ──────────── */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {/* Left: qty input + note */}
          <div className="flex flex-col gap-3">
            <EditableQuantityInput
              orderId={order.id}
              value={currentQty}
              aiSuggestion={order.ai_recommended_qty}
              unit={order.unit}
              ownerModified={ownerModified}
              onChange={handleQtyChange}
              disabled={!isPending}
            />
            {isPending && (
              <div className="flex flex-col gap-1">
                <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                  Owner note (optional)
                </span>
                <input
                  type="text"
                  className="input text-xs py-1.5"
                  placeholder="Add a note…"
                  value={note}
                  maxLength={300}
                  onChange={(e) => setNote(e.target.value)}
                  onBlur={() => {
                    if (note !== order.owner_note) {
                      apiPatch(`/orders/${order.id}`, { final_qty: currentQty, owner_note: note });
                    }
                  }}
                />
              </div>
            )}
          </div>

          {/* Right: full reasoning */}
          <ReasoningPanel
            orderId={order.id}
            reasoning={order.ai_reasoning}
          />
        </div>

        {/* ── Action buttons ──────────────────────────────────────── */}
        {isPending && (
          <div className="flex items-center gap-2 pt-1">
            <button
              id={`btn-approve-${order.id}`}
              onClick={() => setShowApproval(true)}
              className="btn-success flex-1"
              aria-label={`Approve and send order for ${order.product_name}`}
            >
              <Send size={13} />
              Approve &amp; Send WhatsApp
            </button>
            <button
              id={`btn-reject-${order.id}`}
              onClick={handleReject}
              className="btn-danger px-3 py-2"
              aria-label={`Reject order for ${order.product_name}`}
            >
              <XCircle size={13} />
              Reject
            </button>
          </div>
        )}

        {/* Sent state */}
        {isApproved && (
          <div
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm"
            style={{ background: 'rgba(52,211,153,0.08)', border: '1px solid rgba(52,211,153,0.2)' }}
          >
            <CheckCircle2 size={14} style={{ color: '#34d399' }} />
            <span style={{ color: '#6ee7b7' }}>
              {order.status === 'sent_whatsapp'
                ? `WhatsApp sent to ${order.supplier_name}`
                : 'Order approved'}
            </span>
          </div>
        )}
      </div>

      {/* ── Approval Modal ──────────────────────────────────────── */}
      {showApproval && (
        <OrderApprovalModal
          order={{ ...order, final_qty: currentQty, total_cost: currentQty * order.price_per_unit }}
          onClose={() => setShowApproval(false)}
          onSent={(updated) => {
            setShowApproval(false);
            onUpdated(updated);
          }}
        />
      )}
    </>
  );
}
