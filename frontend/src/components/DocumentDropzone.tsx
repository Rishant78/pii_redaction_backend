import { useCallback, useState } from 'react';
import { UploadCloud, FileText } from 'lucide-react';
import { cn } from '../lib/utils';

interface DocumentDropzoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export function DocumentDropzone({ onFileSelect, disabled = false }: DocumentDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (disabled) return;
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  }, [disabled, onFileSelect]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  }, [onFileSelect]);

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col items-center justify-center py-12 px-4 animate-in fade-in zoom-in-95 duration-500">
      
      {/* Refined Hero / Empty State */}
      <div className="mb-12 text-center space-y-3">
        <div className="inline-flex items-center justify-center px-3 py-1 mb-4 text-xs font-medium bg-zinc-100 text-zinc-600 rounded-full border border-zinc-200">
          Secure document processing
        </div>
        <h2 className="text-4xl font-semibold text-zinc-950 tracking-tight">Protect sensitive information</h2>
        <p className="text-zinc-500 text-lg max-w-lg mx-auto leading-relaxed">
          Upload a Word document to automatically detect, normalize, and safely redact PII entities.
        </p>
      </div>

      <label
        className={cn(
          "w-full relative flex flex-col items-center justify-center py-20 px-6 border border-dashed rounded-2xl cursor-pointer transition-all duration-300 bg-white shadow-sm",
          disabled ? "opacity-50 cursor-not-allowed border-zinc-200" :
          isDragging 
            ? "border-zinc-900 bg-zinc-50 scale-[1.01] shadow-md ring-4 ring-zinc-900/5" 
            : "border-zinc-300 hover:border-zinc-400 hover:bg-zinc-50 hover:shadow-md"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="h-14 w-14 bg-white border border-zinc-200 shadow-sm rounded-xl flex items-center justify-center mb-5 transition-transform group-hover:scale-105">
          <UploadCloud className="h-6 w-6 text-zinc-700" />
        </div>
        <h3 className="text-lg font-semibold text-zinc-950 mb-1">Upload DOCX file</h3>
        <p className="text-sm text-zinc-500 mb-8 text-center max-w-sm">
          Drag and drop your document here, or click to browse.
        </p>
        
        <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-100/50 border border-zinc-200 rounded-md shadow-sm">
          <FileText className="h-4 w-4 text-zinc-600" />
          <span className="text-xs font-medium text-zinc-700">Supported format: .docx</span>
        </div>

        <input
          type="file"
          className="hidden"
          accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleChange}
          disabled={disabled}
        />
      </label>

      {/* Visual Product Flow indicator */}
      <div className="mt-16 w-full max-w-xl mx-auto flex items-center justify-between text-zinc-400">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 rounded-full border-2 border-zinc-200 flex items-center justify-center bg-white text-xs font-semibold text-zinc-900">1</div>
          <span className="text-xs font-medium text-zinc-500">Detect</span>
        </div>
        <div className="flex-1 h-[1px] bg-zinc-200 mx-4" />
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 rounded-full border-2 border-zinc-200 flex items-center justify-center bg-white text-xs font-semibold text-zinc-400">2</div>
          <span className="text-xs font-medium">Redact</span>
        </div>
        <div className="flex-1 h-[1px] bg-zinc-200 mx-4" />
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 rounded-full border-2 border-zinc-200 flex items-center justify-center bg-white text-xs font-semibold text-zinc-400">3</div>
          <span className="text-xs font-medium">Download</span>
        </div>
      </div>
    </div>
  );
}

