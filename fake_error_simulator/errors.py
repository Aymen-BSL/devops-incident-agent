import random
import json
from datetime import datetime, timezone
from faker import Faker

fake = Faker()

# Define some realistic error scenarios
ERROR_TEMPLATES = [
    {
        "service": "billing-api",
        "message": "Payment gateway timeout",
        "error_type": "TimeoutError",
        "severity": "high",
        "probability": 0.1
    },
    {
        "service": "auth-service",
        "message": "User authentication failed",
        "error_type": "AuthenticationError",
        "severity": "medium",
        "probability": 0.3
    },
    {
        "service": "inventory-service",
        "message": "Database connection reset",
        "error_type": "ConnectionError",
        "severity": "high",
        "probability": 0.1
    },
    {
        "service": "frontend-app",
        "message": "Resource not found",
        "error_type": "NotFoundError",
        "severity": "low",
        "probability": 0.5
    },
    {
        "service": "notification-service",
        "message": "Email delivery failed",
        "error_type": "SMTPException",
        "severity": "medium",
        "probability": 0.2
    }
]

SIMULATED_ENVIRONMENTS = ["production", "staging", "development"]

def generate_fake_stack_trace(error_type, message):
    """Generates a plausible-looking python stack trace."""
    frames = [
        "File \"/app/src/main.py\", line 45, in process_request\n    return handler.handle(request)",
        "File \"/app/src/handler.py\", line 28, in handle\n    result = self.service.execute(data)",
        f"File \"/app/src/services/business_logic.py\", line 102, in execute\n    raise {error_type}(\"{message}\")"
    ]
    trace = "Traceback (most recent call last):\n"
    for frame in frames:
        trace += f"  {frame}\n"
    trace += f"{error_type}: {message}"
    return trace

def generate_error():
    """Generates a random error object based on templates."""
    template = random.choice(ERROR_TEMPLATES)
    
    # Generate dynamic data
    request_id = f"req_{fake.uuid4()[:8]}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    error_payload = {
        "service": template["service"],
        "environment": random.choice(SIMULATED_ENVIRONMENTS),
        "timestamp": timestamp,
        "level": "ERROR",
        "message": template["message"],
        "error_type": template["error_type"],
        "severity": template["severity"],
        "stack_trace": generate_fake_stack_trace(template["error_type"], template["message"]),
        "request_id": request_id
    }
    
    return error_payload
