"""Shared helpers for tests. No real API is ever called."""
import json

PHISHING_EMAIL = {
    "sender": "security@paypa1-support.com",
    "subject": "Your account will be suspended",
    "body": "Verify your password now at http://paypa1-secure-login.com/verify",
}
LEGIT_EMAIL = {
    "sender": "dewi@example-university.ac.id",
    "subject": "Meeting on Thursday",
    "body": "Hi team, our project meeting is Thursday at 3 PM in Room B204.",
}


def make_response(verdict="phishing", score=92, flags=None, **overrides):
    """Build a valid model answer as JSON text; overrides let tests break it."""
    if flags is None:
        flags = [{"type": "urgency", "evidence": "account will be suspended"}]
    data = {
        "verdict": verdict,
        "risk_score": score,
        "red_flags": flags,
        "explanation": "This email pressures the reader to act quickly.",
        "recommended_action": "Do not click the link. Delete the email.",
    }
    data.update(overrides)
    return json.dumps(data)


class FakeLLM:
    """Mock LLM: returns or raises the queued items one by one."""

    def __init__(self, *items):
        self.items = list(items)
        self.calls = 0
        self.last_messages = None

    def __call__(self, messages):
        self.calls += 1
        self.last_messages = messages
        item = self.items.pop(0) if len(self.items) > 1 else self.items[0]
        if isinstance(item, Exception):
            raise item
        return item
