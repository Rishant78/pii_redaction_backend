# Frontend/API Contract

Base URL during local development: `http://localhost:8000`

## GET /health

Returns:

```json
{"status":"ok","service":"pii-redaction"}
```

## POST /analyze

Multipart form field: `file` (`.docx`).

Returns document metadata, counts by PII type, unique-value counts and up to 100 detection samples.

## POST /redact

Multipart form field: `file` (`.docx`).

Returns `redacted_output.docx` as a downloadable DOCX response.

The backend should remain the source of truth for detection and replacement. A frontend should only display results, upload documents and download the generated document.
