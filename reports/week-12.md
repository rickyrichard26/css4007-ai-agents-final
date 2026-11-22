# Semester Week 12 Progress Report

## Completed Work

- Implemented input validation in `src/validation.py`. It rejects non-dict input, non-text fields, an empty body, a body over 10,000 characters and an over-long sender or subject, all before any LLM call is made. It returns a trimmed copy and does not modify the original input.
- Implemented output parsing and schema validation in `src/output_validation.py`. It accepts JSON even when wrapped in a markdown fence, and checks that the verdict is one of the allowed values, the risk score is an integer from 0 to 100 (booleans and non-integer numbers are rejected), every red flag has a valid type and non-empty evidence, and the explanation and recommended action are non-empty. Extra keys from the model are dropped.
- Wrote unit tests with pytest that run without an API key: 19 tests for input validation and 46 test cases for output validation (many are parametrized).
- Committed four sample emails (phishing, legitimate, suspicious, prompt injection). I created them and tested them manually with the real model in Week 11, and added them to the repository this week.

## Important Commits

- Commit hash: fb38140
- Description: Add input validation with unit tests (16 Nov 2026)
- Link: https://github.com/rickyrichard26/css4007-ai-agents-final/commit/fb38140

- Commit hash: 8aeb56a
- Description: Add output parsing and schema validation with unit tests (22 Nov 2026)
- Link: https://github.com/rickyrichard26/css4007-ai-agents-final/commit/8aeb56a

- Commit hash: 4e8f69c
- Description: Add sample emails for manual testing (22 Nov 2026)
- Link: https://github.com/rickyrichard26/css4007-ai-agents-final/commit/4e8f69c

## Current Functionality

The application can build a prompt for an email, send it to the model and return the raw reply (Week 11). Input validation and output validation now exist as separate, tested modules. They are not yet connected into one pipeline command; that is planned for Week 13.

## Problems Encountered

- My first test files were named with dots (`test.validation.py`), so pytest did not recognize them.
- One test file was saved empty (0 bytes) because I had not saved it, so it ran no tests.
- I first worked in a separate local folder that was not a Git repository, so I had to move the files into my fork before committing. Git commands also failed when I ran them in the wrong folder.
- Most of the week's code was committed late in the week. I should spread the work over more days.

## Solutions

- Renamed the files with underscores (`test_validation.py`), re-created the empty file's content, and confirmed the counts with pytest (19 and 46 passed).
- Copied the files into the fork, re-ran the tests there, and committed module by module so that each commit contains one module and its tests.
- For Week 13 I will work in smaller steps over several days and commit after each module.

## What I Learned

- Validating input before calling the LLM saves cost and avoids sending unusable data to the model.
- In Python `bool` is a subclass of `int`, so a boolean score would pass a plain integer check unless it is rejected explicitly.
- A model can return valid-looking JSON in the wrong shape, or wrapped in a markdown fence, so its output must be parsed and validated field by field.
- Parametrized tests let one test function cover many bad inputs, and tests with a mock need no API key, so they are reproducible.

## Next Week

- Connect the modules into one pipeline (input validation, prompt, LLM call with retries, output validation) with a readable report and a command-line interface.
- Add integration tests with a mock LLM for API failures and malformed output.
- Run the full pipeline with the real model and record the results.
