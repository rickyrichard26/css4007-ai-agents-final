# Semester Week 10 Progress Report

## Completed Work

- Forked the instructor repository and cloned it locally.
- Read the shared README and the D-level requirements.
- Chose level D and the project topic: PhishGuard, an LLM-powered phishing email analyzer.
- Completed `reports/proposal.md`: problem description, target users, expected functionality, function specifications, architecture, three example requests, an evaluation plan with seven planned tests, and weekly milestones for Weeks 10-17.
- Defined the structured JSON output schema (verdict, risk score, red flags, explanation, recommended action).

## Important Commits

- Commit hash: REPLACE_WITH_REAL_HASH
- Description: Add project proposal and week 10 report
- Link: REPLACE_WITH_COMMIT_LINK

## Current Functionality

No running application yet. This week was planning only: the proposal, the architecture and the output schema are defined.

## Problems Encountered

- Choosing a topic that is simple enough for D level but still meaningful and relevant to my cyber security focus.
- Deciding how strict the output schema should be so that it can be validated reliably.

## Solutions

- Chose phishing email analysis, where the input and output are well defined and easy to test.
- Defined a fixed JSON schema with allowed values for the verdict and red flag types, and a score range of 0-100, so that validation can be done mechanically.
- Planned tests with a mock LLM client so they are reproducible without an API key.

## What I Learned

- A D-level application is a pipeline: input validation, prompt construction, LLM call, output validation and a formatted result.
- Asking an LLM for structured output is not enough on its own. The output must be validated because the model can return malformed or out-of-range data.
- The development consistency coefficient rewards steady weekly progress, so work should be spread across the weeks.

## Next Week

- Set up the project structure and environment configuration without committing secrets.
- Implement the LLM client and the first working request.
- Write the first version of the prompt and a basic README.
