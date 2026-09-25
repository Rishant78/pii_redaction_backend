export type PIIType = "PERSON" | "EMAIL" | "PHONE" | "ORGANIZATION" | "ADDRESS" | "SSN" | "CREDIT_CARD" | "DOB" | "IP_ADDRESS";

export interface AnalyzeResponse {
  paragraphs: number;
  tables: number;
  detections: number;
  counts: Record<PIIType, number>;
  unique_values: Record<PIIType, number>;
  samples: Array<{
    type: PIIType;
    text: string;
    confidence: number;
    source: string;
  }>;
}

export type AppState = 
  | { status: 'idle' }
  | { status: 'analyzing'; file: File }
  | { status: 'analyzed'; file: File; results: AnalyzeResponse }
  | { status: 'redacting'; file: File; results: AnalyzeResponse }
  | { status: 'success'; originalFile: File; redactedBlob: Blob; filename: string; replacementCount: number }
  | { status: 'error'; message: string; previousState?: AppState };
