import { AnalyzeResponse, PIIType } from '../lib/types';
import { FileText, Shield, ArrowRight } from 'lucide-react';
import { cn } from '../lib/utils';

interface AnalysisResultsProps {
  file: File;
  results: AnalyzeResponse;
  onRedact: () => void;
  onCancel: () => void;
  isRedacting?: boolean;
}

const piiLabels: Record<PIIType, string> = {
  PERSON: 'Person Names',
  ORGANIZATION: 'Organizations',
  ADDRESS: 'Addresses',
  EMAIL: 'Email Addresses',
  PHONE: 'Phone Numbers',
  SSN: 'Social Security Numbers',
  CREDIT_CARD: 'Credit Cards',
  DOB: 'Dates of Birth',
  IP_ADDRESS: 'IP Addresses',
};

export function AnalysisResults({ file, results, onRedact, onCancel, isRedacting }: AnalysisResultsProps) {
  const activeCategories = Object.entries(results.counts)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1]) as [PIIType, number][];

  return (
    <div className="w-full max-w-3xl mx-auto py-12 px-4 animate-in fade-in zoom-in-95 duration-500">
      
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-3xl font-semibold text-zinc-950 tracking-tight">Analysis Complete</h2>
          <p className="text-zinc-500 mt-2 text-lg">Review detected PII categories before proceeding to redaction.</p>
        </div>
        <button 
          onClick={onCancel}
          disabled={isRedacting}
          className="text-sm font-medium text-zinc-500 hover:text-zinc-950 transition-colors px-4 py-2 rounded-lg hover:bg-zinc-100 disabled:opacity-50"
        >
          Cancel
        </button>
      </div>

      <div className="bg-white border border-zinc-200 rounded-2xl overflow-hidden shadow-sm mb-8 ring-1 ring-zinc-950/5">
        <div className="p-5 border-b border-zinc-100 bg-zinc-50/50 flex items-center gap-4">
          <div className="h-12 w-12 bg-white border border-zinc-200 shadow-sm rounded-xl flex items-center justify-center">
            <FileText className="h-6 w-6 text-zinc-700" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-zinc-950">{file.name}</h3>
            <p className="text-sm text-zinc-500">
              {(file.size / 1024 / 1024).toFixed(2)} MB • {results.paragraphs} paragraphs processed
            </p>
          </div>
        </div>
        
        <div className="p-8">
          <div className="flex items-center justify-between mb-6">
            <h4 className="text-base font-semibold text-zinc-950">
              {activeCategories.length} PII categories detected
            </h4>
          </div>

          <div className="space-y-2">
            {activeCategories.length === 0 ? (
              <div className="py-12 text-center text-zinc-500 text-sm border-2 border-dashed border-zinc-100 rounded-xl">
                No sensitive information was detected in this document.
              </div>
            ) : (
              activeCategories.map(([type, count]) => (
                <div key={type} className="flex items-center justify-between py-3 px-4 bg-zinc-50/50 hover:bg-zinc-100/80 border border-zinc-100 rounded-xl transition-colors group">
                  <span className="text-sm font-medium text-zinc-700 group-hover:text-zinc-950">
                    {piiLabels[type] || type}
                  </span>
                  <div className="flex items-center gap-3 bg-white px-3 py-1 rounded-full border border-zinc-200 shadow-sm">
                    <span className="text-sm font-semibold text-zinc-950">{count}</span>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <div className="mt-8 p-4 bg-zinc-50 border border-zinc-100 rounded-xl flex items-start gap-3">
            <Shield className="h-5 w-5 text-zinc-500 mt-0.5 shrink-0" />
            <p className="text-sm text-zinc-600 leading-relaxed">
              These are initial first-pass detections. The final redaction engine uses a complete multi-pass entity-resolution pipeline to ensure compound and split-run entities are fully redacted.
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={onRedact}
          disabled={isRedacting}
          className={cn(
            "flex items-center gap-2 px-8 py-3 bg-zinc-950 text-white font-medium rounded-xl shadow-md transition-all duration-300 hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-zinc-950 focus:ring-offset-2",
            isRedacting ? "opacity-90 cursor-wait scale-[0.98]" : "hover:scale-[1.02]"
          )}
        >
          {isRedacting ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Initializing Engine...
            </>
          ) : (
            <>
              Confirm & Redact
              <ArrowRight className="h-5 w-5" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
