import { AnalyzeResponse } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export async function analyzeDocument(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    let msg = 'Failed to analyze document. Please check that the backend is running.';
    try {
      const data = await res.json();
      msg = data.detail || msg;
    } catch {}
    throw new Error(msg);
  }

  return res.json();
}

export async function redactDocument(file: File): Promise<{ blob: Blob; replacementCount: number }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_URL}/redact`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    let msg = 'Failed to redact document. Please check that the backend is running.';
    try {
      const data = await res.json();
      msg = data.detail || msg;
    } catch {}
    throw new Error(msg);
  }

  const blob = await res.blob();
  const replacements = parseInt(res.headers.get('x-pii-detections') || '0', 10);
  return { blob, replacementCount: replacements };
}
