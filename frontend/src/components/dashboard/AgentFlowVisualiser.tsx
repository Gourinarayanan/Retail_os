import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Play, Loader2, CheckCircle2, XCircle, Clock, Sparkles,
  ChevronRight, Network, Activity, Terminal,
} from 'lucide-react';
import { streamBriefing } from '../../api/client';
import type { AgentLogEntry, AgentName, SSECompleteEvent } from '../../types';

interface AgentConfig {
  id:    AgentName;
  label: string;
  icon:  string;
  color: string;
}

const AGENTS: AgentConfig[] = [
  { id: 'context',     label: 'Context',     icon: '🌤️', color: 'text-sky-500'    },
  { id: 'scenario',    label: 'Scenario',    icon: '🎯', color: 'text-violet-500' },
  { id: 'forecast',    label: 'Forecast',    icon: '📈', color: 'text-emerald-500'},
  { id: 'inventory',   label: 'Inventory',   icon: '📦', color: 'text-amber-500'  },
  { id: 'supplier',    label: 'Supplier',    icon: '🚛', color: 'text-red-500'    },
  { id: 'opportunity', label: 'Opportunity', icon: '💡', color: 'text-orange-500' },
  { id: 'briefing',    label: 'Briefing',    icon: '✨', color: 'text-pink-500'   },
];

type NodeStatus = 'idle' | 'running' | 'complete' | 'error';
interface NodeState { status: NodeStatus; summary: string; elapsed: number | null; startedAt: number | null; }
const INITIAL_NODES: Record<string, NodeState> = Object.fromEntries(
  AGENTS.map(a => [a.id, { status: 'idle', summary: '', elapsed: null, startedAt: null }])
);

function LiveElapsed({ startedAt }: { startedAt: number }) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setElapsed(Date.now() - startedAt), 100);
    return () => clearInterval(id);
  }, [startedAt]);
  return <span className="text-[10px] font-mono text-primary">{(elapsed / 1000).toFixed(1)}s</span>;
}

interface AgentFlowVisualiserProps {
  onComplete?: () => void;
}

export default function AgentFlowVisualiser({ onComplete }: AgentFlowVisualiserProps) {
  const [running,   setRunning]   = useState(false);
  const [nodes,     setNodes]     = useState<Record<string, NodeState>>(INITIAL_NODES);
  const [summary,   setSummary]   = useState<SSECompleteEvent | null>(null);
  const [error,     setError]     = useState<string | null>(null);
  const [totalTime, setTotalTime] = useState<number | null>(null);
  const [selectedId, setSelectedId] = useState<string>('context');
  const startTimeRef = useRef<number | null>(null);

  const reset = useCallback(() => {
    setNodes(INITIAL_NODES);
    setSummary(null);
    setError(null);
    setTotalTime(null);
    startTimeRef.current = null;
  }, []);

  const handleEntry = useCallback((raw: object) => {
    const entry = raw as AgentLogEntry;
    const { agent, status, summary: msg } = entry;
    setSelectedId(agent);
    setNodes(prev => {
      const node = prev[agent] ?? { status: 'idle', summary: '', elapsed: null, startedAt: null };
      if (status === 'started')  return { ...prev, [agent]: { status: 'running',  summary: msg, startedAt: Date.now(), elapsed: null } };
      if (status === 'complete') return { ...prev, [agent]: { status: 'complete', summary: msg, elapsed: node.startedAt ? Date.now() - node.startedAt : null, startedAt: node.startedAt } };
      if (status === 'error')    return { ...prev, [agent]: { status: 'error',    summary: msg, elapsed: node.startedAt ? Date.now() - node.startedAt : null, startedAt: node.startedAt } };
      return prev;
    });
  }, []);

  const handleComplete = useCallback((raw: object) => {
    const data = raw as SSECompleteEvent;
    setSummary(data);
    setRunning(false);
    if (startTimeRef.current) setTotalTime(Date.now() - startTimeRef.current);
    onComplete?.();
  }, [onComplete]);

  const handleError = useCallback((err: Error) => {
    setError(err.message);
    setRunning(false);
  }, []);

  const startPipeline = useCallback(async () => {
    reset();
    setRunning(true);
    startTimeRef.current = Date.now();
    await streamBriefing(handleEntry, handleComplete, handleError);
  }, [reset, handleEntry, handleComplete, handleError]);

  const selectedNode = nodes[selectedId];
  const selectedAgent = AGENTS.find(a => a.id === selectedId) ?? AGENTS[0];

  return (
    <div className="glass-panel rounded-xl p-6 border border-border-glass">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-border-glass/60">
        <div className="flex items-center gap-3">
          <Network className="w-5 h-5 text-primary" />
          <div>
            <h3 className="font-headline-sm font-bold text-on-surface">Agent Pipeline Orchestrator</h3>
            <p className="font-label-xs text-on-surface-variant uppercase tracking-wider">Multi-Agent Workflow States</p>
          </div>
        </div>
        <button
          id="btn-run-briefing"
          onClick={startPipeline}
          disabled={running}
          className="px-4 py-1.5 rounded-lg border border-primary/40 bg-primary/10 text-primary hover:bg-primary/20 hover:border-primary disabled:opacity-40 transition-all font-label-md text-xs tracking-wider uppercase flex items-center gap-2"
        >
          {running
            ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Running…</>
            : <><Play className="w-3.5 h-3.5" /> Run Briefing</>
          }
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Node list */}
        <div className="lg:col-span-7 flex flex-col gap-3">
          {AGENTS.map(agent => {
            const state = nodes[agent.id];
            const isSelected  = agent.id === selectedId;
            const isCompleted = state.status === 'complete';
            const isRunning   = state.status === 'running';
            const isError     = state.status === 'error';

            return (
              <div
                key={agent.id}
                onClick={() => setSelectedId(agent.id)}
                className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 relative overflow-hidden group ${
                  isSelected
                    ? 'bg-primary/5 border-primary'
                    : 'bg-surface-container-low border-border-glass hover:bg-surface-container-high'
                }`}
              >
                {isRunning && <div className="absolute top-0 left-0 w-1 h-full bg-primary animate-pulse" />}

                <div className="flex items-center justify-between gap-4 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg border border-border-glass/80 ${
                      isRunning ? 'bg-primary/20' : isCompleted ? 'bg-primary/10' : 'bg-surface-container'
                    }`}>
                      <span className="text-base leading-none">{agent.icon}</span>
                    </div>
                    <div>
                      <h4 className="font-headline-sm text-sm font-bold text-on-surface group-hover:text-primary transition-colors">
                        {agent.label} Agent
                      </h4>
                      <p className="font-label-xs text-xs text-on-surface-variant uppercase mt-0.5">
                        {isRunning && state.startedAt ? <LiveElapsed startedAt={state.startedAt} /> : state.status}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-1 select-none">
                    <span className={`text-[11px] font-label-xs uppercase tracking-wider px-2 py-0.5 rounded ${
                      isRunning   ? 'bg-primary/20 text-primary font-bold animate-pulse'
                      : isCompleted ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                      : isError     ? 'bg-red-50 text-red-500 border border-red-200'
                      : 'bg-surface-container-highest text-on-surface-variant'
                    }`}>
                      {isError ? 'error' : state.status}
                    </span>
                    {isCompleted && state.elapsed != null && (
                      <span className="font-label-xs text-[10px] text-on-surface-variant font-mono">
                        {(state.elapsed / 1000).toFixed(1)}s
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Console */}
        <div className="lg:col-span-5 glass-panel rounded-lg p-5 border border-border-glass flex flex-col justify-between min-h-[300px]">
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-border-glass pb-3">
              <Terminal className="w-4 h-4 text-primary" />
              <span className="font-label-md text-on-surface uppercase tracking-wider">Agent Console Output</span>
            </div>

            <div className="space-y-2">
              <p className="font-label-xs text-on-surface-variant uppercase">TARGET NODE:</p>
              <h4 className="font-headline-sm text-base text-primary font-bold">{selectedAgent.label} Agent</h4>
              <p className="font-label-xs text-xs text-on-surface-variant">
                STATUS: <span className="text-primary">{selectedNode?.status?.toUpperCase()}</span>
              </p>
            </div>

            <div className="p-3.5 rounded bg-surface-container-lowest border border-border-glass font-mono text-xs text-on-surface-variant leading-relaxed h-32 overflow-y-auto">
              {selectedNode?.summary ? (
                <><span className="text-primary font-bold">&gt;_ </span>{selectedNode.summary}</>
              ) : (
                <span className="italic text-on-surface-variant/40">&gt;_ Listening for execution queue... Node in standby.</span>
              )}
            </div>

            {error && (
              <div className="p-3 rounded bg-red-50 border border-red-200 text-red-600 text-xs flex items-center gap-2">
                <XCircle className="w-4 h-4 shrink-0" /> {error}
              </div>
            )}

            {summary && (
              <div className="p-3 rounded bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 space-y-1">
                <div className="flex items-center gap-1.5 font-bold">
                  <CheckCircle2 className="w-4 h-4" /> Pipeline Complete!
                </div>
                <p>{summary.orders_count} orders · {summary.opportunities_count} opportunities
                  {totalTime && ` · ${(totalTime / 1000).toFixed(1)}s total`}
                </p>
              </div>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-border-glass text-xs space-y-2 text-on-surface-variant select-none">
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-ping" />
              <span>Pipeline Health: Operational</span>
            </div>
            <p className="text-[10px] uppercase font-label-xs text-on-surface-variant/60">
              Gemini-powered multi-agent orchestration
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
