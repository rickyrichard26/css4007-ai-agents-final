"""Main pipeline: validate input -> build prompt -> call LLM -> validate output."""
import time

from src.errors import LLMConfigError, LLMError, OutputError
from src.llm_client import call_llm
from src.output_validation import parse_and_validate
from src.prompts import build_prompt
from src.validation import validate_input

RETRY_DELAY_SECONDS = 1.0


def analyze_email(
    email: dict,
    llm=call_llm,
    max_llm_retries: int = 2,
    max_output_retries: int = 1,
    sleep=time.sleep,
) -> dict:
    """Return a validated phishing assessment for the email.

    llm: a function that takes chat messages and returns text. It is injectable
         so that tests can use a mock instead of the real API.
    max_llm_retries: extra attempts after an API failure (timeouts, server errors).
    max_output_retries: extra attempts after the model returns invalid output.
    """
    cleaned = validate_input(email)          # raises InputError, no LLM call made
    messages = build_prompt(cleaned)

    llm_failures = 0
    output_failures = 0
    while True:
        try:
            raw = llm(messages)
        except LLMConfigError:
            raise                            # retrying a missing API key is pointless
        except LLMError as exc:
            llm_failures += 1
            if llm_failures > max_llm_retries:
                raise LLMError(
                    f"The model could not be reached after {llm_failures} attempts: {exc}"
                ) from exc
            sleep(RETRY_DELAY_SECONDS * llm_failures)
            continue

        try:
            return parse_and_validate(raw)
        except OutputError as exc:
            output_failures += 1
            if output_failures > max_output_retries:
                raise OutputError(
                    f"The model gave an invalid answer {output_failures} times: {exc}"
                ) from exc
