import React, { useState, useRef, useCallback } from 'react';
import {
  Package, CheckCircle2, XCircle,
  Send, Truck, IndianRupee, Zap, MapPin
} from 'lucide-react';
import type { Order } from '../../types';
import { apiPatch } from '../../api/client';
import EditableQuantityInput from './EditableQuantityInput';
import ReasoningPanel from './ReasoningPanel';
import OrderApprovalModal from '../modals/OrderApprovalModal';

const CYCLE_STYLES: Record<string, { class: string; label: string }> = {
  daily:     { class: 'bg-primary/10 text-primary border-primary/20',     label: '📅 Daily' },
  weekly:    { class: 'bg-violet-100 text-violet-700 border-violet-200',  label: '📆 Weekly' },
  monthly:   { class: 'bg-surface-container-high text-on-surface-variant border-border-glass', label: '🗓 Monthly' },
  emergency: { class: 'bg-red-100 text-red-700 border-red-200',           label: '🚨 Emergency' },
};

const STATUS_STYLES: Record<string, { class: string; label: string }> = {
  pending_approval: { class: 'bg-amber-100 text-amber-700 border-amber-200', label: 'Pending' },
  approved:         { class: 'bg-emerald-100 text-emerald-700 border-emerald-200', label: 'Approved' },
  sent_whatsapp:    { class: 'bg-emerald-100 text-emerald-700 border-emerald-200', label: '✓ Sent' },
  rejected:         { class: 'bg-red-100 text-red-700 border-red-200', label: 'Rejected' },
};

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
      } catch { } finally { setSaving(false); }
    }, 500);
  }, [order.id, note, onUpdated]);

  const handleReject = useCallback(async () => {
    try {
      await apiPatch<void>(`/orders/${order.id}/reject`, { reason: 'Rejected by owner' });
      setRejected(true);
      onRejected(order.id);
    } catch { }
  }, [order.id, onRejected]);

  const costDisplay = (currentQty * order.price_per_unit).toLocaleString('en-IN', {
    maximumFractionDigits: 0,
  });

  return (
    <>
      <div
        id={`order-card-${order.id}`}
        className={`glass-panel rounded-2xl p-5 md:p-6 transition-all duration-300 relative overflow-hidden border ${
          isEmergency ? 'border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.1)]' :
          rejected ? 'border-border-glass opacity-60 grayscale-[0.3]' :
          isApproved ? 'border-emerald-500/30' : 'border-border-glass'
        }`}
      >
        {isEmergency && <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/10 rounded-full blur-3xl pointer-events-none" />}
        {isApproved && <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />}

        {/* Header row */}
        <div className="flex flex-col md:flex-row items-start justify-between gap-4 mb-5 pb-5 border-b border-border-glass/60 relative z-10">
          <div className="flex items-start gap-4">
            <div className={`flex items-center justify-center w-12 h-12 rounded-xl shrink-0 shadow-sm border ${
              isEmergency ? 'bg-red-50 border-red-200 text-red-500' : 'bg-surface-container border-border-glass text-primary'
            }`}>
              {isEmergency ? <Zap className="w-6 h-6" /> : <Package className="w-6 h-6" />}
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-headline-sm text-base font-bold text-on-surface">{order.product_name}</h3>
                <span className="font-mono text-[10px] text-on-surface-variant/80 bg-surface-container px-1.5 py-0.5 rounded border border-border-glass">
                  {order.product_sku}
                </span>
              </div>
              <div className="flex items-center gap-2 flex-wrap pt-0.5">
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider border ${cycleStyle.class}`}>
                  {cycleStyle.label}
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider border ${statusStyle.class}`}>
                  {statusStyle.label}
                </span>
                {saving && <span className="text-[10px] font-medium text-on-surface-variant/60 animate-pulse">saving…</span>}
              </div>
            </div>
          </div>

          <div className="text-left md:text-right shrink-0 bg-surface-container-low px-4 py-2 rounded-xl border border-border-glass">
            <div className="flex items-center gap-0.5 justify-start md:justify-end text-primary">
              <IndianRupee className="w-4 h-4" />
              <span className="text-xl font-bold font-mono tracking-tight">{costDisplay}</span>
            </div>
            <p className="text-[10px] font-medium text-on-surface-variant mt-0.5">
              ₹{order.price_per_unit} / {order.unit}
            </p>
          </div>
        </div>

        {/* Body content */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative z-10">
          {/* Left column: Supplier, Qty, Actions */}
          <div className="lg:col-span-5 flex flex-col gap-5">
            {/* Supplier Info */}
            <div className="flex items-center gap-3 p-3 rounded-xl bg-surface-container-low border border-border-glass">
              <div className="w-8 h-8 rounded-lg bg-surface-container-high flex items-center justify-center shrink-0">
                <Truck className="w-4 h-4 text-on-surface-variant" />
              </div>
              <div className="min-w-0">
                <p className="font-semibold text-sm text-on-surface truncate">{order.supplier_name}</p>
                <p className="text-[10px] text-on-surface-variant truncate">{order.supplier_contact}</p>
              </div>
              <div className="ml-auto font-mono text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded">
                {order.supplier_whatsapp}
              </div>
            </div>

            {/* Editable Quantity */}
            <div className="p-4 rounded-xl bg-surface-container-lowest border border-border-glass shadow-sm">
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
                <div className="mt-4 pt-4 border-t border-border-glass">
                  <div className="flex items-center justify-between mb-1.5 px-1">
                    <span className="font-label-xs text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">
                      Owner Note
                    </span>
                    <span className="text-[9px] text-on-surface-variant/50 uppercase tracking-widest">(Optional)</span>
                  </div>
                  <input
                    type="text"
                    className="nexus-input w-full px-3 py-1.5 text-xs rounded-lg"
                    placeholder="Add special instructions for supplier..."
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

            {/* Actions */}
            {isPending && (
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 mt-auto">
                <button
                  id={`btn-approve-${order.id}`}
                  onClick={() => setShowApproval(true)}
                  className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white py-2.5 px-4 rounded-xl font-bold text-xs tracking-wider uppercase transition-colors flex items-center justify-center gap-2 shadow-sm"
                >
                  <Send className="w-4 h-4" /> Approve & Send
                </button>
                <button
                  id={`btn-reject-${order.id}`}
                  onClick={handleReject}
                  className="bg-surface-container-high hover:bg-red-50 text-on-surface hover:text-red-600 border border-border-glass hover:border-red-200 py-2.5 px-4 rounded-xl font-bold text-xs tracking-wider uppercase transition-colors flex items-center justify-center gap-2"
                >
                  <XCircle className="w-4 h-4" /> Reject
                </button>
              </div>
            )}

            {isApproved && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-emerald-50 border border-emerald-200 mt-auto">
                <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                <span className="font-semibold text-emerald-700 text-sm">
                  {order.status === 'sent_whatsapp' ? `WhatsApp dispatched to ${order.supplier_name}` : 'Order approved manually'}
                </span>
              </div>
            )}
          </div>

          {/* Right column: Reasoning */}
          <div className="lg:col-span-7">
            <ReasoningPanel orderId={order.id} reasoning={order.ai_reasoning} />
          </div>
        </div>
      </div>

      {showApproval && (
        <OrderApprovalModal
          order={{ ...order, final_qty: currentQty, total_cost: currentQty * order.price_per_unit }}
          onClose={() => setShowApproval(false)}
          onSent={(updated) => { setShowApproval(false); onUpdated(updated); }}
        />
      )}
    </>
  );
}
