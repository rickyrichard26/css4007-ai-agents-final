"""Thin wrapper around an OpenAI-compatible chat API.

Configuration comes from environment variables (see .env.example).
No secrets are ever stored in the repository.
"""
import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from src.errors import LLMConfigError, LLMError

load_dotenv()

DEFAULT_MODEL = "gpt-5.6-luna"


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMConfigError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return OpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        timeout=float(os.getenv("LLM_TIMEOUT", "30")),
    )


def call_llm(messages: list[dict], client: OpenAI | None = None) -> str:
    """Send chat messages to the model and return the raw text reply."""
    client = client or get_client()
    kwargs = {}
    # Some models reject a custom temperature, so it is only sent when set.
    temperature = os.getenv("LLM_TEMPERATURE")
    if temperature:
        kwargs["temperature"] = float(temperature)

    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", DEFAULT_MODEL),
            messages=messages,
            **kwargs,
        )
    except OpenAIError as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise LLMError("The model returned an empty response.")
    return content
