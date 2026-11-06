import React from "react";

interface KpiCardProps {
  label: string;
  value: number | string;
  subtext?: string;
  variant?: "default" | "critical" | "warning" | "success" | "primary";
}

export const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  subtext,
  variant = "default"
}) => {
  let valueColor = "text-foreground";
  let borderAccent = "border-borderDark";

  if (variant === "critical") {
    valueColor = "text-critical";
    borderAccent = "border-critical/30";
  } else if (variant === "warning") {
    valueColor = "text-warning";
    borderAccent = "border-warning/30";
  } else if (variant === "success") {
    valueColor = "text-success";
    borderAccent = "border-success/30";
  } else if (variant === "primary") {
    valueColor = "text-primary";
    borderAccent = "border-primary/30";
  }

  return (
    <div className={`p-4 rounded-lg bg-surface border ${borderAccent} flex flex-col justify-between transition-all`}>
      <span className="text-xs font-mono text-muted uppercase tracking-wider">{label}</span>
      <div className={`text-3xl font-extrabold mt-1 ${valueColor}`}>{value}</div>
      {subtext && <span className="text-[11px] text-muted mt-1 font-mono">{subtext}</span>}
    </div>
  );
};
