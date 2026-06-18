import React, { useState, useEffect, useRef } from 'react';
import { X, Send, CheckCircle2, Loader2, MessageSquare, Phone, IndianRupee, Package } from 'lucide-react';
import toast from 'react-hot-toast';
import type { Order } from '../../types';
import { apiPost } from '../../api/client';

interface OrderApprovalModalProps {
  order:   Order;
  onClose: () => void;
  onSent:  (updated: Order) => void;
}

export default function OrderApprovalModal({ order, onClose, onSent }: OrderApprovalModalProps) {
  const [sending, setSending] = useState(false);
  const [sent,    setSent]    = useState(false);
  const backdropRef = useRef<HTMLDivElement>(null);

  // ── Close on Escape ───────────────────────────────────────────────────
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  // ── Lock body scroll ──────────────────────────────────────────────────
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  // ── Send ──────────────────────────────────────────────────────────────
  const handleSend = async () => {
    setSending(true);
    try {
      const result = await apiPost<{ order: Order; whatsapp_sent: boolean; message: string }>(
        `/orders/${order.id}/approve`
      );

      setSent(true);
      const supplierName = order.supplier_name;

      if (result.whatsapp_sent) {
        toast.success(
          `WhatsApp sent to ${supplierName}! 🎉`,
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
      } else {
        toast('Order approved — WhatsApp send failed. Check Twilio config.', {
          icon: '⚠️',
          duration: 5000,
        });
      }

      // Short delay so user sees sent state before modal closes
      setTimeout(() => onSent(result.order), 800);
    } catch {
      /* toast by interceptor */
    } finally {
      setSending(false);
    }
  };

  // ── Format WhatsApp preview ───────────────────────────────────────────
  const whatsapp = order.whatsapp_message || `Order for ${order.product_name}: ${Math.round(order.final_qty)} ${order.unit}s from ${order.supplier_name}`;

  return (
    /* Backdrop */
    <div
      ref={backdropRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)' }}
      onClick={(e) => { if (e.target === backdropRef.current) onClose(); }}
      role="dialog"
      aria-modal="true"
      aria-label="Order approval"
    >
      <div
        className="relative w-full max-w-lg flex flex-col gap-0 rounded-2xl overflow-hidden"
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-bright)',
          boxShadow: '0 24px 64px rgba(0,0,0,0.6)',
          maxHeight: '90vh',
        }}
      >
        {/* ── Modal header ─────────────────────────────────────── */}
        <div
          className="flex items-center justify-between px-5 py-4"
          style={{ borderBottom: '1px solid var(--border)' }}
        >
          <div className="flex items-center gap-2">
            <div
              className="flex h-8 w-8 items-center justify-center rounded-lg"
              style={{ background: 'rgba(52,211,153,0.1)' }}
            >
              <MessageSquare size={16} style={{ color: '#34d399' }} />
            </div>
            <div>
              <p className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>
                Approve Order
              </p>
              <p className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
                Review and send via WhatsApp
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex h-7 w-7 items-center justify-center rounded-lg transition-colors"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--border)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            aria-label="Close modal"
          >
            <X size={15} />
          </button>
        </div>

        {/* ── Order summary ─────────────────────────────────────── */}
        <div
          className="px-5 py-4 flex flex-col gap-3"
          style={{ borderBottom: '1px solid var(--border)' }}
        >
          {/* Product row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Package size={14} style={{ color: '#60a5fa' }} />
              <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                {order.product_name}
              </span>
              <span className="mono text-[11px]" style={{ color: 'var(--text-muted)' }}>
                {order.product_sku}
              </span>
            </div>
            <span className={`badge-${order.order_cycle === 'emergency' ? 'red' : 'blue'}`}>
              {order.order_cycle}
            </span>
          </div>

          {/* Quantity + Cost grid */}
          <div className="grid grid-cols-3 gap-2">
            {[
              { label: 'Quantity', value: `${Math.round(order.final_qty)} ${order.unit}s`,   color: 'var(--text-primary)' },
              { label: 'Unit Price', value: `₹${order.price_per_unit}/${order.unit}`,         color: 'var(--text-secondary)' },
              { label: 'Total Cost', value: `₹${Math.round(order.total_cost).toLocaleString('en-IN')}`, color: '#6ee7b7' },
            ].map(({ label, value, color }) => (
              <div
                key={label}
                className="flex flex-col gap-0.5 rounded-lg px-3 py-2"
                style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
              >
                <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{label}</span>
                <span className="text-sm font-bold mono" style={{ color }}>{value}</span>
              </div>
            ))}
          </div>

          {/* Supplier */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
              <Phone size={11} />
              <span>{order.supplier_name}</span>
              <span style={{ color: 'var(--text-muted)' }}>· {order.supplier_contact}</span>
            </div>
            <span className="mono" style={{ color: '#60a5fa' }}>
              {order.supplier_whatsapp}
            </span>
          </div>

          {/* Owner modification warning */}
          {order.owner_modified && (
            <div
              className="rounded-lg px-3 py-2 text-xs flex items-center gap-2"
              style={{
                background: 'rgba(245,158,11,0.08)',
                border: '1px solid rgba(245,158,11,0.2)',
                color: '#fcd34d',
              }}
            >
              ✏️ Quantity modified by owner ({Math.round(order.ai_recommended_qty)} AI → {Math.round(order.final_qty)} final)
            </div>
          )}
        </div>

        {/* ── WhatsApp message preview ──────────────────────────── */}
        <div className="px-5 py-4 overflow-y-auto flex flex-col gap-2" style={{ maxHeight: '260px' }}>
          <p className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
            WhatsApp Message Preview
          </p>
          <div
            className="rounded-xl px-4 py-3 text-xs leading-relaxed font-mono whitespace-pre-wrap"
            style={{
              background: '#0e1921',
              border: '1px solid rgba(37,211,102,0.2)',
              color: '#e2e8f0',
              borderRadius: '12px 12px 12px 4px',
            }}
          >
            {whatsapp}
          </div>
          <p className="text-[10px] text-right" style={{ color: 'var(--text-muted)' }}>
            Will be sent to {order.supplier_whatsapp} via Twilio
          </p>
        </div>

        {/* ── Footer actions ────────────────────────────────────── */}
        <div
          className="flex items-center justify-between px-5 py-4"
          style={{ borderTop: '1px solid var(--border)' }}
        >
          <button onClick={onClose} className="btn-ghost text-sm">
            Cancel
          </button>

          {sent ? (
            <div className="flex items-center gap-2" style={{ color: '#34d399' }}>
              <CheckCircle2 size={16} />
              <span className="text-sm font-semibold">Sent!</span>
            </div>
          ) : (
            <button
              id={`btn-modal-send-${order.id}`}
              onClick={handleSend}
              disabled={sending}
              className="btn-success text-sm disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              aria-label="Confirm and send WhatsApp order"
            >
              {sending ? (
                <><Loader2 size={14} className="animate-spin" /> Sending…</>
              ) : (
                <><Send size={14} /> Confirm &amp; Send WhatsApp</>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
