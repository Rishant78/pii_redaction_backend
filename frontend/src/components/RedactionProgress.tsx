import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';

export function RedactionProgress() {
  const [stage, setStage] = useState(0);

  const stages = [
    "Scanning document structure...",
    "Resolving detected entities...",
    "Applying replacements...",
    "Verifying output..."
  ];

  // Fake the progression text over 10 seconds just for visual feedback
  // since the backend doesn't stream progress.
  useEffect(() => {
    const timer1 = setTimeout(() => setStage(1), 2000);
    const timer2 = setTimeout(() => setStage(2), 5000);
    const timer3 = setTimeout(() => setStage(3), 8500);
    
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div className="w-full max-w-lg mx-auto py-20 px-4 flex flex-col items-center justify-center animate-in fade-in duration-500">
      <div className="relative mb-8">
        <div className="absolute inset-0 bg-zinc-200 rounded-full blur-2xl opacity-50 animate-pulse" />
        <div className="h-16 w-16 bg-white border border-zinc-200 shadow-md rounded-2xl flex items-center justify-center relative z-10">
          <Loader2 className="h-8 w-8 text-zinc-950 animate-spin" strokeWidth={2.5} />
        </div>
      </div>
      
      <h3 className="text-2xl font-semibold text-zinc-950 tracking-tight mb-3">Redacting document</h3>
      
      <div className="h-6 flex items-center justify-center overflow-hidden">
        <p key={stage} className="text-sm text-zinc-500 font-medium animate-in slide-in-from-bottom-2 fade-in duration-300">
          {stages[stage]}
        </p>
      </div>
      
      {/* Visual track */}
      <div className="w-48 h-1 bg-zinc-100 rounded-full mt-8 overflow-hidden relative">
        <div className="absolute top-0 bottom-0 left-0 w-1/3 bg-zinc-950 rounded-full animate-[progress_2s_ease-in-out_infinite]" />
      </div>
    </div>
  );
}
