import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from docx import Document
import tempfile
import pytest

from src.api import app
from src.main import main
from src.models import Span, PIIType
from src.replacements import ReplacementGenerator

client = TestClient(app)

def test_api_cors_preflight():
    # Test that CORS headers are present for localhost:3000
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/redact", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

def test_api_redact_endpoint_cleanup(tmp_path):
    doc_path = tmp_path / "test.docx"
    doc = Document()
    doc.add_paragraph("Kushal Hegde")
    doc.save(doc_path)
    
    with open(doc_path, "rb") as f:
        # Patch tempfile.mkdtemp to spy on the returned directory
        original_mkdtemp = tempfile.mkdtemp
        temp_dirs = []
        def mocked_mkdtemp(*args, **kwargs):
            d = original_mkdtemp(*args, **kwargs)
            temp_dirs.append(d)
            return d
            
        with patch("tempfile.mkdtemp", side_effect=mocked_mkdtemp):
            response = client.post("/redact", files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
            assert response.status_code == 200
            assert "X-PII-Detections" in response.headers
            
        # Background tasks in TestClient run synchronously after response
        # Verify cleanup
        assert len(temp_dirs) == 1
        assert not os.path.exists(temp_dirs[0])

def test_cli_canonical_lookup_keyerror_fix(tmp_path):
    # Test that src.main.main() doesn't throw a KeyError when s.text differs from canonical_text
    
    test_spans = [
        Span(0, 25, "KSH INTERNATIONAL LIMITED", PIIType.ORGANIZATION, 1.0, "mock", canonical_text="Ksh International Limited")
    ]
    
    generator = ReplacementGenerator()
    # The registry holds canonical_text
    generator.generate("Ksh International Limited", PIIType.ORGANIZATION)
    
    test_args = ["main.py", "--input", "mock.docx", "--output", "mock_out.docx"]
    
    with patch("sys.argv", test_args):
        with patch("src.main.redact_docx", return_value=(test_spans, generator)):
            # If it throws a KeyError, this test will fail
            main()
