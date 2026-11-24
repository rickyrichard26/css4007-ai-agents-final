import pytest

from src.analyzer import analyze_email
from src.errors import InputError, LLMConfigError, LLMError, OutputError
from tests.helpers import LEGIT_EMAIL, PHISHING_EMAIL, FakeLLM, make_response


def no_sleep(_seconds):
    pass


# Test 1: valid phishing email
def test_phishing_email_gets_valid_phishing_result():
    llm = FakeLLM(make_response("phishing", 92))
    result = analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)
    assert result["verdict"] == "phishing"
    assert result["risk_score"] == 92
    assert result["red_flags"][0]["type"] == "urgency"


# Test 2: valid legitimate email
def test_legitimate_email_gets_valid_legitimate_result():
    llm = FakeLLM(make_response("legitimate", 5, flags=[]))
    result = analyze_email(LEGIT_EMAIL, llm=llm, sleep=no_sleep)
    assert result["verdict"] == "legitimate"
    assert result["red_flags"] == []


# Test 3: empty email is rejected and the LLM is never called
@pytest.mark.parametrize("body", ["", "   \n  ", None])
def test_empty_email_is_rejected_without_calling_llm(body):
    llm = FakeLLM(make_response())
    with pytest.raises(InputError):
        analyze_email({"sender": "a@b.com", "subject": "x", "body": body}, llm=llm)
    assert llm.calls == 0


# Test 4: oversized email is rejected
def test_oversized_email_is_rejected():
    llm = FakeLLM(make_response())
    with pytest.raises(InputError, match="too long"):
        analyze_email({"body": "a" * 10_001}, llm=llm)
    assert llm.calls == 0


# Test 5: malformed JSON -> retry once, then a graceful OutputError
def test_malformed_json_is_retried_once_then_fails_gracefully():
    llm = FakeLLM("this is not json")
    with pytest.raises(OutputError):
        analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)
    assert llm.calls == 2


def test_malformed_json_then_valid_json_succeeds_on_retry():
    llm = FakeLLM("not json", make_response())
    result = analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)
    assert result["verdict"] == "phishing"
    assert llm.calls == 2


# Test 6: invalid verdict or out-of-range score is rejected
@pytest.mark.parametrize(
    "overrides",
    [
        {"verdict": "dangerous"},
        {"risk_score": 150},
        {"risk_score": -1},
        {"risk_score": "high"},
        {"red_flags": [{"type": "made_up", "evidence": "x"}]},
        {"explanation": ""},
    ],
)
def test_invalid_model_output_is_rejected(overrides):
    llm = FakeLLM(make_response(**overrides))
    with pytest.raises(OutputError):
        analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)


# Test 7: API timeout / server error -> retries, then a friendly error
def test_api_failure_is_retried_then_raises_llm_error():
    llm = FakeLLM(LLMError("timeout"))
    with pytest.raises(LLMError, match="could not be reached"):
        analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)
    assert llm.calls == 3  # first try + 2 retries


def test_api_failure_then_success_recovers():
    llm = FakeLLM(LLMError("timeout"), make_response())
    result = analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)
    assert result["verdict"] == "phishing"


def test_missing_api_key_is_not_retried():
    llm = FakeLLM(LLMConfigError("no key"))
    with pytest.raises(LLMConfigError):
        analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)
    assert llm.calls == 1


def test_json_wrapped_in_markdown_fence_is_accepted():
    llm = FakeLLM("```json\n" + make_response() + "\n```")
    assert analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)["verdict"] == "phishing"


def test_inconsistent_verdict_and_score_is_retried_then_succeeds():
    llm = FakeLLM(make_response("legitimate", 95), make_response("phishing", 95))
    result = analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)
    assert result["verdict"] == "phishing"
    assert llm.calls == 2


def test_always_inconsistent_answer_fails_after_one_retry():
    llm = FakeLLM(make_response("legitimate", 95))
    with pytest.raises(OutputError, match="does not match"):
        analyze_email(PHISHING_EMAIL, llm=llm, sleep=no_sleep)
    assert llm.calls == 2