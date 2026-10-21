# Project Guidelines

## Code Review Standards
- Prioritize correctness, security, and data integrity.
- Identify concrete defects rather than stylistic preferences.
- Include file paths and supporting evidence for findings.
- Do not report speculative issues without a clear explanation.
- Avoid reporting the same issue more than once.

## Testing Standards
- Inspect existing tests before suggesting new test cases.
- Prefer tests that validate observable behavior.
- Include relevant edge cases and error-handling scenarios.
- Avoid duplicating scenarios already covered by existing tests.

## Fixture Conventions
- Reuse existing fixtures and test helpers where appropriate.
- Follow the repository's established test data conventions.
- Avoid introducing unnecessary duplicate test data.

## Review Output
- Classify findings by severity.
- Explain the potential impact of each finding.
- Recommend a specific corrective action.
- Report no findings when no actionable issues are identified.
