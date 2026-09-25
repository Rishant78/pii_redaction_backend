import { useState, useCallback } from 'react';
import { AppState } from '../lib/types';
import { analyzeDocument, redactDocument } from '../lib/api';

export function useDocumentRedaction() {
  const [state, setState] = useState<AppState>({ status: 'idle' });

  const reset = useCallback(() => {
    setState({ status: 'idle' });
  }, []);

  const handleFileSelect = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.docx')) {
      setState({ 
        status: 'error', 
        message: 'Only .docx files are supported. Please select a valid Word document.' 
      });
      return;
    }

    setState({ status: 'analyzing', file });

    try {
      const results = await analyzeDocument(file);
      setState({ status: 'analyzed', file, results });
    } catch (err: unknown) {
      const error = err as Error;
      setState({ status: 'error', message: error.message });
    }
  }, []);

  const handleRedact = useCallback(async () => {
    if (state.status !== 'analyzed') return;

    const { file, results } = state;
    setState({ status: 'redacting', file, results });

    try {
      const { blob, replacementCount } = await redactDocument(file);
      
      const originalName = file.name;
      const baseName = originalName.substring(0, originalName.lastIndexOf('.')) || originalName;
      const filename = `${baseName}_redacted.docx`;

      setState({
        status: 'success',
        originalFile: file,
        redactedBlob: blob,
        filename,
        replacementCount
      });
    } catch (err: unknown) {
      const error = err as Error;
      setState({ status: 'error', message: error.message, previousState: state });
    }
  }, [state]);

  const handleDownload = useCallback(() => {
    if (state.status !== 'success') return;
    
    const url = URL.createObjectURL(state.redactedBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = state.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [state]);

  const recoverFromError = useCallback(() => {
    if (state.status === 'error' && state.previousState) {
      setState(state.previousState);
    } else {
      reset();
    }
  }, [state, reset]);

  return {
    state,
    reset,
    handleFileSelect,
    handleRedact,
    handleDownload,
    recoverFromError
  };
}
