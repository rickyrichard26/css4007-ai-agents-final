"""Command-line interface.

Examples:
  python -m src.cli --file samples/phishing.json
  python -m src.cli --sender a@b.com --subject "Hi" --body "Meeting at 3pm"
  python -m src.cli --file samples/phishing.json --json
"""
import argparse
import json
import sys

from src.analyzer import analyze_email
from src.errors import InputError, LLMError, OutputError
from src.report import format_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PhishGuard: LLM phishing email analyzer")
    parser.add_argument("--file", help="JSON file with sender, subject and body")
    parser.add_argument("--sender", default="")
    parser.add_argument("--subject", default="")
    parser.add_argument("--body", help="email body (or pipe it through stdin)")
    parser.add_argument("--json", action="store_true", help="print the raw JSON result")
    return parser


def _load_email(args) -> dict:
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError as exc:
            raise InputError(f"File not found: {args.file}") from exc
        except json.JSONDecodeError as exc:
            raise InputError(f"{args.file} is not valid JSON: {exc.msg}") from exc
    body = args.body
    if body is None:
        body = "" if sys.stdin.isatty() else sys.stdin.read()
    return {"sender": args.sender, "subject": args.subject, "body": body}


def main(argv=None, analyze=analyze_email) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = analyze(_load_email(args))
    except InputError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    except LLMError as exc:
        print(f"Could not get an answer from the model: {exc}", file=sys.stderr)
        return 3
    except OutputError as exc:
        print(f"The model returned an unusable answer: {exc}", file=sys.stderr)
        return 4
    print(json.dumps(result, indent=2) if args.json else format_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
