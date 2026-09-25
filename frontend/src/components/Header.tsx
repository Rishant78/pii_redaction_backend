"use client";

import { useState, useEffect } from 'react';
import { checkHealth } from '../lib/api';
import { Shield } from 'lucide-react';
import { cn } from '../lib/utils';

export function StatusIndicator() {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    
    const verifyHealth = async () => {
      const healthy = await checkHealth();
      if (mounted) setIsHealthy(healthy);
    };

    verifyHealth();
    const interval = setInterval(verifyHealth, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="flex items-center gap-2 text-sm text-zinc-500 font-medium tracking-tight">
      <div className={cn(
        "h-2 w-2 rounded-full",
        isHealthy === null ? "bg-zinc-300 animate-pulse" :
        isHealthy ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" : "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]"
      )} />
      {isHealthy === null ? "Checking connection..." :
       isHealthy ? "Backend connected" : "Backend offline"}
    </div>
  );
}

export function Header() {
  return (
    <header className="w-full border-b border-zinc-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 bg-zinc-950 rounded-lg flex items-center justify-center shadow-[0_2px_10px_rgba(0,0,0,0.1)]">
            <Shield className="h-4 w-4 text-white" strokeWidth={2.5} />
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-sm font-semibold text-zinc-950 tracking-tight">PII Redaction Tool</h1>
            <span className="h-4 w-[1px] bg-zinc-300" />
            <p className="text-xs text-zinc-500 font-medium">Enterprise Document Protection</p>
          </div>
        </div>
        <StatusIndicator />
      </div>
    </header>
  );
}
