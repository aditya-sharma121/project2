import React from "react";

interface ConfidenceBadgeProps {
  score?: number;
  label?: string;
  className?: string;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ score, label, className = "" }) => {
  let displayLabel = label;
  if (!displayLabel && score !== undefined) {
    if (score >= 85) displayLabel = "High-confidence evidence";
    else if (score >= 70) displayLabel = "Strong evidence";
    else if (score >= 40) displayLabel = "Probable";
    else displayLabel = "Unverified";
  }

  displayLabel = displayLabel || "Unverified";

  let styles = "bg-muted/10 text-muted border-borderDark";
  if (displayLabel.includes("High-confidence")) {
    styles = "bg-success/20 text-success border-success/40";
  } else if (displayLabel.includes("Strong")) {
    styles = "bg-primary/20 text-primary border-primary/40";
  } else if (displayLabel.includes("Probable")) {
    styles = "bg-warning/20 text-warning border-warning/40";
  } else {
    styles = "bg-borderDark/40 text-muted border-borderDark";
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-mono border ${styles} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-75"></span>
      <span>{displayLabel}</span>
      {score !== undefined && (
        <span className="opacity-80">({score.toFixed(0)})</span>
      )}
    </span>
  );
};
