import json

from src.cli import main
from src.errors import LLMError
from src.report import format_report
from tests.helpers import make_response

RESULT = json.loads(make_response("phishing", 92))


def test_format_report_contains_key_information():
    text = format_report(RESULT)
    assert "PHISHING" in text
    assert "92/100" in text
    assert "[urgency]" in text


def test_format_report_handles_no_red_flags():
    assert "(none found)" in format_report({**RESULT, "red_flags": []})


def test_cli_prints_report_for_valid_file(tmp_path, capsys):
    email_file = tmp_path / "mail.json"
    email_file.write_text(json.dumps({"sender": "a@b.com", "subject": "s", "body": "hello"}))
    code = main(["--file", str(email_file)], analyze=lambda email: RESULT)
    assert code == 0
    assert "Verdict: PHISHING" in capsys.readouterr().out


def test_cli_reports_missing_file(capsys):
    assert main(["--file", "does-not-exist.json"]) == 2
    assert "File not found" in capsys.readouterr().err


def test_cli_reports_empty_body(capsys):
    assert main(["--body", "   "]) == 2
    assert "empty" in capsys.readouterr().err


def test_cli_reports_model_failure(capsys):
    def failing(_email):
        raise LLMError("timeout")

    assert main(["--body", "hello"], analyze=failing) == 3
    assert "timeout" in capsys.readouterr().err
