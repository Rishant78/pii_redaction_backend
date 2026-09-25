from __future__ import annotations
import argparse
from pathlib import Path
from .document import redact_docx
from .service import analyze_docx


def main():
    parser=argparse.ArgumentParser(description="PII Redaction Tool")
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--analyze',action='store_true')
    args=parser.parse_args()
    if args.analyze:
        import json
        print(json.dumps(analyze_docx(args.input),indent=2,ensure_ascii=False))
        return
    spans,generator=redact_docx(args.input,args.output)
    print(f"Created: {args.output}")
    print(f"Unique PII values replaced: {len(spans)}")
    for s in spans:
        lookup_val = s.canonical_text if s.canonical_text else s.text
        print(f"{s.pii_type.value}: {s.text} -> {generator.by_type[s.pii_type][lookup_val]}")

if __name__=='__main__': main()
