# PII Redaction Tool

## Overview
This application accepts a DOCX document, detects supported Personally Identifiable Information (PII), replaces detected values with deterministic synthetic alternatives, and produces a redacted DOCX. It includes both a Python backend (FastAPI) for processing and a modern React/Next.js frontend for user interaction.

## Supported PII
- Full names (Context-aware person-name heuristics)
- Company/organization names (Using corporate suffixes and entity context)
- Physical/mailing addresses (Using address hints + Indian PIN codes)
- Email addresses
- Phone numbers
- SSNs (US)
- Credit card numbers (Validated via Luhn algorithm)
- Dates of birth (Context-aware based on DOB/birth proximity)
- IPv4 addresses

*Note: While the detectors successfully support all 9 types, the supplied Red Herring Prospectus (RHP) source document completely lacked examples of Social Security Numbers (SSNs), Credit Card Numbers, IP Addresses, and Dates of Birth. Those 4 categories were therefore validated synthetically.*

## Architecture
The application uses a strict multi-pass pipeline:
1. **Document Extraction**: Raw paragraphs, tables, headers, and footers are extracted from the DOCX without stripping underlying run boundaries.
2. **First-Pass Detection**: Text is evaluated against all PII rules to produce raw entity spans.
3. **Overlap Resolution**: Colliding spans are resolved based on type priority.
4. **Entity Registry & Alias Propagation**: A document-wide registry tracks canonical representations of entities (e.g., matching "Company Ltd." with "Company"). This ensures the exact same synthetic replacement is mapped to every occurrence of that entity across the entire document.
5. **Synthetic Replacement Generation**: The registry produces deterministic, safe synthetic replacements that match the entity type.
6. **Second-Pass Redaction**: The DOCX XML structure is modified at the run level. The system handles split-run PII dynamically without corrupting document styles.
7. **DOCX Output**: The file is repackaged and served.

## Detection Approach
The tool uses a hybrid approach:
- **Regex & Structured Detection**: Used for highly structured identifiers like Emails, Phone Numbers, IPs, SSNs, and Credit Cards (supplemented with a Luhn check).
- **Contextual Detection**: Used for ambiguous fields like Person Names, Addresses, and Dates of Birth. Instead of relying solely on capitalization, it scans for context markers (e.g., "Mr.", "residing at", "born on").
- **Canonicalization**: The Organization detector dynamically handles varying suffix combinations (e.g., "Private Limited", "Inc", "LLP") and strips meaningless prefixes.

*No external LLMs, spaCy, or Presidio models are used. The entire engine runs via deterministic rules and localized context sliding windows.*

## DOCX Handling
The backend parses the document using `python-docx`. It ensures that text split across multiple DOCX "runs" (due to formatting changes or tracking artifacts) is correctly identified and replaced. Text runs containing PII are replaced inline, preserving surrounding text formatting, tables, headers, and footers intact.

## Synthetic Replacement Strategy
Replacements are generated deterministically and consistently. 
For example:
- Original: `Kushal Hegde`
- Redacted: `Nora Young` (Synthetic Person Name)

If "Kushal Hegde" appears 14 times, it is replaced by "Nora Young" 14 times, maintaining referential integrity for readers reviewing the redacted text.

## Evaluation
The repository includes an `evaluation/` directory detailing two primary tests:

1. **Synthetic Benchmark**: A 14-item controlled smoke-test guaranteeing that the baseline regex and context logic for all 9 required PII types function correctly (Accuracy: 100%, Precision: 100%, Recall: 100%, F1: 100%, Jaccard/IoU: 100%).
2. **RHP Ground-Truth Subset**: A JSON standoff annotation containing 13 complex real-world spans (and 5 explicitly annotated non-PII negative spans) across 7 paragraphs from the supplied Red Herring Prospectus. Matches are counted strictly (exact paragraph index + exact character offsets). 

*Metrics from the RHP ground truth (Accuracy: 100%, Precision: 100%, Recall: 100%, F1: 100%, Jaccard/IoU: 100%) apply ONLY to this manually annotated evaluation subset and do not imply flawless performance across the entire 127-page document, where unannotated edge cases may exist.*

## API
- `GET /health` : Returns `{ "status": "ok", "service": "pii-redaction" }`
- `POST /analyze` : Accepts a `multipart/form-data` DOCX file and returns first-pass detection stats (`counts`, `unique_values`, `samples`, `paragraphs`).
- `POST /redact` : Accepts a `multipart/form-data` DOCX file and returns the physical binary `.docx` payload, alongside an `x-pii-detections` HTTP header detailing the total number of replacements performed.

## Frontend
The project includes a production-ready Next.js frontend located in `frontend/`. It features a drag-and-drop document upload interface, an analysis validation summary, a redaction workflow, and secure document downloading. The UI is built with Tailwind CSS v4 and `lucide-react`.

## Local Setup

### Backend (Python)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# Start the API on http://localhost:8000
uvicorn src.api:app --reload
```

### Frontend (Next.js)
```bash
cd frontend
npm install

# Start the frontend on http://localhost:3000
npm run dev
```

## Environment Variables
The frontend optionally respects the following configuration:
- `NEXT_PUBLIC_API_URL`: Points to the FastAPI backend (Defaults to `http://localhost:8000` if absent).

*No API keys or secrets are required to run this repository.*

## Testing
- **Backend Tests**: 36 Pytest assertions covering detection, canonicalization, replacement, API structure, CLI interfaces, and strict address bounds. (`pytest`)
- **Frontend Tests**: Full static TypeScript validation and strict ESLint conformance. (`npm run lint && npm run build`)
- **End-to-End**: Verified by running the complete 127-page RHP DOCX through the `src/main.py` pipeline, generating a clean output with exactly 0 original PII leaks.

## Tradeoffs and Limitations
- **Address Conservatism vs False Positives**: Unstructured Indian addresses lack clear boundaries. The detection window uses explicit prefix/marker bounds (e.g. `Registered Office:` or `Gat No.`) to prevent aggressively capturing generic legal prose describing jurisdictions, eliminating false positives while retaining robust multiline recall.
- **RHP Dataset Skew**: The supplied Red Herring Prospectus lacked SSNs, Credit Cards, IPv4 addresses, and Dates of Birth. The detector logic works against synthetic benchmarks, but its behavior on real-world unstructured documents for these categories cannot be proven via the provided source material.
- **Document-Level Ground Truth**: Only a limited 13-item subset of the document was manually annotated for evaluation. The 100% precision/recall claims strictly apply ONLY to this subset and the synthetic benchmark. Full-document precision/recall is not claimed for the unannotated 127-page RHP.

## Project Structure
```
pii_redaction_backend/
├── src/                    # Core Python redaction engine
│   ├── document.py         # DOCX traversal and split-run redaction
│   ├── detectors.py        # 9 PII detectors + overlap resolution
│   ├── replacements.py     # Deterministic synthetic generators
│   ├── api.py              # FastAPI endpoints
│   ├── main.py             # CLI runner
│   └── evaluation.py       # Benchmark evaluation script
├── tests/                  # Pytest unit & integration tests
├── evaluation/             # Evaluation reports and ground truth JSON
├── frontend/               # Next.js React Application
│   ├── src/components/     # Polished UI elements
│   ├── src/app/            # Next.js App Router (page.tsx, layout.tsx)
│   └── src/lib/            # API client wrappers and types
├── input/                  # Source documents
├── output/                 # Redacted results (ignored by Git)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```
