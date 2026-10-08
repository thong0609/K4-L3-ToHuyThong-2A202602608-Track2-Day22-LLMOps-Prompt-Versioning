"""Tao 2 file log: mot cho PII, mot cho JSON."""
import sys
from pathlib import Path

log_pii   = Path(__file__).parent.parent / "evidence" / "04_pii_demo_log.txt"
log_json  = Path(__file__).parent.parent / "evidence" / "04_json_demo_log.txt"

# Clear + ghi
log_pii.write_text("", encoding="utf-8")
log_json.write_text("", encoding="utf-8")

import io, contextlib

# Capture stdout cua ham PII
from io import StringIO
buf_pii = StringIO()
buf_json = StringIO()

orig_stdout = sys.stdout

# Phan PII
sys.stdout = buf_pii
from src.guardrails_validator import demo_pii_guard
demo_pii_guard()
sys.stdout = orig_stdout
log_pii.write_text(buf_pii.getvalue(), encoding="utf-8")
print(buf_pii.getvalue())

# Phan JSON
sys.stdout = buf_json
from src.guardrails_validator import demo_json_guard
demo_json_guard()
sys.stdout = orig_stdout
log_json.write_text(buf_json.getvalue(), encoding="utf-8")
print(buf_json.getvalue())
