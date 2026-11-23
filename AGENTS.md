# Mailroom rules

Mailroom is a command-line tool for one newsletter: Kettlebird Tea's Steep Club. It reads the subscribers, checks an issue, and sends it to a practice mail server.

## How I learn

- I am new to Python. I have completed up to 13.12 of https://agentfactory.panaversity.org/building-ai-workers/programming-fundamentals/ and I update this number as I learn.
- Write only with what I have learned. If something new would really help, stop and tell me its name in one line. I decide.
- When the code uses something new, show me that piece first and ask me to predict what it does. Stay quiet while I guess. Then run it, and explain a line only when I ask.

## Process
- Use uv for everything.
- Commit and push after every step.
- Every change goes on a branch and arrives as a pull request.
- A pull request shows its evidence.
- The checks must pass before a merge.
- Undo a bad merge with a revert pull request, then add the test that would have caught it.
- Behaviors first: expected answers are written as tests, shown failing, then the code is written.
- Tests first; one test per behavior, named for the behavior. pytest runs them.
- I decide the test cases and their answers. Never change an expected answer to make a test pass.
- When something breaks, show me the full error before changing anything.

## Code
- Every function has type hints, and pyright must be clean.
- One module per job. Only the commands module prints.
- Pass Subscriber and Issue objects around, never raw rows or raw text.
- Never read today's date inside the logic. Pass the run date in. Only the command line reads today's date.
- Subject and preview length count what Python's len() counts.
- Report every problem with its row. No traceback for a user's mistake.
- Links must use https.
- The greeting must be in the first line of the body.

## Data
- Data from outside goes through the model before any code uses it. The model checks the shape. Our own rules check the meaning.
- JSON read from a file is outside data: it goes through a model too.
- Retry only what can succeed later, and every send has an idempotency key.
- Handle each status on purpose. Never retry a 4xx.
- Send with a limit on how many at once.

## Sending
- Never use a real person's email address. Use @example.com, and @resend.dev for practice sends.
- The key and the address come from the environment. Sending works only against localhost.
- Fixed rules are checked by Mailroom. Claude handles the judgment.
