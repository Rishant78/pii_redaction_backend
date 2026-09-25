"use client";

import { useDocumentRedaction } from '../hooks/useDocumentRedaction';
import { DocumentDropzone } from '../components/DocumentDropzone';
import { AnalysisResults } from '../components/AnalysisResults';
import { RedactionProgress } from '../components/RedactionProgress';
import { RedactionSuccess } from '../components/RedactionSuccess';
import { ErrorState } from '../components/ErrorState';
import { Loader2 } from 'lucide-react';

export default function Home() {
  const { 
    state, 
    handleFileSelect, 
    handleRedact, 
    handleDownload, 
    reset, 
    recoverFromError 
  } = useDocumentRedaction();

  return (
    <main className="flex-1 flex flex-col w-full max-w-6xl mx-auto px-6 py-12">
      {state.status === 'idle' && (
        <DocumentDropzone onFileSelect={handleFileSelect} />
      )}

      {state.status === 'analyzing' && (
        <div className="flex flex-col items-center justify-center py-20 animate-in fade-in duration-300">
          <Loader2 className="h-8 w-8 text-zinc-400 animate-spin mb-4" />
          <h3 className="text-lg font-medium text-zinc-900">Analyzing document...</h3>
          <p className="text-sm text-zinc-500 mt-1">Discovering PII entities in {state.file.name}</p>
        </div>
      )}

      {state.status === 'analyzed' && (
        <AnalysisResults 
          file={state.file}
          results={state.results}
          onRedact={handleRedact}
          onCancel={reset}
        />
      )}

      {state.status === 'redacting' && (
        <RedactionProgress />
      )}

      {state.status === 'success' && (
        <RedactionSuccess
          originalFile={state.originalFile}
          redactedFilename={state.filename}
          onDownload={handleDownload}
          onReset={reset}
        />
      )}

      {state.status === 'error' && (
        <ErrorState 
          message={state.message} 
          onRetry={recoverFromError} 
          canRetry={!!state.previousState} 
        />
      )}
    </main>
  );
}
