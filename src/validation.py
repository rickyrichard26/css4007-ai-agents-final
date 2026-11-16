"""Input validation: reject unusable emails before spending an LLM call."""
from src.errors import InputError

MAX_BODY_CHARS = 10_000   # documented limit for the email body
MAX_HEADER_CHARS = 500    # limit for sender and subject


def validate_input(email: dict) -> dict:
    """Return a cleaned copy of the email or raise InputError."""
    if not isinstance(email, dict):
        raise InputError("The email must be a dict with sender, subject and body.")

    cleaned = {}
    for field in ("sender", "subject", "body"):
        value = email.get(field, "")
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise InputError(f"'{field}' must be text.")
        cleaned[field] = value.strip()

    if not cleaned["body"]:
        raise InputError("The email body is empty. Provide the email text to analyze.")
    if len(cleaned["body"]) > MAX_BODY_CHARS:
        raise InputError(
            f"The email body is too long ({len(cleaned['body'])} characters). "
            f"The limit is {MAX_BODY_CHARS}."
        )
    for field in ("sender", "subject"):
        if len(cleaned[field]) > MAX_HEADER_CHARS:
            raise InputError(f"'{field}' is too long (limit {MAX_HEADER_CHARS} characters).")
    return cleaned
