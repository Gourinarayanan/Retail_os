import React, { useState, useEffect, useRef } from 'react';
import { X, CheckCircle2, Loader2, MessageCircle, Package, ArrowRight, ShieldCheck, AlertTriangle } from 'lucide-react';
import type { Order } from '../../types';

interface OrderApprovalModalProps {
  order: Order;
  onClose: () => void;
  onSent: (updated: Order) => void;
}

export default function OrderApprovalModal({ order, onClose, onSent }: OrderApprovalModalProps) {
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const backdropRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);



  const handleSend = async () => {
    setSending(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    setSent(true);
    setTimeout(() => {
      onSent({ ...order, status: 'sent_whatsapp' });
    }, 2500);
  };

  const whatsapp = order.whatsapp_message || `Order for ${order.product_name}: ${Math.round(order.final_qty)} ${order.unit}s from ${order.supplier_name}`;

  return (
    <div
      ref={backdropRef}
      className="fixed inset-0 z-[100] flex items-center sm:justify-center p-4 sm:p-6 overflow-y-auto"
      style={{
        background: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(16px)',
        animation: 'fadeIn 0.3s ease-out'
      }}
      onClick={(e) => { if (e.target === backdropRef.current) onClose(); }}
    >
      <div
        className="relative w-full max-w-[420px] flex flex-col rounded-[28px] overflow-hidden shadow-2xl transition-all duration-500 transform scale-100 my-auto mx-auto"
        style={{
          background: 'linear-gradient(180deg, #1A1A1A 0%, #0D0D0D 100%)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: '0 40px 80px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.1)',
        }}
      >
        {/* Glow effect */}
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-[#25D366] rounded-full blur-[120px] opacity-20 pointer-events-none"></div>

        {sent ? (
           // SUCCESS STATE
           <div className="flex flex-col items-center justify-center p-12 text-center animate-in fade-in zoom-in duration-500" style={{ height: '460px' }}>
             <div className="relative mb-8">
               <div className="absolute inset-0 bg-[#25D366] rounded-full animate-ping opacity-30" style={{ animationDuration: '2s' }}></div>
               <div className="w-28 h-28 rounded-full bg-gradient-to-tr from-[#128C7E] to-[#25D366] flex items-center justify-center shadow-[0_0_60px_rgba(37,211,102,0.4)] relative z-10 transform scale-100">
                 <CheckCircle2 size={56} color="white" strokeWidth={2.5} />
               </div>
             </div>
             <h2 className="text-[28px] font-bold text-white mb-3 tracking-tight">Sent Successfully</h2>
             <p className="text-[15px] text-gray-400 max-w-[260px] leading-relaxed">
               Order securely dispatched to <span className="text-[#25D366] font-semibold">{order.supplier_name}</span> via WhatsApp.
             </p>
           </div>
        ) : (
          <div className="animate-in fade-in duration-300">
            {/* HEADER */}
            <div className="flex items-center justify-between px-7 py-6 border-b border-white/5 relative z-10">
              <div className="flex items-center gap-4">
                <div className="w-11 h-11 rounded-full bg-gradient-to-br from-[#25D366] to-[#128C7E] flex items-center justify-center shadow-lg shadow-[#25D366]/25">
                  <MessageCircle size={22} color="white" />
                </div>
                <div>
                  <h3 className="text-white font-bold text-[19px] tracking-tight leading-none mb-1">Confirm Order</h3>
                  <p className="text-[13px] text-gray-400 font-medium">WhatsApp Dispatch</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X size={16} />
              </button>
            </div>

            {/* BODY */}
            <div className="p-7 flex flex-col gap-6 relative z-10 overflow-y-auto max-h-[50vh] sm:max-h-[60vh] custom-scrollbar">
              {/* Order Details Card */}
              <div className="bg-white/[0.02] border border-white/5 rounded-[20px] p-5 flex flex-col gap-4 shadow-inner">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3.5">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center border border-white/5">
                      <Package size={20} className="text-blue-400" />
                    </div>
                    <div>
                      <p className="text-white font-semibold text-[15px] leading-tight mb-0.5">{order.product_name}</p>
                      <p className="text-[12px] text-gray-500 font-mono">{order.product_sku}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-bold text-[20px] leading-tight mb-0.5">₹{Math.round(order.total_cost).toLocaleString('en-IN')}</p>
                    <p className="text-[11px] text-gray-500 font-medium uppercase tracking-wider">{Math.round(order.final_qty)} {order.unit}s @ ₹{order.price_per_unit}</p>
                  </div>
                </div>

                <div className="h-px bg-white/5 w-full"></div>

                <div className="flex items-center justify-between text-[13px]">
                  <div className="flex items-center gap-2 text-gray-400 font-medium">
                    <ShieldCheck size={16} className="text-[#25D366]" />
                    <span>{order.supplier_name}</span>
                  </div>
                  <span className="font-mono text-[#25D366] bg-[#25D366]/10 px-2.5 py-1 rounded-md font-medium">
                    {order.supplier_whatsapp}
                  </span>
                </div>
              </div>

              {/* Authentic WhatsApp Bubble */}
              <div className="flex flex-col gap-2.5">
                <p className="text-[11px] text-gray-500 uppercase tracking-widest pl-1 font-bold">Message Preview</p>
                <div className="relative bg-[#0b141a] rounded-[20px] p-5 border border-white/5 overflow-hidden shadow-inner">
                  {/* Subtle chat background pattern */}
                  <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'url("https://static.whatsapp.net/rsrc.php/v3/yO/r/FsWUqsWZgEu.png")' }}></div>
                  
                  <div className="relative flex justify-end">
                    <div className="relative bg-[#005c4b] text-[#e9edef] rounded-2xl rounded-tr-sm px-3.5 pt-2.5 pb-1.5 max-w-[92%] shadow-md text-[14.5px] leading-[1.4]">
                      {/* Tail */}
                      <div className="absolute top-0 -right-[9px] w-0 h-0 border-t-[0px] border-t-transparent border-b-[14px] border-b-transparent border-l-[12px] border-l-[#005c4b]"></div>
                      
                      <div className="whitespace-pre-wrap pb-3 font-sans">{whatsapp}</div>
                      
                      <div className="absolute bottom-1 right-2 flex items-center gap-1 text-[10.5px] text-white/60 font-medium">
                        {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        <svg viewBox="0 0 16 15" width="16" height="15" className="text-[#53bdeb]">
                          <path fill="currentColor" d="M15.01 3.316l-.478-.372a.365.365 0 0 0-.51.063L8.666 9.879a.32.32 0 0 1-.484.033l-.358-.325a.319.319 0 0 0-.484.032l-.378.483a.418.418 0 0 0 .036.541l1.32 1.266c.143.14.361.125.484-.033l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.879a.32.32 0 0 1-.484.033L1.891 7.769a.366.366 0 0 0-.515.006l-.423.433a.364.364 0 0 0 .006.514l3.258 3.185c.143.14.361.125.484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* FOOTER */}
            <div className="p-7 pt-1 relative z-10">
              <div className="mb-4 bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 flex items-start gap-3">
                <div className="bg-amber-500/20 p-1.5 rounded-lg shrink-0">
                  <AlertTriangle size={16} className="text-amber-500" />
                </div>
                <div>
                  <p className="text-amber-500 text-[13px] font-bold tracking-tight mb-0.5">Demo Mode Active</p>
                  <p className="text-amber-500/80 text-[11px] leading-snug">
                    WhatsApp integration is simulated for this hackathon prototype. No real messages are sent.
                  </p>
                </div>
              </div>
              <button
                onClick={handleSend}
                disabled={sending}
                className="w-full bg-[#25D366] hover:bg-[#22C55E] text-[#0A0A0A] font-bold text-[16px] py-4 rounded-[16px] transition-all flex items-center justify-center gap-2.5 shadow-[0_8px_24px_rgba(37,211,102,0.25)] hover:shadow-[0_12px_32px_rgba(37,211,102,0.4)] hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none group"
              >
                {sending ? (
                  <><Loader2 size={20} className="animate-spin text-[#0A0A0A]" /> Transmitting via WhatsApp...</>
                ) : (
                  <>Send via WhatsApp <ArrowRight size={20} className="group-hover:translate-x-1.5 transition-transform duration-300" /></>
                )}
              </button>
              <p className="text-center text-[12px] text-gray-500 mt-4 font-medium flex justify-center items-center gap-1.5">
                <ShieldCheck size={14} /> End-to-end encrypted
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
