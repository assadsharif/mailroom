# Predictions

Write each prediction before the run. Never change it afterwards.

## Step 0 · The base
Name and audience: Kettlebird Tea's Steep Club, for tea lovers.
Prediction:

## Step 1 · Count your subscribers
Total and per group:

- Total: 24
- tea-curious: 8
- gift-buyers: 8
- daily-drinkers: 8

Gave consent: 24

## Step 2 · Dates
Does 2026-10-21 count in the last 30 days? Yes. With the run date 2026-11-20 the window starts on 2026-10-21, so that day counts and 2026-10-20 does not. 7 subscribers fall inside it.
First Monday of December 2026 and the send after it: 2026-12-07, and the send after that is 2027-01-04.

## Step 3 · Reading an error
Will it crash? Last line of the error:

## Step 4 · Real tests
How many tests after the move, one per behavior: 14.

One for each behavior: 24 in total; 8 in each of the three groups; 7 joined in the last 30 days; 2026-10-21 counts and 2026-10-20 does not; the next send for 2026-11-20, 2026-12-07 and 2026-12-31; --since 2026-10-01 gives 12; the subscribers command; the next-send command; a bad row reported with its row number.

## Step 5 · Tests first
Expected answers for the six subject cases:

## Step 7 · The rest of the rules
Two cases per rule:

## Step 8 · Modules
Which tests break when the code moves, and why:

## Step 9 · Types
Crash or wrong answer? Which is worse:

## Step 10 · Classes
What print(subscriber) shows:

## Step 11 · Schemas
Which of the 8 sign-up rows will the model accept:

## Step 12 · What a schema lets through
Which two rules can live inside the model:

## Step 13 · Errors as design
Stop everything, or report and carry on: no file, wrong columns, bad date, Gmail address, two links:

## Step 14 · JSON
How the run date looks in the file:

## Step 15 · One email
Status code and body for a good email:

## Step 16 · Failures
Status for: no subject, unknown id, server switched off:

## Step 17 · Async
Time for 24 emails one by one, and five at a time:

## Step 18 · SDK
Does the SDK retry, and how long does it wait:

## Step 19 · Pull requests
Files the report command will touch:

## Step 20 · Evidence
Tests, types, or a person catches the new rule:

## Step 21 · Checks that block
Will GitHub allow the merge of a 56-character subject:

## Step 22 · Review
Which rules can no test catch:

## Step 23 · Approvals
Which files could do real harm:

## Step 24 · After the merge
Why the http:// link gets through, and whose call the older test is:

## Step 25 · Guard
What the guard reads from the hook JSON:

## Step 26 · Studio
Who notices a 56-character subject first:
