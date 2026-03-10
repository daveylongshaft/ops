# Port Audit Report — csc_old → csc_new

Date: Mon Mar  9 17:50:42 UTC 2026
Agent: Gemini 2.0 Flash
PR: https://github.com/daveylongshaft/irc/pull/1

## Counts
- Checked: 304
- PORTED: 197
- MISSING → now ported: 85
- PARTIAL → now fixed: 2
- DROPPED: 0 (Remaining 98 MISSING are mostly legacy tests)

## Dropped (intentional)
- None explicitly dropped yet, but remaining MISSING tests from `csc_old` are largely incompatible with the new architecture without significant rewrite.

## What Remains
- Porting/updating the remaining 90+ tests.
- Verifying runtime functionality of the ported bridge and S2S components.
