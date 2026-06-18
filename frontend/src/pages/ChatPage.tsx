import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Send, Loader2, Sparkles, RefreshCw, Info, BookOpen,
  User, Bot, Trash2
} from 'lucide-react';
import type { ChatMessage } from '../types';
import { apiGet, apiPost } from '../api/client';

// ── Message bubble ────────────────────────────────────────────────────────────

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user';
  const time   = new Date(msg.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

  const renderContent = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, i) => {
      if (line.startsWith('## '))
        return <p key={i} className="font-bold text-sm mt-2 mb-1" style={{ color: 'var(--text-primary)' }}>{line.slice(3)}</p>;
      if (line.startsWith('### '))
        return <p key={i} className="font-semibold text-xs uppercase tracking-wider mt-2" style={{ color: '#93c5fd' }}>{line.slice(4)}</p>;
      if (line.startsWith('- ') || line.startsWith('* '))
        return (
          <div key={i} className="flex items-start gap-2">
            <span className="mt-1.5 w-1 h-1 rounded-full shrink-0" style={{ background: '#3b82f6' }} />
            <span>{line.slice(2)}</span>
          </div>
        );
      if (line.startsWith('**') && line.endsWith('**'))
        return <p key={i} className="font-semibold">{line.replace(/\*\*/g, '')}</p>;
      if (!line.trim()) return <div key={i} className="h-1.5" />;
      return <p key={i}>{line}</p>;
    });
  };

  return (
    <div
      className={`flex gap-3 stream-item ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div
        className="flex h-8 w-8 items-center justify-center rounded-full shrink-0 mt-1"
        style={{
          background: isUser
            ? 'linear-gradient(135deg,#3b82f6,#8b5cf6)'
            : 'rgba(139,92,246,0.15)',
          border: isUser ? 'none' : '1px solid rgba(139,92,246,0.3)',
        }}
      >
        {isUser
          ? <User size={14} className="text-white" />
          : <Sparkles size={14} style={{ color: '#c4b5fd' }} />
        }
      </div>

      {/* Bubble */}
      <div
        className="flex flex-col gap-1.5 max-w-[75%]"
        style={{ alignItems: isUser ? 'flex-end' : 'flex-start' }}
      >
        <div
          className="rounded-2xl px-4 py-3 text-sm leading-relaxed flex flex-col gap-0.5"
          style={{
            background: isUser
              ? 'rgba(59,130,246,0.2)'
              : 'var(--bg-card)',
            border: isUser
              ? '1px solid rgba(59,130,246,0.3)'
              : '1px solid var(--border)',
            color: 'var(--text-secondary)',
            borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
          }}
        >
          {renderContent(msg.content)}
        </div>

        {/* Footer: time + RAG source */}
        <div className={`flex items-center gap-2 ${isUser ? 'flex-row-reverse' : ''}`}>
          <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{time}</span>
          {!isUser && msg.context_used && (
            <div
              className="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded"
              style={{ background: 'rgba(139,92,246,0.08)', color: '#c4b5fd', border: '1px solid rgba(139,92,246,0.15)' }}
              title={`RAG context: ${msg.context_used}`}
            >
              <BookOpen size={9} />
              <span className="truncate max-w-[180px]">{msg.context_used}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Typing indicator ──────────────────────────────────────────────────────────

function TypingIndicator() {
  return (
    <div className="flex gap-3 stream-item">
      <div className="flex h-8 w-8 items-center justify-center rounded-full shrink-0"
        style={{ background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.3)' }}>
        <Sparkles size={14} style={{ color: '#c4b5fd' }} />
      </div>
      <div className="flex items-center gap-1.5 px-4 py-3 rounded-2xl"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '18px 18px 18px 4px' }}>
        {[0, 1, 2].map((i) => (
          <div key={i} className="w-1.5 h-1.5 rounded-full"
            style={{ background: '#8b5cf6', animation: `pulse-dot 1.2s ease-in-out ${i * 0.2}s infinite` }} />
        ))}
      </div>
    </div>
  );
}

// ── Suggestion chips ──────────────────────────────────────────────────────────

const SUGGESTIONS = [
  'What should I stock before Onam?',
  'Which supplier is best for spices?',
  'How should I handle a hartal tomorrow?',
  'Which products are near expiry?',
  'What are today\'s critical stock alerts?',
  'How do I maximise profit this festival season?',
];

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input,    setInput]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const [fetching, setFetching] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLTextAreaElement>(null);

  // ── Load history ─────────────────────────────────────────────────────
  const loadHistory = useCallback(async () => {
    setFetching(true);
    try {
      const data = await apiGet<ChatMessage[]>('/chat/history');
      setMessages(data);
    } catch {/* silent */} finally { setFetching(false); }
  }, []);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  // ── Auto-scroll ──────────────────────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // ── Send message ─────────────────────────────────────────────────────
  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    // Optimistic user message
    const optimistic: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: trimmed,
      context_used: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimistic]);
    setInput('');
    setLoading(true);

    try {
      // Backend: POST /api/chat { content: str } → { reply: str, sources: str }
      const result = await apiPost<{ reply: string; sources: string }>('/chat', { content: trimmed });
      const assistantMsg: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: result.reply,
        context_used: result.sources || null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please check that the backend is running and Gemini API key is set.',
          context_used: null,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [loading]);

  // ── Clear history (client-side only — no backend DELETE endpoint) ───────────
  const clearHistory = useCallback(() => {
    if (!window.confirm('Clear chat view? (History stays in DB)')) return;
    setMessages([]);
  }, []);

  // ── Keyboard handler ─────────────────────────────────────────────────
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="page-enter flex flex-col h-full" style={{ height: 'calc(100vh - 56px - 48px)' }}>

      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>AI Assistant</h1>
          <div className="flex items-center gap-2 mt-1">
            <span className="dot-green dot-pulse" />
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              Gemini Flash · RAG-powered · knows your store's context
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={loadHistory} className="btn-ghost p-2" title="Refresh history">
            <RefreshCw size={14} />
          </button>
          <button onClick={clearHistory} disabled={!messages.length}
            className="btn-ghost p-2 disabled:opacity-40" title="Clear chat">
            <Trash2 size={14} style={{ color: '#f87171' }} />
          </button>
        </div>
      </div>

      {/* ── Chat window ─────────────────────────────────────────────── */}
      <div
        className="flex-1 overflow-y-auto scroll-panel rounded-xl p-4 flex flex-col gap-4 mb-4"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', minHeight: 0 }}
      >
        {/* Empty state */}
        {!fetching && messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-5 py-8">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl"
              style={{ background: 'linear-gradient(135deg,rgba(59,130,246,0.15),rgba(139,92,246,0.15))', border: '1px solid rgba(139,92,246,0.2)' }}>
              <Bot size={28} style={{ color: '#c4b5fd' }} />
            </div>
            <div className="text-center">
              <p className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
                Good morning! I'm your RetailWise AI
              </p>
              <p className="text-sm mt-1 max-w-sm" style={{ color: 'var(--text-muted)' }}>
                Ask me about stock levels, suppliers, festival demand, hartal planning, or any retail decision.
              </p>
            </div>

            {/* Suggestion chips */}
            <div className="flex flex-wrap justify-center gap-2 max-w-lg">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="text-xs px-3 py-2 rounded-xl transition-all"
                  style={{
                    background: 'rgba(59,130,246,0.08)',
                    border: '1px solid rgba(59,130,246,0.2)',
                    color: '#93c5fd',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(59,130,246,0.15)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(59,130,246,0.08)')}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Fetching skeleton */}
        {fetching && (
          <div className="flex flex-col gap-4">
            {[0, 1].map((i) => (
              <div key={i} className={`flex gap-3 ${i % 2 === 1 ? 'flex-row-reverse' : ''}`}>
                <div className="skeleton w-8 h-8 rounded-full shrink-0" />
                <div className="skeleton rounded-2xl h-12 flex-1 max-w-[60%]" />
              </div>
            ))}
          </div>
        )}

        {/* Messages */}
        {!fetching && messages.map((msg) => (
          <MessageBubble key={msg.id} msg={msg} />
        ))}

        {/* Typing indicator */}
        {loading && <TypingIndicator />}

        <div ref={bottomRef} />
      </div>

      {/* ── Suggestion chips (contextual, when has messages) ─────── */}
      {messages.length > 0 && !loading && (
        <div className="flex gap-2 mb-3 overflow-x-auto pb-1 shrink-0">
          {SUGGESTIONS.slice(0, 4).map((s) => (
            <button
              key={s}
              onClick={() => sendMessage(s)}
              className="text-[11px] px-3 py-1.5 rounded-xl whitespace-nowrap shrink-0 transition-all"
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                color: 'var(--text-secondary)',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(59,130,246,0.4)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border)')}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* ── Input bar ───────────────────────────────────────────────── */}
      <div
        className="flex items-end gap-3 rounded-xl px-4 py-3 shrink-0"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-bright)' }}
      >
        <textarea
          ref={inputRef}
          id="chat-input"
          rows={1}
          className="flex-1 resize-none bg-transparent outline-none text-sm leading-relaxed"
          style={{ color: 'var(--text-primary)', maxHeight: 120 }}
          placeholder="Ask about stock, suppliers, festivals, hartal… (Enter to send)"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            // Auto-grow
            e.target.style.height = 'auto';
            e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
          }}
          onKeyDown={handleKeyDown}
          disabled={loading}
          aria-label="Chat message input"
        />
        <button
          id="btn-send-chat"
          onClick={() => sendMessage(input)}
          disabled={loading || !input.trim()}
          className="btn-primary shrink-0 h-9 w-9 p-0 flex items-center justify-center rounded-xl disabled:opacity-40 disabled:cursor-not-allowed disabled:transform-none"
          aria-label="Send message"
        >
          {loading
            ? <Loader2 size={15} className="animate-spin" />
            : <Send size={15} />
          }
        </button>
      </div>

      {/* Info footnote */}
      <p className="text-[10px] text-center mt-2 shrink-0" style={{ color: 'var(--text-muted)' }}>
        <Info size={9} className="inline mr-1" />
        Answers draw from your live inventory, today's briefing, and the RAG knowledge base.
      </p>
    </div>
  );
}
