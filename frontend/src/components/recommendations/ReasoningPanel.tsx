import React from 'react';
import { Brain, ChevronRight, AlertTriangle, TrendingUp, Package } from 'lucide-react';

interface ReasoningPanelProps {
  reasoning: string;   // full ai_reasoning text
  reasons?:  string[]; // optional structured reasons array
  orderId:   number;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function classifyLine(line: string): 'prophet' | 'scenario' | 'stock' | 'cycle' | 'expiry' | 'default' {
  const l = line.toLowerCase();
  if (l.includes('prophet') || l.includes('forecast') || l.includes('baseline'))  return 'prophet';
  if (l.includes('scenario') || l.includes('multiplier') || l.includes('onam')
    || l.includes('hartal') || l.includes('rain') || l.includes('eid')
    || l.includes('festival') || l.includes('christmas'))                          return 'scenario';
  if (l.includes('stock') || l.includes('batch') || l.includes('current')
    || l.includes('inventory') || l.includes('days remaining'))                    return 'stock';
  if (l.includes('cycle') || l.includes('daily') || l.includes('weekly')
    || l.includes('monthly') || l.includes('emergency'))                           return 'cycle';
  if (l.includes('expir'))                                                         return 'expiry';
  return 'default';
}

const LINE_ICONS: Record<string, React.ReactNode> = {
  prophet:  <TrendingUp  size={11} style={{ color: '#34d399', flexShrink: 0 }} />,
  scenario: <AlertTriangle size={11} style={{ color: '#fbbf24', flexShrink: 0 }} />,
  stock:    <Package     size={11} style={{ color: '#60a5fa', flexShrink: 0 }} />,
  cycle:    <ChevronRight size={11} style={{ color: '#c4b5fd', flexShrink: 0 }} />,
  expiry:   <AlertTriangle size={11} style={{ color: '#f87171', flexShrink: 0 }} />,
  default:  <ChevronRight size={11} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />,
};

const LINE_COLORS: Record<string, string> = {
  prophet:  '#86efac',
  scenario: '#fde68a',
  stock:    '#bfdbfe',
  cycle:    '#ddd6fe',
  expiry:   '#fca5a5',
  default:  'var(--text-secondary)',
};

// ── Main Component ────────────────────────────────────────────────────────────

export default function ReasoningPanel({ reasoning, reasons, orderId }: ReasoningPanelProps) {
  // Split reasoning into lines, filter blanks
  const lines = reasoning
    .split(/\n|·|•/)
    .map((l) => l.trim())
    .filter((l) => l.length > 4);

  return (
    <div
      id={`reasoning-panel-${orderId}`}
      className="flex flex-col gap-1.5"
    >
      {/* Header — always visible, full content below (no collapse per spec) */}
      <div className="flex items-center gap-1.5 mb-1">
        <Brain size={12} style={{ color: '#c4b5fd' }} />
        <span
          className="text-[10px] font-semibold uppercase tracking-wider"
          style={{ color: '#c4b5fd' }}
        >
          AI Reasoning
        </span>
      </div>

      {/* Full reasoning text — NOT collapsed */}
      <div
        className="rounded-lg px-3 py-3 flex flex-col gap-1.5"
        style={{
          background: 'rgba(139,92,246,0.05)',
          border: '1px solid rgba(139,92,246,0.15)',
        }}
      >
        {lines.map((line, i) => {
          const type = classifyLine(line);
          return (
            <div key={i} className="flex items-start gap-2">
              {LINE_ICONS[type]}
              <span
                className="text-[11px] leading-snug"
                style={{ color: LINE_COLORS[type] }}
              >
                {line}
              </span>
            </div>
          );
        })}

        {/* Extra structured reasons if provided */}
        {reasons && reasons.length > 0 && (
          <>
            <div className="divider my-1" />
            {reasons.map((r, i) => (
              <div key={`r-${i}`} className="flex items-start gap-2">
                <ChevronRight size={11} style={{ color: '#60a5fa', flexShrink: 0 }} />
                <span className="text-[11px] leading-snug" style={{ color: '#bfdbfe' }}>
                  {r}
                </span>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
