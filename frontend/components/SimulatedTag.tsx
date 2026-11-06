import React from "react";

interface SimulatedTagProps {
  isSimulated?: boolean;
  className?: string;
}

export const SimulatedTag: React.FC<SimulatedTagProps> = ({ isSimulated, className = "" }) => {
  if (!isSimulated) return null;

  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono border border-purple-500/40 bg-purple-500/10 text-purple-400 font-semibold tracking-wider uppercase ${className}`}
      title="This data point is synthetic / seeded for demo simulation"
    >
      Simulated
    </span>
  );
};
