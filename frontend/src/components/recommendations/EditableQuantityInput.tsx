import React from 'react';
import { RefreshCcw, PencilLine } from 'lucide-react';

interface EditableQuantityInputProps {
  orderId:           number;
  value:             number;
  aiSuggestion:      number;
  unit:              string;
  ownerModified:     boolean;
  onChange:          (newQty: number) => void;
  disabled?:         boolean;
}

export default function EditableQuantityInput({
  orderId,
  value,
  aiSuggestion,
  unit,
  ownerModified,
  onChange,
  disabled = false,
}: EditableQuantityInputProps) {
  const isDifferent = Math.abs(value - aiSuggestion) > 0.01;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between px-1">
        <span className="font-label-xs text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">
          Final Quantity
        </span>
        {ownerModified && (
          <span className="font-label-xs text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-50 text-amber-600 border border-amber-200 flex items-center gap-1 font-bold">
            <PencilLine className="w-2.5 h-2.5" /> Edited
          </span>
        )}
      </div>

      <div className="relative flex items-center">
        <input
          id={`order-qty-${orderId}`}
          type="number"
          min={0}
          step={0.5}
          value={value}
          disabled={disabled}
          onChange={(e) => {
            const raw = parseFloat(e.target.value);
            if (!isNaN(raw) && raw >= 0) onChange(raw);
          }}
          className={`nexus-input w-full pr-12 pl-4 py-2 rounded-xl font-bold font-mono text-lg transition-colors ${
            isDifferent ? 'text-amber-600 border-amber-300 focus:border-amber-400 bg-amber-50/30' : 'text-on-surface'
          }`}
          aria-label={`Final quantity for order ${orderId}`}
        />
        <span className="absolute right-4 text-xs font-semibold text-on-surface-variant/60 pointer-events-none">
          {unit}s
        </span>
      </div>

      <div className="flex items-center justify-between px-1 h-5">
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-on-surface-variant">🤖 AI suggested:</span>
          <span className={`text-[10.5px] font-mono font-bold ${isDifferent ? 'text-amber-500' : 'text-on-surface-variant'}`}>
            {aiSuggestion} {unit}s
          </span>
        </div>
        {isDifferent && (
          <button
            onClick={() => onChange(aiSuggestion)}
            className="flex items-center gap-1 text-[10px] text-primary hover:text-indigo-700 font-semibold transition-colors"
            title="Reset to AI suggestion"
          >
            <RefreshCcw className="w-3 h-3" /> Reset
          </button>
        )}
      </div>
    </div>
  );
}
