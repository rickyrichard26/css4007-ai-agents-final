import json

import pytest

from src.errors import OutputError
from src.output_validation import parse_and_validate
from tests.helpers import make_response


def test_valid_answer_is_parsed():
    result = parse_and_validate(make_response("phishing", 92))
    assert result["verdict"] == "phishing"
    assert result["risk_score"] == 92
    assert result["red_flags"] == [{"type": "urgency", "evidence": "account will be suspended"}]


def test_answer_wrapped_in_markdown_fence_is_accepted():
    raw = "```json\n" + make_response() + "\n```"
    assert parse_and_validate(raw)["verdict"] == "phishing"


def test_whole_number_float_score_is_converted_to_int():
    result = parse_and_validate(make_response(score=85.0))
    assert result["risk_score"] == 85
    assert isinstance(result["risk_score"], int)


def test_empty_red_flags_list_is_valid():
    result = parse_and_validate(make_response("legitimate", 4, flags=[]))
    assert result["red_flags"] == []


def test_extra_keys_from_the_model_are_dropped():
    raw = json.dumps({**json.loads(make_response()), "internal_notes": "ignore me"})
    assert "internal_notes" not in parse_and_validate(raw)


def test_text_fields_are_trimmed():
    raw = make_response(explanation="  Looks bad.  ", recommended_action="  Delete it.  ")
    result = parse_and_validate(raw)
    assert result["explanation"] == "Looks bad."
    assert result["recommended_action"] == "Delete it."


@pytest.mark.parametrize("raw", ["", "   ", None, 123])
def test_empty_or_non_text_answer_is_rejected(raw):
    with pytest.raises(OutputError):
        parse_and_validate(raw)


@pytest.mark.parametrize("raw", ["not json at all", "{'verdict': 'phishing'}", '{"verdict": '])
def test_invalid_json_is_rejected(raw):
    with pytest.raises(OutputError, match="valid JSON"):
        parse_and_validate(raw)


@pytest.mark.parametrize("raw", ["[1, 2, 3]", '"just a string"', "42"])
def test_json_that_is_not_an_object_is_rejected(raw):
    with pytest.raises(OutputError, match="JSON object"):
        parse_and_validate(raw)


@pytest.mark.parametrize("verdict", ["dangerous", "PHISHING", "", None, 1])
def test_invalid_verdict_is_rejected(verdict):
    with pytest.raises(OutputError, match="verdict"):
        parse_and_validate(make_response(verdict=verdict))


@pytest.mark.parametrize("score", [-1, 101, 150, 85.5, "high", "90", None, True])
def test_invalid_risk_score_is_rejected(score):
    with pytest.raises(OutputError, match="risk_score"):
        parse_and_validate(make_response(score=score))


@pytest.mark.parametrize("score", [0, 100])
def test_score_boundaries_are_accepted(score):
    assert parse_and_validate(make_response(score=score))["risk_score"] == score


def test_missing_risk_score_is_rejected():
    data = json.loads(make_response())
    del data["risk_score"]
    with pytest.raises(OutputError, match="risk_score"):
        parse_and_validate(json.dumps(data))


def test_red_flags_must_be_a_list():
    with pytest.raises(OutputError, match="red_flags"):
        parse_and_validate(make_response(flags="urgency"))


@pytest.mark.parametrize(
    "flag",
    [
        "urgency",                                      # not an object
        {"type": "made_up", "evidence": "x"},           # unknown type
        {"type": "urgency"},                            # missing evidence
        {"type": "urgency", "evidence": "   "},         # blank evidence
        {"type": "urgency", "evidence": 5},             # evidence not text
    ],
)
def test_invalid_red_flag_is_rejected(flag):
    with pytest.raises(OutputError):
        parse_and_validate(make_response(flags=[flag]))


@pytest.mark.parametrize("field", ["explanation", "recommended_action"])
@pytest.mark.parametrize("value", ["", "   ", None, 5])
def test_missing_or_blank_text_fields_are_rejected(field, value):
    with pytest.raises(OutputError, match=field):
        parse_and_validate(make_response(**{field: value}))