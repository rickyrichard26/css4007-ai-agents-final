"""Parse and validate the model's JSON answer.

The model is not trusted to follow the schema, so every field is checked.
"""
import json
import re

from src.errors import OutputError

VALID_VERDICTS = ("phishing", "suspicious", "legitimate")
# The risk score must fall in the range that belongs to the verdict.
VERDICT_SCORE_RANGES = {
    "legitimate": (0, 30),
    "suspicious": (31, 70),
    "phishing": (71, 100),
}
VALID_FLAG_TYPES = (
    "urgency",
    "suspicious_link",
    "sender_mismatch",
    "credential_request",
    "attachment",
    "other",
)


def _strip_code_fence(text: str) -> str:
    """Models sometimes wrap JSON in ```json ... ``` even when told not to."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_and_validate(raw_text: str) -> dict:
    """Return a validated result dict or raise OutputError."""
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise OutputError("The model returned an empty answer.")

    try:
        data = json.loads(_strip_code_fence(raw_text))
    except json.JSONDecodeError as exc:
        raise OutputError(f"The model answer is not valid JSON ({exc.msg}).") from exc

    if not isinstance(data, dict):
        raise OutputError("The model answer must be a JSON object.")

    verdict = data.get("verdict")
    if verdict not in VALID_VERDICTS:
        raise OutputError(f"Invalid verdict: {verdict!r}.")

    score = data.get("risk_score")
    if isinstance(score, float) and score.is_integer():
        score = int(score)
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        raise OutputError(f"risk_score must be an integer from 0 to 100, got {score!r}.")

    low, high = VERDICT_SCORE_RANGES[verdict]
    if not low <= score <= high:
        raise OutputError(
            f"The verdict {verdict!r} does not match risk_score {score} "
            f"(expected {low}-{high})."
        )

    flags = data.get("red_flags")
    if not isinstance(flags, list):
        raise OutputError("red_flags must be a list.")
    clean_flags = []
    for flag in flags:
        if not isinstance(flag, dict):
            raise OutputError("Each red flag must be an object.")
        flag_type, evidence = flag.get("type"), flag.get("evidence")
        if flag_type not in VALID_FLAG_TYPES:
            raise OutputError(f"Invalid red flag type: {flag_type!r}.")
        if not isinstance(evidence, str) or not evidence.strip():
            raise OutputError("Each red flag needs non-empty evidence text.")
        clean_flags.append({"type": flag_type, "evidence": evidence.strip()})

    for field in ("explanation", "recommended_action"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise OutputError(f"{field} must be non-empty text.")

    return {
        "verdict": verdict,
        "risk_score": score,
        "red_flags": clean_flags,
        "explanation": data["explanation"].strip(),
        "recommended_action": data["recommended_action"].strip(),
    }