from __future__ import annotations
import tempfile
import shutil
import os
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .service import analyze_docx
from .document import redact_docx

app=FastAPI(title="PII Redaction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status":"ok","service":"pii-redaction"}

@app.post("/analyze")
async def analyze(file: UploadFile=File(...)):
    if not file.filename or not file.filename.lower().endswith('.docx'):
        raise HTTPException(400,"Only .docx files are supported")
    with tempfile.TemporaryDirectory() as td:
        src=Path(td)/"input.docx"
        src.write_bytes(await file.read())
        return analyze_docx(src)

@app.post("/redact")
async def redact(background_tasks: BackgroundTasks, file: UploadFile=File(...)):
    if not file.filename or not file.filename.lower().endswith('.docx'):
        raise HTTPException(400,"Only .docx files are supported")
    td=tempfile.mkdtemp()
    
    def cleanup():
        shutil.rmtree(td, ignore_errors=True)
        
    background_tasks.add_task(cleanup)
    
    src=Path(td)/"input.docx"; out=Path(td)/"redacted.docx"
    src.write_bytes(await file.read())
    spans,_=redact_docx(src,out)
    return FileResponse(out, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="redacted_output.docx", headers={"X-PII-Detections":str(len(spans))})
