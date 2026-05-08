"""
Helpers for sanitising log payloads.

We strip authentication / secret values from headers and payment / webhook
bodies before they hit the log pipeline so that operational logs never carry
credentials, signatures, or user-identifying payment details verbatim.
"""
from typing import Any, Mapping

# Header names (lower-cased) whose values should never be logged.
SENSITIVE_HEADERS = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
    "x-yookassa-signature",
    "x-telegram-bot-api-secret-token",
}

# Top-level keys in webhook / metadata payloads to redact when logging.
SENSITIVE_BODY_KEYS = {
    "token",
    "card",
    "card_token",
    "secret",
    "secret_key",
    "api_key",
    "password",
    "phone",
    "email",
    "authorization_details",
    "payment_token",
    "recipient",
    "payment_method",
}


def sanitise_headers(headers: Mapping[str, str]) -> dict:
    """Return a copy of headers with sensitive values masked."""
    if not headers:
        return {}
    sanitised: dict = {}
    for name, value in headers.items():
        if name.lower() in SENSITIVE_HEADERS:
            sanitised[name] = "***REDACTED***"
        else:
            sanitised[name] = value
    return sanitised


def sanitise_body(body: Any, depth: int = 0) -> Any:
    """
    Return a copy of a webhook body with sensitive keys redacted.

    Walks the structure to a small depth (containers can be nested).
    """
    if depth > 5:
        return "***TRUNCATED***"

    if isinstance(body, dict):
        cleaned: dict = {}
        for key, value in body.items():
            if isinstance(key, str) and key.lower() in SENSITIVE_BODY_KEYS:
                cleaned[key] = "***REDACTED***"
            else:
                cleaned[key] = sanitise_body(value, depth + 1)
        return cleaned

    if isinstance(body, list):
        return [sanitise_body(item, depth + 1) for item in body]

    return body
