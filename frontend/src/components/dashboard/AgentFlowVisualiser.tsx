import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Loader2, CheckCircle2, XCircle, Clock, Sparkles, ChevronRight } from 'lucide-react';
import { streamBriefing } from '../../api/client';
import type { AgentLogEntry, AgentName, SSECompleteEvent } from '../../types';

// ── Agent pipeline config ─────────────────────────────────────────────────────

interface AgentConfig {
  id:       AgentName;
  label:    string;
  icon:     string;
  color:    string;
  bgColor:  string;
}

const AGENTS: AgentConfig[] = [
  { id: 'context',     label: 'Context',     icon: '🌤️',  color: '#60a5fa', bgColor: 'rgba(59,130,246,0.12)' },
  { id: 'scenario',    label: 'Scenario',    icon: '🎯',  color: '#c4b5fd', bgColor: 'rgba(139,92,246,0.12)' },
  { id: 'forecast',    label: 'Forecast',    icon: '📈',  color: '#34d399', bgColor: 'rgba(52,211,153,0.12)' },
  { id: 'inventory',   label: 'Inventory',   icon: '📦',  color: '#fbbf24', bgColor: 'rgba(251,191,36,0.12)' },
  { id: 'supplier',    label: 'Supplier',    icon: '🚛',  color: '#f87171', bgColor: 'rgba(248,113,113,0.12)' },
  { id: 'opportunity', label: 'Opportunity', icon: '💡',  color: '#fb923c', bgColor: 'rgba(251,146,60,0.12)' },
  { id: 'briefing',    label: 'Briefing',    icon: '✨',  color: '#e879f9', bgColor: 'rgba(232,121,249,0.12)' },
];

type NodeStatus = 'idle' | 'running' | 'complete' | 'error';

interface NodeState {
  status:    NodeStatus;
  summary:   string;
  elapsed:   number | null;   // ms
  startedAt: number | null;   // Date.now()
}

const INITIAL_NODES: Record<string, NodeState> = Object.fromEntries(
  AGENTS.map((a) => [a.id, { status: 'idle', summary: '', elapsed: null, startedAt: null }])
);

// ── Animated connector ────────────────────────────────────────────────────────

function Connector({ active }: { active: boolean }) {
  return (
    <div className="flex items-center shrink-0" style={{ width: 28 }}>
      <div
        className="h-0.5 w-full transition-all duration-500"
        style={{
          background: active
            ? 'linear-gradient(90deg, #3b82f6, #8b5cf6)'
            : 'var(--border)',
          boxShadow: active ? '0 0 6px rgba(59,130,246,0.5)' : 'none',
        }}
      />
      <ChevronRight
        size={12}
        style={{
          color: active ? '#60a5fa' : 'var(--text-muted)',
          marginLeft: -6,
          transition: 'color 0.3s',
        }}
      />
    </div>
  );
}

// ── Agent Node Box ────────────────────────────────────────────────────────────

function AgentNode({
  agent,
  state,
}: {
  agent:  AgentConfig;
  state:  NodeState;
}) {
  const isRunning  = state.status === 'running';
  const isComplete = state.status === 'complete';
  const isError    = state.status === 'error';
  const isIdle     = state.status === 'idle';

  const borderColor = isRunning  ? agent.color
                    : isComplete ? agent.color
                    : isError    ? '#f43f5e'
                    : 'var(--border)';

  const bgColor = isRunning  ? agent.bgColor
                : isComplete ? agent.bgColor.replace('0.12', '0.06')
                : isError    ? 'rgba(244,63,94,0.08)'
                : 'var(--bg-card)';

  const glowStyle = isRunning
    ? { boxShadow: `0 0 16px ${agent.color}40` }
    : isComplete
    ? { boxShadow: `0 0 8px ${agent.color}25` }
    : {};

  return (
    <div
      className="flex flex-col items-center gap-2 transition-all duration-400"
      style={{ minWidth: 82 }}
    >
      {/* Box */}
      <div
        className="relative flex flex-col items-center gap-1 rounded-xl px-3 py-3 w-full text-center transition-all duration-400"
        style={{
          background:   bgColor,
          border:       `1.5px solid ${borderColor}`,
          opacity:      isIdle ? 0.45 : 1,
          transform:    isRunning ? 'scale(1.04)' : 'scale(1)',
          ...glowStyle,
        }}
      >
        {/* Pulse ring when running */}
        {isRunning && (
          <span
            className="absolute inset-0 rounded-xl animate-ping"
            style={{ border: `1.5px solid ${agent.color}`, opacity: 0.3 }}
          />
        )}

        {/* Status icon overlay */}
        <div className="absolute -top-2 -right-2">
          {isRunning  && <Loader2 size={14} style={{ color: agent.color }} className="animate-spin" />}
          {isComplete && <CheckCircle2 size={14} style={{ color: '#10b981' }} />}
          {isError    && <XCircle size={14} style={{ color: '#f43f5e' }} />}
        </div>

        {/* Emoji icon */}
        <span className="text-lg leading-none">{agent.icon}</span>

        {/* Label */}
        <span
          className="text-[11px] font-semibold leading-tight"
          style={{ color: isIdle ? 'var(--text-muted)' : 'var(--text-primary)' }}
        >
          {agent.label}
        </span>

        {/* Elapsed */}
        {state.elapsed !== null && (
          <span className="flex items-center gap-0.5 text-[10px] mono" style={{ color: 'var(--text-muted)' }}>
            <Clock size={8} />
            {(state.elapsed / 1000).toFixed(1)}s
          </span>
        )}

        {/* Running indicator */}
        {isRunning && state.startedAt && (
          <LiveElapsed startedAt={state.startedAt} color={agent.color} />
        )}
      </div>

      {/* Summary tooltip on hover */}
      {state.summary && !isIdle && (
        <p
          className="text-[10px] text-center leading-snug px-1 max-w-[90px]"
          style={{ color: 'var(--text-muted)' }}
          title={state.summary}
        >
          {state.summary.slice(0, 40)}{state.summary.length > 40 ? '…' : ''}
        </p>
      )}
    </div>
  );
}

// Live elapsed timer (updates every 100ms while running)
function LiveElapsed({ startedAt, color }: { startedAt: number; color: string }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setElapsed(Date.now() - startedAt), 100);
    return () => clearInterval(id);
  }, [startedAt]);

  return (
    <span className="text-[10px] mono" style={{ color }}>
      {(elapsed / 1000).toFixed(1)}s
    </span>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

interface AgentFlowVisualiserProps {
  onComplete?: () => void;  // callback when pipeline finishes — parent refetches briefing
}

export default function AgentFlowVisualiser({ onComplete }: AgentFlowVisualiserProps) {
  const [running,    setRunning]    = useState(false);
  const [nodes,      setNodes]      = useState<Record<string, NodeState>>(INITIAL_NODES);
  const [summary,    setSummary]    = useState<SSECompleteEvent | null>(null);
  const [error,      setError]      = useState<string | null>(null);
  const [totalTime,  setTotalTime]  = useState<number | null>(null);
  const startTimeRef = useRef<number | null>(null);

  // ── Reset ─────────────────────────────────────────────────────────────
  const reset = useCallback(() => {
    setNodes(INITIAL_NODES);
    setSummary(null);
    setError(null);
    setTotalTime(null);
    startTimeRef.current = null;
  }, []);

  // ── Handle SSE entries ────────────────────────────────────────────────
  const handleEntry = useCallback((raw: object) => {
    const entry = raw as AgentLogEntry;
    const { agent, status, summary: msg, ts } = entry;

    setNodes((prev) => {
      const node = prev[agent] ?? { status: 'idle', summary: '', elapsed: null, startedAt: null };

      if (status === 'started') {
        return { ...prev, [agent]: { status: 'running', summary: msg, startedAt: Date.now(), elapsed: null } };
      }
      if (status === 'complete') {
        const elapsed = node.startedAt ? Date.now() - node.startedAt : null;
        return { ...prev, [agent]: { status: 'complete', summary: msg, elapsed, startedAt: node.startedAt } };
      }
      if (status === 'error') {
        const elapsed = node.startedAt ? Date.now() - node.startedAt : null;
        return { ...prev, [agent]: { status: 'error', summary: msg, elapsed, startedAt: node.startedAt } };
      }
      return prev;
    });
  }, []);

  // ── Handle complete ───────────────────────────────────────────────────
  const handleComplete = useCallback((raw: object) => {
    const data = raw as SSECompleteEvent;
    setSummary(data);
    setRunning(false);
    if (startTimeRef.current) {
      setTotalTime(Date.now() - startTimeRef.current);
    }
    onComplete?.();
  }, [onComplete]);

  // ── Handle error ──────────────────────────────────────────────────────
  const handleError = useCallback((err: Error) => {
    setError(err.message);
    setRunning(false);
  }, []);

  // ── Start pipeline ────────────────────────────────────────────────────
  const startPipeline = useCallback(async () => {
    reset();
    setRunning(true);
    startTimeRef.current = Date.now();
    await streamBriefing(handleEntry, handleComplete, handleError);
  }, [reset, handleEntry, handleComplete, handleError]);

  // ── Which agent index is running/last completed ────────────────────────
  const lastActiveIdx = AGENTS.findIndex(
    (a) => nodes[a.id]?.status === 'running'
  );
  const completedSet = new Set(
    AGENTS.filter((a) => nodes[a.id]?.status === 'complete').map((a) => a.id)
  );

  return (
    <div className="card flex flex-col gap-5">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            Agent Pipeline
          </h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
            7 AI agents running in sequence
          </p>
        </div>
        <button
          id="btn-run-briefing"
          onClick={startPipeline}
          disabled={running}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          aria-label="Run morning briefing pipeline"
        >
          {running
            ? <><Loader2 size={14} className="animate-spin" /> Running…</>
            : <><Play size={14} /> Run Briefing</>
          }
        </button>
      </div>

      {/* ── Flow ───────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between overflow-x-auto pb-1">
        {AGENTS.map((agent, idx) => (
          <React.Fragment key={agent.id}>
            <AgentNode agent={agent} state={nodes[agent.id]} />
            {idx < AGENTS.length - 1 && (
              <Connector
                active={
                  completedSet.has(agent.id) ||
                  (lastActiveIdx > idx)
                }
              />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* ── Error ──────────────────────────────────────────────────── */}
      {error && (
        <div
          className="rounded-lg px-4 py-3 text-sm flex items-center gap-2"
          style={{ background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.25)', color: '#fda4af' }}
        >
          <XCircle size={14} /> Pipeline error: {error}
        </div>
      )}

      {/* ── Complete summary ────────────────────────────────────────── */}
      {summary && (
        <div
          className="stream-item rounded-xl px-4 py-4 flex flex-col gap-3"
          style={{
            background: 'rgba(16,185,129,0.06)',
            border: '1px solid rgba(16,185,129,0.2)',
          }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={15} style={{ color: '#10b981' }} />
              <span className="text-sm font-semibold" style={{ color: '#6ee7b7' }}>
                Briefing Complete
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--text-muted)' }}>
              {totalTime && (
                <span className="mono">{(totalTime / 1000).toFixed(1)}s total</span>
              )}
              <span>{summary.orders_count} orders</span>
              <span>{summary.opportunities_count} opportunities</span>
            </div>
          </div>

          {/* Brief preview */}
          {summary.brief_preview && (
            <div
              className="rounded-lg px-3 py-2.5 text-xs leading-relaxed"
              style={{
                background: 'rgba(0,0,0,0.2)',
                color: 'var(--text-secondary)',
                borderLeft: '2px solid rgba(139,92,246,0.5)',
              }}
            >
              <Sparkles size={11} className="inline mr-1.5" style={{ color: '#c4b5fd' }} />
              {summary.brief_preview}…
            </div>
          )}
        </div>
      )}

      {/* ── Idle state hint ─────────────────────────────────────────── */}
      {!running && !summary && !error && (
        <p className="text-xs text-center" style={{ color: 'var(--text-muted)' }}>
          Click <strong>Run Briefing</strong> to start the 7-agent AI pipeline
        </p>
      )}
    </div>
  );
}
