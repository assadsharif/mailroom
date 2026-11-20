# What a reviewer checks in Mailroom

These are the rules no test can fully catch. Check each one in every pull request.

- Sending code changes only happen against localhost, and never to a non-practice address (see `policy.py`).
- No real person's email address appears anywhere in code, data, or tests.
- Today's date is read only in `commands.py`. Logic receives the run date as an argument.
- Only `commands.py` prints.
- Every function has type hints, and a new behavior has a test with an expected answer the author did not change to make it pass.
- An expected answer was changed only with a stated reason in the pull request.
- Retries never apply to a 4xx response, and every send carries an idempotency key.
- A new rule for issues is written in `docs/email-rules.md` before it is written in code.
- The pull request's Evidence section contains real output, not a claim.
- A bad merge is undone with a revert, followed by a test that would have caught it.
