# Haiku: Gemini CLI Weekly Upgrade Check (Recurring)

<!-- delay 1772400000 -->

## Purpose
Check for gemini-cli updates weekly and apply them. This is a recurring/perpetual task that reschedules itself after each run.

## Implementation

### 1. Check for Gemini CLI Updates
```bash
npm outdated -g @google/gemini-cli
# If there's an update available, upgrade it
npm update -g @google/gemini-cli
```

### 2. Verify Installation
After upgrade:
```bash
which gemini-cli
gemini-cli --version
```

### 3. Reschedule Next Check
This workorder creates a copy of itself with a new delay timestamp (7 days from now):
```bash
CURRENT_DELAY=$(grep -oP 'delay \K\d+' workorders/ready/haiku-gemini-cli-weekly-upgrade-check.md | head -1)
NEXT_DELAY=$(($(date +%s) + 604800))
# Copy this workorder and update its delay
cp workorders/ready/haiku-gemini-cli-weekly-upgrade-check.md \
   workorders/ready/haiku-gemini-cli-weekly-upgrade-check-reschedule.md
sed -i "s/delay [0-9]*/delay $NEXT_DELAY/" workorders/ready/haiku-gemini-cli-weekly-upgrade-check-reschedule.md
```

## Acceptance Criteria

- [ ] Checks for gemini-cli updates
- [ ] Applies updates if available
- [ ] Verifies gemini-cli is still working after upgrade
- [ ] Creates new workorder with 7-day delay
- [ ] Original workorder moved to done/
- [ ] No errors in update process
- [ ] Recurring pattern works (verify second run reschedules again)

## Notes

- This workorder requires the PM scheduled delay feature to be implemented first
- Runs weekly to keep gemini-cli current without blocking queue-worker with auto-upgrades
- If upgrade fails, leaves original workorder in ready/ for human investigation
- Each successful run creates a new instance for next week

---

## Agent Log

START
