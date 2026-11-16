"""Unit tests for src/validation.py (input validation)."""
import pytest

from src.errors import InputError
from src.validation import MAX_BODY_CHARS, MAX_HEADER_CHARS, validate_input


def test_valid_email_is_returned_with_whitespace_trimmed():
    cleaned = validate_input(
        {"sender": "  a@b.com ", "subject": " Hello ", "body": "\n Meeting at 3 PM \n"}
    )
    assert cleaned == {"sender": "a@b.com", "subject": "Hello", "body": "Meeting at 3 PM"}


def test_missing_sender_and_subject_default_to_empty_text():
    cleaned = validate_input({"body": "Only a body"})
    assert cleaned["sender"] == ""
    assert cleaned["subject"] == ""


def test_original_input_is_not_modified():
    original = {"sender": " a@b.com ", "subject": "s", "body": " text "}
    validate_input(original)
    assert original["body"] == " text "


@pytest.mark.parametrize("body", ["", "   ", "\n\t  \n", None])
def test_empty_body_is_rejected(body):
    with pytest.raises(InputError, match="empty"):
        validate_input({"sender": "a@b.com", "subject": "s", "body": body})


def test_missing_body_key_is_rejected():
    with pytest.raises(InputError):
        validate_input({"sender": "a@b.com", "subject": "s"})


def test_body_at_the_limit_is_accepted():
    cleaned = validate_input({"body": "a" * MAX_BODY_CHARS})
    assert len(cleaned["body"]) == MAX_BODY_CHARS


def test_body_over_the_limit_is_rejected():
    with pytest.raises(InputError, match="too long"):
        validate_input({"body": "a" * (MAX_BODY_CHARS + 1)})


@pytest.mark.parametrize("field", ["sender", "subject"])
def test_overlong_sender_or_subject_is_rejected(field):
    email = {"sender": "a@b.com", "subject": "s", "body": "text"}
    email[field] = "x" * (MAX_HEADER_CHARS + 1)
    with pytest.raises(InputError, match=field):
        validate_input(email)


@pytest.mark.parametrize("bad_email", [None, "just a string", ["body"], 42])
def test_non_dict_input_is_rejected(bad_email):
    with pytest.raises(InputError):
        validate_input(bad_email)


@pytest.mark.parametrize("field", ["sender", "subject", "body"])
def test_non_text_field_is_rejected(field):
    email = {"sender": "a@b.com", "subject": "s", "body": "text"}
    email[field] = 123
    with pytest.raises(InputError, match=field):
        validate_input(email)