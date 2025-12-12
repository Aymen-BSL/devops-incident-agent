from fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import json

from models import ParsedLog, ErrorLog
from utils import normalize_log
from db import init_db, get_known_error, insert_incident, upsert_known_error

load_dotenv()

mcp = FastMCP(name="DevOps Incident Agent")


@mcp.tool()
def analyze_log(log: ErrorLog) -> dict:
    """
    Normalize a raw error log and compute a fingerprint.

    n8n will pass the JSON body from the webhook directly as 'log'.
    We return a dict so n8n can use fields like fingerprint, service, etc.
    """
    parsed = normalize_log(log)
    return parsed


@mcp.tool()
def lookup_known_error(fingerprint: str) -> str:
    """
    Check if we have seen this error before.

    Returns a human-readable summary string for now:
    - If known: includes occurrences count.
    - If unknown: returns 'NOT_FOUND'.
    """
    ke = get_known_error(fingerprint)
    if ke is None:
        return "NOT_FOUND"

    return (
        f"Known error #{ke['id']} (service={ke['service']}, error_type={ke['error_type']}): "
        f"{ke['description']} | suggested fix: {ke['suggested_fix']} | "
        f"occurrences={ke['occurrences']}, last_seen_at={ke['last_seen_at']}"
    )

@mcp.tool()
def save_known_error(
    fingerprint: str,
    description: str,
    suggested_fix: str,
    service: str = "",
    error_type: str = "",
    timestamp: str = "",
) -> str:
    """
    Save or update a known error record for the given fingerprint.
    n8n will call this after the LLM produces a suggested fix.
    We build a minimal ParsedLog for the DB helper.
    """
    parsed: ParsedLog = {
        "service": service or "unknown",
        "environment": "production",  # optional, you can pass real env if available
        "error_type": error_type or "unknown",
        "severity": "unknown",
        "message": "",
        "fingerprint": fingerprint,
        "stack_summary": "",
        "timestamp": timestamp or "",
        "request_id": "",
    }
    ke = upsert_known_error(parsed, description, suggested_fix)
    return f"Saved known error #{ke['id']} (fingerprint={fingerprint})"

@mcp.tool()
def record_incident(log: ErrorLog) -> str:
    """
    Store a new incident in the database.

    For v1, we don't auto-generate description/fix here,
    just record it so it can be inspected or used later.
    """
    parsed = normalize_log(log)
    raw_json = json.dumps(log, ensure_ascii=False)
    incident = insert_incident(parsed, raw_json)
    return (
        f"Recorded incident #{incident['id']} for fingerprint={incident['fingerprint']} "
        f"(service={incident['service']}, error_type={incident['error_type']})"
    )


if __name__ == "__main__":
    # Ensure DB tables exist before starting
    init_db()

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000,
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ],
    )
