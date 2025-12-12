from typing import TypedDict, Literal

LogLevel = Literal["ERROR", "WARN", "INFO"]
Environment = Literal["production", "staging", "development"]

class ErrorLog(TypedDict):
    """Raw error log as received from the simulator or any app."""
    service: str
    environment: Environment
    timestamp: str
    level: LogLevel
    message: str
    error_type: str
    severity: str
    stack_trace: str
    request_id: str

class ParsedLog(TypedDict):
    """Normalized version of the error log, with a fingerprint."""
    service: str
    environment: Environment
    error_type: str
    severity: str
    message: str
    fingerprint: str
    stack_summary: str
    timestamp: str
    request_id: str


class KnownError(TypedDict):
    """Row from the known_errors table."""
    id: int
    fingerprint: str
    error_type: str
    service: str
    description: str
    suggested_fix: str
    first_seen_at: str
    last_seen_at: str
    occurrences: int


class Incident(TypedDict):
    """Row from the incidents table."""
    id: int
    fingerprint: str
    service: str
    environment: Environment
    error_type: str
    severity: str
    message: str
    stack_summary: str
    raw_log: str
    created_at: str
