import React from "react";

interface DisclaimerBannerProps {
  className?: string;
}

export const DisclaimerBanner: React.FC<DisclaimerBannerProps> = ({ className = "" }) => {
  return (
    <div
      className={`p-3 rounded-lg border border-warning/30 bg-warning/10 text-warning text-xs font-mono flex items-start gap-2.5 ${className}`}
    >
      <span className="font-bold shrink-0">⚠️ ADVISORY NOTICE:</span>
      <div className="leading-relaxed">
        AFTERFLOW is an experimental 48-hour prototype decision-support tool, <strong>NOT an official emergency dispatch service</strong>.
        Hazard assessments and routes are advisory calculations and <strong>never guaranteed safe</strong>. Always defer to official municipal directives, local emergency responders, and police road closures.
      </div>
    </div>
  );
};
