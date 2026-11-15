# PhishGuard: LLM-Powered Phishing Email Analyzer

CSS 4007 AI Agents Final Project, level D.

PhishGuard sends an email (sender, subject, body) to an LLM and returns a validated,
structured risk assessment: verdict, risk score, red flags, explanation and recommended action.

```text
Input -> validate_input -> build_prompt -> LLM (retry on failure)
      -> parse_and_validate (retry once) -> format_report -> Output
```

## Setup

Requires Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

Open `.env` and set `OPENAI_API_KEY`. Optionally set `MODEL_NAME` and `OPENAI_BASE_URL`
(for another OpenAI-compatible provider). Never commit `.env`.

## Run

```bash
python -m src.cli --file samples/phishing.json
python -m src.cli --file samples/legitimate.json
python -m src.cli --file samples/suspicious.json
python -m src.cli --file samples/prompt_injection.json
python -m src.cli --sender a@b.com --subject "Hi" --body "Meeting at 3 PM" --json
echo "Verify your password now" | python -m src.cli
```

Exit codes: 0 success, 2 invalid input, 3 model/API failure, 4 invalid model output.

## Test

Tests use a mock LLM, so they need no API key and no internet.

```bash
python -m pytest -v
```

## Evaluate with the real model

```bash
python -m evaluation.run_eval      # writes reports/evaluation-results.md
```

## Structure

```text
src/errors.py             exception types
src/llm_client.py         LLM API wrapper (timeout, error handling)
src/prompts.py            prompt construction (email treated as untrusted data)
src/validation.py         input validation
src/output_validation.py  JSON parsing and schema validation
src/analyzer.py           pipeline with retries
src/report.py             readable report
src/cli.py                command-line interface
tests/                    pytest suite (mock LLM)
samples/                  example emails
evaluation/               real-model evaluation script and eval set
reports/                  proposal and weekly reports
```

## Limits and design notes

- Email body limit: 10,000 characters. Longer input is rejected, not truncated.
- API failures: up to 2 retries with a short delay. Missing API key: no retry.
- Invalid model output: 1 retry, then a clear error.
- The email text is passed in the user message and the system prompt declares it untrusted,
  to reduce prompt-injection risk. This reduces the risk but does not remove it.
- The verdict is an AI assessment, not a guarantee. Verify suspicious emails through official channels.
