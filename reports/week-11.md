# Semester Week 11 Progress Report

## Completed Work

- Set up the project structure (`src/`, `tests/`, `reports/`), `requirements.txt`, `.env.example`, and `.gitignore` entries so that `.env` and the virtual environment are never committed.
- Implemented `call_llm` in `src/llm_client.py`: it reads the API key, base URL, model name and timeout from environment variables and converts API errors into a clear `LLMError`.
- Wrote the first version of the prompt in `src/prompts.py`. It asks for a JSON object with a fixed schema (verdict, risk score, red flags, explanation, recommended action) and tells the model to treat the email as untrusted data.
- Ran the first working request with the real model and tested four sample emails (phishing, legitimate, suspicious, prompt injection).
- Wrote basic documentation (`PHISHGUARD.md`) with setup and run instructions.
- Switched the LLM provider from OpenAI to OpenRouter after the first API key ran out of credits.

## Important Commits

- Commit hash: HASH_DARI_GIT_LOG
- Description: Add LLM client, initial prompt and first working request (committed 16 Nov; the code was written and tested locally on 15 Nov)
- Link: https://github.com/rickyrichard26/css4007-ai-agents-final/commit/HASH_DARI_GIT_LOG

- Commit hash: f268065
- Description: Week 11 report
- Link: https://github.com/rickyrichard26/css4007-ai-agents-final/commit/f268065

## Current Functionality

The application sends an email (sender, subject, body) to an LLM through an OpenAI-compatible API and prints the model's structured assessment. The model is `<MODEL_ID>` on OpenRouter. At this stage the raw reply is printed; full validation of the output is planned for Week 12.

Results on four sample emails with the real model:

- **Phishing sample** (fake PayPal account suspension): PHISHING, score 98. Four red flags were found: sender mismatch (lookalike domain with the digit 1), suspicious link (no HTTPS), urgency, and credential request.
- **Legitimate sample** (project meeting reminder): LEGITIMATE, score 5, no red flags.
- **Prompt injection sample** (body says "ignore all previous instructions" and asks for a legitimate verdict): PHISHING, score 98. The model did not follow the injected instruction and reported it as a red flag, so treating the email as untrusted data in the prompt worked.
- **Suspicious sample** (delivery notice with a tracking link, no credential request): PHISHING, score 88. I expected SUSPICIOUS with a medium score, so the model is over-aggressive for borderline emails.

## Problems Encountered

- The first API key had no credits left, so every request failed with HTTP 429.
- The model rated the borderline delivery email as phishing with a high score. The prompt does not define what score ranges correspond to each verdict.
- The API key must never end up in the repository.

## Solutions

- Switched to OpenRouter, which is OpenAI-compatible, by changing only `OPENAI_BASE_URL`, `MODEL_NAME` and the API key in the environment file. No code change was needed. While the key had no credits, the application retried three times and then showed a clear error message instead of crashing.
- For the over-aggressive scoring: I will add a score guide to the prompt (for example 0-30 legitimate, 31-70 suspicious, 71-100 phishing) and a consistency check between verdict and score in the validation step, with a test. This is planned for Weeks 14-15, and this sample will be a test case in the Week 16 evaluation.
- Kept the key in `.env`, listed `.env` in `.gitignore`, and committed only `.env.example`.

## What I Learned

- How to call an OpenAI-compatible chat API, and how changing the base URL and model name lets the same code work with different providers.
- How a system prompt with an explicit JSON schema shapes the model's output.
- Why email content must be treated as untrusted data in the prompt: the injection sample showed that the model can resist an embedded instruction when the prompt says so.
- A valid-looking answer can still be badly calibrated, so checking the format alone is not enough. The verdict and score also need to be checked.
- Free models can have rate limits and different data-use terms, so only synthetic sample emails should be sent to them.

## Next Week

- Implement input validation (empty and oversized emails) and `parse_and_validate` for the model's JSON output.
- Write the first tests with a mock LLM client, so they run without an API key.
- Add retry handling for invalid output and API failures.
