import React from 'react';

interface EditableQuantityInputProps {
  orderId:           number;
  value:             number;         // current final_qty
  aiSuggestion:      number;         // ai_recommended_qty (read-only hint)
  unit:              string;
  ownerModified:     boolean;
  onChange:          (newQty: number) => void;  // called on every change (debounced by parent)
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
    <div className="flex flex-col gap-1.5">
      {/* Label row */}
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
          Final Quantity
        </span>
        {ownerModified && (
          <span
            className="text-[10px] px-1.5 py-0.5 rounded font-medium"
            style={{ background: 'rgba(245,158,11,0.12)', color: '#fcd34d', border: '1px solid rgba(245,158,11,0.2)' }}
          >
            ✏ Owner-edited
          </span>
        )}
      </div>

      {/* Input */}
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
          className="input pr-12 font-semibold text-base mono"
          style={{
            borderColor: isDifferent ? 'rgba(245,158,11,0.5)' : undefined,
            color: isDifferent ? '#fcd34d' : 'var(--text-primary)',
          }}
          aria-label={`Final quantity for order ${orderId}`}
        />
        <span
          className="absolute right-3 text-xs"
          style={{ color: 'var(--text-muted)' }}
        >
          {unit}s
        </span>
      </div>

      {/* AI suggestion hint — always visible, greyed */}
      <div className="flex items-center gap-1.5">
        <span
          className="text-[10px]"
          style={{ color: 'var(--text-muted)' }}
        >
          🤖 AI suggested:
        </span>
        <span
          className="text-[10px] mono font-medium"
          style={{ color: isDifferent ? 'rgba(245,158,11,0.6)' : 'var(--text-muted)' }}
        >
          {aiSuggestion} {unit}s
        </span>
        {isDifferent && (
          <button
            onClick={() => onChange(aiSuggestion)}
            className="text-[10px] ml-1"
            style={{ color: '#60a5fa' }}
            title="Reset to AI suggestion"
          >
            ↺ Reset
          </button>
        )}
      </div>
    </div>
  );
}
