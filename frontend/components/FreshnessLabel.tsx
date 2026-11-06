import React from "react";

interface FreshnessLabelProps {
  minutes?: number;
  createdAt?: string;
  className?: string;
}

export const FreshnessLabel: React.FC<FreshnessLabelProps> = ({ minutes, createdAt, className = "" }) => {
  let min = minutes;
  if (min === undefined && createdAt) {
    const created = new Date(createdAt).getTime();
    min = Math.max(0, (Date.now() - created) / 60000);
  }

  const m = min ?? 0;
  const isStale = m > 360; // > 6 hours is stale

  let text = `${m.toFixed(0)}m ago`;
  if (m >= 60) {
    const hours = (m / 60).toFixed(1);
    text = `${hours}h ago`;
  }

  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-mono ${
        isStale ? "text-warning/90 font-medium" : "text-muted"
      } ${className}`}
      title={isStale ? "Stale report (>6h window) - may no longer reflect current ground conditions" : "Recent report"}
    >
      <span>{text}</span>
      {isStale && (
        <span className="px-1 py-0.2 bg-warning/20 border border-warning/40 text-[10px] rounded text-warning">
          STALE
        </span>
      )}
    </span>
  );
};
