"""First working request: send one sample email to the LLM and print the raw reply.

Run from the project root:  python -m src.first_request
"""
from src.llm_client import LLMError, call_llm
from src.prompts import build_prompt

SAMPLE_EMAIL = {
    "sender": "security@paypa1-support.com",
    "subject": "Your account will be suspended in 24 hours",
    "body": (
        "Dear customer, we detected unusual activity. "
        "Verify your password immediately at http://paypa1-secure-login.com/verify "
        "or your account will be permanently closed."
    ),
}

if __name__ == "__main__":
    try:
        print(call_llm(build_prompt(SAMPLE_EMAIL)))
    except LLMError as exc:
        print(f"Error: {exc}")
