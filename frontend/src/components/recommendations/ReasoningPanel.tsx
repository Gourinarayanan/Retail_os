import React from 'react';
import { Brain, ChevronRight, AlertTriangle, TrendingUp, Package } from 'lucide-react';

interface ReasoningPanelProps {
  reasoning: string;
  reasons?:  string[];
  orderId:   number;
}

function classifyLine(line: string): 'prophet' | 'scenario' | 'stock' | 'cycle' | 'expiry' | 'default' {
  const l = line.toLowerCase();
  if (l.includes('holt-winters') || l.includes('prophet') || l.includes('forecast') || l.includes('baseline'))  return 'prophet';
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
  prophet:  <TrendingUp  className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />,
  scenario: <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />,
  stock:    <Package     className="w-3.5 h-3.5 text-sky-500 shrink-0 mt-0.5" />,
  cycle:    <ChevronRight className="w-3.5 h-3.5 text-violet-500 shrink-0 mt-0.5" />,
  expiry:   <AlertTriangle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />,
  default:  <ChevronRight className="w-3.5 h-3.5 text-on-surface-variant shrink-0 mt-0.5" />,
};

const LINE_COLORS: Record<string, string> = {
  prophet:  'text-emerald-700',
  scenario: 'text-amber-700',
  stock:    'text-sky-700',
  cycle:    'text-violet-700',
  expiry:   'text-red-700',
  default:  'text-on-surface-variant',
};

export default function ReasoningPanel({ reasoning, reasons, orderId }: ReasoningPanelProps) {
  const lines = reasoning
    .split(/\n|·|•/)
    .map(l => l.trim())
    .filter(l => l.length > 4);

  return (
    <div id={`reasoning-panel-${orderId}`} className="flex flex-col gap-2 h-full">
      <div className="flex items-center gap-1.5 px-1">
        <Brain className="w-3.5 h-3.5 text-primary" />
        <span className="font-label-xs text-[10px] uppercase tracking-wider text-primary font-bold">
          Copilot Reasoning
        </span>
      </div>

      <div className="flex-1 rounded-xl px-4 py-3 bg-surface-container-low border border-border-glass flex flex-col gap-2">
        {lines.map((line, i) => {
          const type = classifyLine(line);
          return (
            <div key={i} className="flex items-start gap-2.5">
              {LINE_ICONS[type]}
              <span className={`text-[11.5px] leading-snug font-medium ${LINE_COLORS[type]}`}>
                {line}
              </span>
            </div>
          );
        })}

        {reasons && reasons.length > 0 && (
          <>
            <div className="w-full h-px bg-border-glass my-1" />
            {reasons.map((r, i) => (
              <div key={`r-${i}`} className="flex items-start gap-2.5">
                <ChevronRight className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
                <span className="text-[11.5px] leading-snug font-medium text-primary">
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
