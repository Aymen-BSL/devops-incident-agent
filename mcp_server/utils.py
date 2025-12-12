import hashlib
from typing import List
from models import ErrorLog, ParsedLog

def _stack_summary(stack_trace: str, max_lines: int = 3) -> str:
    """Take the first few lines of the stack trace for a concise summary."""
    lines: List[str] = stack_trace.splitlines()
    head = lines[:max_lines]
    return "\n".join(head)

def make_fingerprint(log: ErrorLog) -> str:
    """
    Create a stable fingerprint for an error.

    For v1, we hash:
    - service
    - error_type
    - first line of stack trace

    This groups "same kind of error" together even if timestamps / request IDs differ.
    """
    stack_first_line = log["stack_trace"].splitlines()[-1] if log["stack_trace"] else ""
    key = f"{log['service']}|{log['error_type']}|{stack_first_line}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()

def normalize_log(log: ErrorLog) -> ParsedLog:
    """Convert a raw ErrorLog into a ParsedLog with fingerprint and summary."""
    fingerprint = make_fingerprint(log)
    summary = _stack_summary(log["stack_trace"])

    return {
        "service": log["service"],
        "environment": log["environment"],
        "error_type": log["error_type"],
        "severity": log["severity"],
        "message": log["message"],
        "fingerprint": fingerprint,
        "stack_summary": summary,
        "timestamp": log["timestamp"],
        "request_id": log["request_id"],
    }