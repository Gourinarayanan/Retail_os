import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Send, Loader2, Sparkles, RefreshCw, Info, BookOpen,
  User, Bot, Trash2, Cpu, Terminal, BrainCircuit,
} from 'lucide-react';
import type { ChatMessage } from '../types';
import { apiGet, apiPost } from '../api/client';

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input,    setInput]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const [fetching, setFetching] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLTextAreaElement>(null);

  const loadHistory = useCallback(async () => {
    setFetching(true);
    try {
      const data = await apiGet<ChatMessage[]>('/chat/history');
      setMessages(data);
    } catch { } finally { setFetching(false); }
  }, []);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

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

  const clearHistory = useCallback(() => {
    if (!window.confirm('Clear chat view? (History stays in DB)')) return;
    setMessages([]);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const PROMPT_SUGGESTIONS = [
    { label: "Run Stock Audit", text: "Show me low stock items. Which supplier has the longest lead time?" },
    { label: "Compare Suppliers", text: "Rank our active suppliers by reliability score. Who should we use for pantry staples?" },
    { label: "Check Security", text: "Is End-to-End Encryption active? Double-check security validation status." }
  ];

  return (
    <div className="space-y-6 animate-fade-in flex flex-col h-[calc(100vh-140px)] min-h-[500px]">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 shrink-0">
        <div className="flex items-center gap-2.5">
          <Terminal className="w-5 h-5 text-primary" />
          <div>
            <h3 className="font-headline-lg text-lg text-on-surface">Nexus copilot console</h3>
            <p className="font-label-xs text-xs text-on-surface-variant uppercase mt-0.5">Dual-Agent Chat Reasoning Engine</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={loadHistory} className="p-2 border border-border-glass rounded-lg text-on-surface-variant hover:text-primary hover:border-primary transition-all">
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={clearHistory}
            disabled={!messages.length}
            className="p-2 px-3 rounded-md bg-surface-container-high border border-border-glass font-label-md text-xs uppercase flex items-center gap-1.5 hover:bg-error/15 hover:text-error transition-all disabled:opacity-40"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear logs</span>
          </button>
        </div>
      </div>

      {/* Main chat layout */}
      <div className="flex-1 min-h-0 glass-panel rounded-xl border border-border-glass flex flex-col justify-between overflow-hidden relative">
        <div className="absolute top-0 right-0 p-4 opacity-5 select-none pointer-events-none">
          <BrainCircuit className="w-96 h-96 text-primary" />
        </div>

        {/* Conversation Logs */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 relative z-10">
          {fetching && messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          )}
          
          {!fetching && messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full gap-5">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center">
                <Cpu className="w-8 h-8 text-primary" />
              </div>
              <div className="text-center">
                <p className="text-sm font-bold text-on-surface">Terminal Ready</p>
                <p className="text-xs text-on-surface-variant mt-1">Awaiting context execution commands.</p>
              </div>
            </div>
          )}

          {messages.map((m, idx) => {
            const isModel = m.role === 'assistant';
            const time = new Date(m.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
            return (
              <div
                key={m.id || idx}
                className={`flex gap-3 max-w-[85%] ${isModel ? 'mr-auto' : 'ml-auto flex-row-reverse'}`}
              >
                <div className={`w-8 h-8 rounded-lg shrink-0 flex items-center justify-center border border-border-glass ${
                  isModel ? 'bg-primary/20 text-primary shadow-sm' : 'bg-surface-container-high text-on-surface-variant'
                }`}>
                  {isModel ? <Cpu className="w-4 h-4" /> : <span className="font-bold text-xs uppercase">US</span>}
                </div>
                <div className={`p-4 rounded-xl border ${
                  isModel
                    ? 'bg-surface-container-low border-border-glass/40 text-on-surface-variant'
                    : 'bg-primary/10 border-primary/40 text-on-surface'
                }`}>
                  <div className="flex justify-between items-center mb-1">
                    <div className="text-xs text-on-surface-variant/50 font-label-xs uppercase tracking-wider">
                      {isModel ? "copilot output" : "executor input"} • {time}
                    </div>
                  </div>
                  <div className="text-sm leading-relaxed whitespace-pre-wrap font-sans text-on-surface">
                    {m.content}
                  </div>
                  {isModel && m.context_used && (
                    <div className="mt-2 text-[10px] text-primary/80 flex items-center gap-1 bg-primary/5 px-2 py-1 rounded w-fit border border-primary/10">
                      <BookOpen className="w-3 h-3" />
                      RAG Sources: {m.context_used}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          
          {loading && (
            <div className="flex gap-3 max-w-[85%] mr-auto">
              <div className="w-8 h-8 rounded-lg shrink-0 flex items-center justify-center border border-border-glass bg-primary/20 text-primary">
                <Cpu className="w-4 h-4" />
              </div>
              <div className="p-4 rounded-xl border bg-surface-container-low border-border-glass/40 text-on-surface-variant">
                <div className="flex items-center gap-2 font-label-md text-xs tracking-wider animate-pulse text-primary">
                  <Sparkles className="w-3.5 h-3.5 animate-spin" />
                  <span>Computing analytical response vectors...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Textbox segment */}
        <div className="p-4 bg-surface-container/60 border-t border-border-glass relative z-10 shrink-0">
          <div className="flex flex-wrap gap-2.5 mb-3.5">
            {PROMPT_SUGGESTIONS.map((pr, i) => (
              <button
                key={i}
                onClick={() => sendMessage(pr.text)}
                disabled={loading}
                className="px-3 py-1.5 rounded-full border border-border-glass text-[10px] font-label-xs uppercase tracking-wider text-on-surface-variant/80 hover:border-primary hover:text-primary bg-surface-container-low transition-all"
              >
                {pr.label}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
              }}
              onKeyDown={handleKeyDown}
              disabled={loading}
              placeholder="Query safety bounds, re-order weights, or system metadata..."
              className="nexus-input flex-1 px-4 py-2.5 rounded-lg text-sm resize-none overflow-hidden h-10"
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={loading || !input.trim()}
              className="px-4 py-2.5 bg-primary text-on-primary rounded-lg hover:bg-primary-fixed transition-all disabled:opacity-30 flex items-center justify-center"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
