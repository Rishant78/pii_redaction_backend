import { AlertTriangle, RefreshCw, ArrowLeft } from 'lucide-react';

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
  canRetry: boolean;
}

export function ErrorState({ message, onRetry, canRetry }: ErrorStateProps) {
  return (
    <div className="w-full max-w-lg mx-auto py-12 px-4 animate-in fade-in zoom-in-95 duration-300">
      <div className="bg-white border border-red-200 rounded-xl overflow-hidden shadow-sm">
        
        <div className="p-6 flex flex-col items-center text-center">
          <div className="h-12 w-12 bg-red-50 rounded-full flex items-center justify-center mb-4">
            <AlertTriangle className="h-6 w-6 text-red-500" strokeWidth={2} />
          </div>
          
          <h3 className="text-lg font-semibold text-zinc-900 mb-2">Error processing document</h3>
          
          <p className="text-sm text-zinc-600 mb-8">
            {message || "Unable to reach the redaction service. Check that the backend is running and try again."}
          </p>

          <button
            onClick={onRetry}
            className="flex items-center gap-2 px-5 py-2.5 bg-zinc-900 text-white font-medium rounded-lg shadow-sm transition-all duration-200 hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:ring-offset-2"
          >
            {canRetry ? (
              <>
                <RefreshCw className="h-4 w-4" />
                Retry
              </>
            ) : (
              <>
                <ArrowLeft className="h-4 w-4" />
                Go back
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
