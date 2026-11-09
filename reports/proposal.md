# Project Proposal — Semester Week 10

## Project Title
**PhishGuard: An LLM-Powered Phishing Email Analyzer**

## Problem Description

Phishing is one of the most common ways attackers steal credentials and spread malware. Ordinary users often cannot tell a malicious email from a legitimate one, and they rarely understand *why* an email is suspicious.

PhishGuard accepts the text of an email (subject, sender, body) and uses an LLM to produce a **structured risk assessment**: a verdict, a risk score, the specific red flags found, a plain-language explanation, and a recommended action. Because the output is validated against a strict schema, it is consistent and machine-readable rather than free-form chat.

This matters because it turns a security-awareness skill into an on-demand tool: the user learns what to look for, not only whether one email is dangerous.

## Target Users

- Students and staff who receive suspicious emails and want a quick second opinion.
- Non-technical users who need red flags explained in plain language.
- Security-awareness trainers who want example analyses for teaching.

## Selected Difficulty

D - Basic LLM application with a single prompt-to-validated-output pipeline

## Expected Functionality

- Accept an email (subject, sender, body) via command line or a simple web form.
- Build a prompt that instructs the LLM to analyze the email as a security analyst.
- Request a JSON response with a fixed schema.
- Validate the JSON (required fields, allowed values, score range 0-100).
- Display a readable report: verdict, risk score, red flags, explanation, recommended action.
- Handle invalid input (empty or too long), malformed model output, and API failures with clear messages.

Output schema:

```json
{
  "verdict": "phishing | suspicious | legitimate",
  "risk_score": 0,
  "red_flags": [
    {"type": "urgency | suspicious_link | sender_mismatch | credential_request | attachment | other",
     "evidence": "short quote or description"}
  ],
  "explanation": "plain-language summary",
  "recommended_action": "what the user should do"
}
```

## Proposed Functions

| Name | Purpose | Input | Expected output | Dependencies |
|---|---|---|---|---|
| `validate_input(email)` | Reject empty or oversized input, trim whitespace | `dict` with subject, sender, body | cleaned `dict` or raises `InputError` | none |
| `build_prompt(email)` | Create the system and user prompt with schema instructions | cleaned email `dict` | list of chat messages | none |
| `call_llm(messages)` | Send the request to the LLM with timeout and retry | messages | raw model text | LLM API client |
| `parse_and_validate(raw_text)` | Parse JSON and check against schema | raw text | validated `dict` or raises `OutputError` | `json`, schema validator |
| `analyze_email(email)` | Orchestrate the full pipeline | email `dict` | validated result `dict` | all functions above |
| `format_report(result)` | Turn the result into readable text | result `dict` | formatted string | none |

Example signature:

```python
def analyze_email(email: dict) -> dict:
    """
    Validates the input, calls the LLM, validates the JSON output,
    and returns a structured phishing assessment.
    """
```

## Proposed Agent Tools

Not applicable — D level. The application is a single prompt-to-validated-output pipeline with no LLM-callable tools.

## Model Selection

- **Model:** `gpt-5.6-luna` through an OpenAI-compatible chat completions API. The model name is a configuration value, so it can be swapped for another provider or a local model (for example via Ollama) without code changes.
- **Approach:** API call with a low temperature (about 0.2) for consistent classification, a request for JSON-only output, and a 30-second timeout with up to 2 retries.
- **Secrets:** the API key is read from an environment variable. `.env` is listed in `.gitignore`, and a `.env.example` is provided.
- **Language:** Python.

## Architecture

```text
User Input (subject, sender, body)
        |
        v
  validate_input  --(invalid)--> clear error message
        |
        v
  build_prompt (role, rules, JSON schema)
        |
        v
      LLM API  --(timeout / error)--> retry, then friendly error
        |
        v
  parse_and_validate --(invalid JSON / bad values)--> retry once, then error
        |
        v
  format_report  -->  Output (verdict, score, red flags, advice)
```

## Example Requests

1. **Obvious phishing:** a fake "Your account will be suspended in 24 hours, verify now" email with a mismatched sender domain and a lookalike link. Expected: verdict `phishing`, high score, flags for urgency, suspicious link, and sender mismatch.
2. **Legitimate email:** a normal meeting reminder from a known contact with no links. Expected: verdict `legitimate`, low score, empty or minimal red flags.
3. **Borderline case:** an unexpected delivery notification with a tracking link but no credential request. Expected: verdict `suspicious`, medium score, a recommendation to verify through the official website.

## Evaluation Plan

Tests use a **mock LLM client**, so they are reproducible and need no API key. Minimum 5 required; planned 7:

| # | Test | Expected result |
|---|---|---|
| 1 | Valid phishing email (mocked valid JSON response) | Returns a valid result with verdict `phishing` |
| 2 | Valid legitimate email (mocked response) | Returns a valid result with verdict `legitimate` |
| 3 | Empty or whitespace-only email | `InputError` with a clear message, no LLM call |
| 4 | Oversized email | Rejected or truncated according to the documented limit |
| 5 | Model returns malformed JSON | Retry once, then a graceful `OutputError` |
| 6 | Model returns an out-of-range `risk_score` or an invalid `verdict` | Validation fails and is handled |
| 7 | API timeout or server error | Retries, then shows a friendly error without crashing |

In addition, I will run a small set of real emails (about 10 phishing and 10 legitimate samples that I write myself) against the real model and record accuracy and failure cases in the Week 16 report.

## Weekly Milestones

| Week | Plan |
|---|---|
| 10 (2-8 Nov) | Proposal, repository setup, project structure, `.gitignore`, `.env.example` |
| 11 (9-15 Nov) | LLM integration, first working request, basic README |
| 12 (16-22 Nov) | Prompt design, JSON schema, `parse_and_validate`, input validation, first tests |
| 13 (23-29 Nov) | Complete the `analyze_email` pipeline, `format_report`, CLI interface, more tests |
| 14 (30 Nov-6 Dec) | Complete the end-to-end workflow, improve usability, prompt refinement |
| 15 (7-13 Dec) | Retry and failure handling, expanded edge-case tests |
| 16 (14-20 Dec) | Run the full suite and the real-sample evaluation, analyze failures, improve, update docs |
| 17 (21-22 Dec) | Final README, results, AI-assistant disclosure statement, demo preparation, submission |

## Notes

- Significant changes to scope will be documented in the weekly reports.
- AI coding assistants will be used and disclosed in the final report.
