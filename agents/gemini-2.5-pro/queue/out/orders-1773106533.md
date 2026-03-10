You are an AI coding agent. Your working directory is the CSC project root.

## YOUR TASK

Read and complete the workorder in: ops/wo/wip/PROMPT_review_pr_daveylongshaft_irc_1_20260309-201234.md

## MANDATORY: JOURNAL TO WIP FILE

Use `python bin/next_step` to journal your progress. This is NOT optional.

FIRST THING you do:
```bash
python bin/next_step ops/wo/wip/PROMPT_review_pr_daveylongshaft_irc_1_20260309-201234.md START
```

AS YOU WORK, journal before each action:
```bash
python bin/next_step ops/wo/wip/PROMPT_review_pr_daveylongshaft_irc_1_20260309-201234.md "reading config.py to understand ConfigManager"
# then do the reading

python bin/next_step ops/wo/wip/PROMPT_review_pr_daveylongshaft_irc_1_20260309-201234.md "implementing enable/disable commands"
# then do the coding

python bin/next_step ops/wo/wip/PROMPT_review_pr_daveylongshaft_irc_1_20260309-201234.md "writing tests in tests/test_foo.py"
# then write tests
```

WHEN DONE:
```bash
python bin/next_step ops/wo/wip/PROMPT_review_pr_daveylongshaft_irc_1_20260309-201234.md COMPLETE
```

WITHOUT JOURNALING:
- Queue-worker cannot detect completion
- Work is marked INCOMPLETE and retried
- You get no credit

## ORIENTATION

1. Read ops/wo/wip/PROMPT_review_pr_daveylongshaft_irc_1_20260309-201234.md for your task instructions
2. Read README.1shot for system procedures
3. Read tools/INDEX.txt for code map
4. Do the work, journaling each step with `python bin/next_step`
5. Write tests (don't run them)
6. Update relevant docs
7. `python bin/next_step ops/wo/wip/PROMPT_review_pr_daveylongshaft_irc_1_20260309-201234.md COMPLETE`

## RULES

- Journal EVERY step with `python bin/next_step`
- Write tests that verify your changes
- Update docs for features you changed
- Do NOT run tests (test-runner handles that)
- Do NOT touch git (queue-worker handles that)
- Do NOT move files between workorders directories

---

