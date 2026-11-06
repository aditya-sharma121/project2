import React from "react";

interface SeverityBadgeProps {
  severity: "low" | "medium" | "high" | "critical" | string;
  className?: string;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, className = "" }) => {
  const s = severity.toLowerCase();

  let colorClasses = "bg-primary/20 text-primary border-primary/40";
  let label = "Low";

  if (s === "critical") {
    colorClasses = "bg-critical/20 text-critical border-critical/50 animate-pulse";
    label = "CRITICAL";
  } else if (s === "high") {
    colorClasses = "bg-critical/20 text-critical border-critical/40";
    label = "High";
  } else if (s === "medium") {
    colorClasses = "bg-warning/20 text-warning border-warning/40";
    label = "Medium";
  } else if (s === "low") {
    colorClasses = "bg-success/20 text-success border-success/40";
    label = "Low";
  } else if (s === "none") {
    colorClasses = "bg-muted/20 text-muted border-borderDark";
    label = "None";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-semibold border ${colorClasses} ${className}`}
    >
      {label}
    </span>
  );
};
