"use client";

import { motion } from "framer-motion";
import { AlertTriangle, ShieldCheck, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface ThreatData {
  status: "BERBAHAYA" | "WASPADA" | "AMAN";
  target: string;
  type: string;
  analysis_report: string;
}

interface ThreatCardProps {
  data: ThreatData;
}

export function ThreatCard({ data }: ThreatCardProps) {
  const isDanger = data.status === "BERBAHAYA";
  const isWarning = data.status === "WASPADA";
  const isSafe = data.status === "AMAN";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "brutal-box p-6 mb-4 relative overflow-hidden",
        isDanger ? "brutal-border animate-shake danger-neon" : "brutal-shadow-static",
        isWarning && "border-brand-warning shadow-[5px_5px_0px_0px_var(--color-brand-warning)]",
        isSafe && "border-brand-safe shadow-[5px_5px_0px_0px_var(--color-brand-safe)]"
      )}
    >
      <div className="flex items-start gap-4 mb-4">
        <div className={cn(
          "p-3 brutal-border bg-black text-white dark:bg-white dark:text-black flex-shrink-0",
          isDanger && "bg-brand-danger text-white border-brand-danger animate-pulse",
          isWarning && "bg-brand-warning text-black border-black",
          isSafe && "bg-brand-safe text-black border-black"
        )}>
          {isDanger && <AlertTriangle size={32} />}
          {isWarning && <Info size={32} />}
          {isSafe && <ShieldCheck size={32} />}
        </div>

        <div className="flex-1">
          <div className="font-mono text-xs text-gray-500 uppercase tracking-widest mb-1">
            {data.type} ANALYSIS REPORT
          </div>
          <h3 className="font-bold text-xl break-all line-clamp-2" title={data.target}>
            {data.target}
          </h3>
          <div className={cn(
            "inline-block mt-2 font-mono font-bold px-2 py-1 text-sm border-2",
            isDanger && "border-brand-danger text-brand-danger",
            isWarning && "border-brand-warning text-brand-warning",
            isSafe && "border-brand-safe text-brand-safe"
          )}>
            STATUS: {data.status}
          </div>
        </div>
      </div>

      <div className="mt-4 p-4 bg-gray-100 dark:bg-[#222] border-t-2 border-black dark:border-white font-sans text-sm leading-relaxed whitespace-pre-wrap">
        {data.analysis_report}
      </div>

      {/* Decorative corners */}
      <div className="absolute top-0 left-0 w-2 h-2 bg-black dark:bg-white" />
      <div className="absolute top-0 right-0 w-2 h-2 bg-black dark:bg-white" />
      <div className="absolute bottom-0 left-0 w-2 h-2 bg-black dark:bg-white" />
      <div className="absolute bottom-0 right-0 w-2 h-2 bg-black dark:bg-white" />
    </motion.div>
  );
}
