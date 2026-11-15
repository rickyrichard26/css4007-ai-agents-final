"""Exceptions used across PhishGuard."""


class InputError(Exception):
    """The user's email input is missing or unusable."""


class LLMError(Exception):
    """The LLM could not be reached or returned nothing usable."""


class LLMConfigError(LLMError):
    """The LLM is misconfigured (for example, no API key). Retrying will not help."""


class OutputError(Exception):
    """The model answered, but not in the required, valid format."""
