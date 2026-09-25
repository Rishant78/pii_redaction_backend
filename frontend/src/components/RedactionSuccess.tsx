import { CheckCircle2, Download, FileText, ArrowLeft } from 'lucide-react';

interface RedactionSuccessProps {
  originalFile: File;
  redactedFilename: string;
  onDownload: () => void;
  onReset: () => void;
}

export function RedactionSuccess({ originalFile, redactedFilename, onDownload, onReset }: RedactionSuccessProps) {
  return (
    <div className="w-full max-w-2xl mx-auto py-16 px-4 animate-in fade-in zoom-in-95 duration-500">
      
      <div className="flex flex-col items-center text-center mb-12">
        <div className="h-16 w-16 bg-zinc-950 text-white rounded-2xl flex items-center justify-center mb-6 shadow-md">
          <CheckCircle2 className="h-8 w-8" strokeWidth={2.5} />
        </div>
        <h2 className="text-3xl font-semibold text-zinc-950 tracking-tight mb-3">Redaction complete</h2>
        <p className="text-zinc-500 text-lg">Your document has been successfully processed and secured.</p>
      </div>

      <div className="bg-white border border-zinc-200 rounded-2xl overflow-hidden shadow-sm mb-12 ring-1 ring-zinc-950/5">
        <div className="p-8 space-y-5">
          <div className="flex items-center gap-4 text-sm font-medium text-zinc-700">
            <div className="h-6 w-6 rounded-full bg-zinc-100 flex items-center justify-center shrink-0">
              <CheckCircle2 className="h-4 w-4 text-zinc-950" />
            </div>
            Document structure verified
          </div>
          <div className="flex items-center gap-4 text-sm font-medium text-zinc-700">
            <div className="h-6 w-6 rounded-full bg-zinc-100 flex items-center justify-center shrink-0">
              <CheckCircle2 className="h-4 w-4 text-zinc-950" />
            </div>
            Multi-pass entity resolution applied
          </div>
          <div className="flex items-center gap-4 text-sm font-medium text-zinc-700">
            <div className="h-6 w-6 rounded-full bg-zinc-100 flex items-center justify-center shrink-0">
              <CheckCircle2 className="h-4 w-4 text-zinc-950" />
            </div>
            Redacted DOCX payload generated
          </div>
        </div>
        
        <div className="border-t border-zinc-100 bg-zinc-50/50 p-6 space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-zinc-500 font-medium">Original file:</span>
            <span className="font-semibold text-zinc-950 flex items-center gap-2 px-3 py-1 bg-white border border-zinc-200 rounded-md">
              <FileText className="h-4 w-4 text-zinc-400" />
              {originalFile.name}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-zinc-500 font-medium">Output file:</span>
            <span className="font-semibold text-zinc-950 flex items-center gap-2 px-3 py-1 bg-white border border-zinc-200 rounded-md">
              <FileText className="h-4 w-4 text-zinc-950" />
              {redactedFilename}
            </span>
          </div>
        </div>
      </div>

      <div className="flex flex-col items-center gap-6">
        <button
          onClick={onDownload}
          className="w-full flex justify-center items-center gap-2 px-8 py-3.5 bg-zinc-950 text-white font-medium rounded-xl shadow-md transition-all duration-300 hover:bg-zinc-800 hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-zinc-950 focus:ring-offset-2"
        >
          <Download className="h-5 w-5" />
          Download secure document
        </button>
        
        <button
          onClick={onReset}
          className="text-sm font-medium text-zinc-500 hover:text-zinc-950 transition-colors py-2 px-4 rounded-lg hover:bg-zinc-100 flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Process another document
        </button>
      </div>
    </div>
  );
}
