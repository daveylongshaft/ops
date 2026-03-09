# PM: Implement Scheduled Workorder Execution with Delay Tags

## Overview
Add support for delayed workorder execution. Workorders can specify a minimum execution time using a `delay` tag on the first line. The PM will skip workorders until their delay time has passed.

## Implementation

### 1. Workorder Format
Workorders with delays start with a delay tag:
```
<!-- delay 1772400000 -->
# My Workorder Title
...content...
```

Or:
```
DELAY=1772400000
# My Workorder Title
...content...
```

### 2. PM Changes (infra/pm.py)

**New function: `extract_delay_tag(workorder_path: Path) -> int | None`**
```python
def extract_delay_tag(workorder_path: Path) -> int | None:
    """Extract delay tag from first line of workorder.

    Returns unix timestamp (int) when workorder should run, or None if no delay.
    Supports formats:
    - <!-- delay 1772400000 -->
    - DELAY=1772400000
    """
    try:
        with open(workorder_path, 'r') as f:
            first_line = f.readline().strip()

        # Try HTML comment format
        if first_line.startswith('<!--') and 'delay' in first_line:
            match = re.search(r'delay\s+(\d+)', first_line)
            if match:
                return int(match.group(1))

        # Try DELAY= format
        if first_line.startswith('DELAY='):
            match = re.search(r'DELAY=(\d+)', first_line)
            if match:
                return int(match.group(1))
    except:
        pass
    return None
```

**Update in `agent_assignment_for_workorder()` or filter before assignment:**
```python
def should_process_workorder(workorder_path: Path) -> bool:
    """Check if workorder is ready to process (not delayed)."""
    import time
    delay_until = extract_delay_tag(workorder_path)
    if delay_until is None:
        return True  # No delay, process immediately

    current_time = int(time.time())
    if current_time >= delay_until:
        return True  # Delay expired, ready to process

    # Still delayed - skip this workorder
    hours_remaining = (delay_until - current_time) / 3600
    log(f"Workorder {workorder_path.name} still delayed ({hours_remaining:.1f} hours remaining)", "DEBUG")
    return False
```

**Update workorder selection logic** in PM to:
1. Scan all workorders in ready/
2. Filter out delayed workorders
3. Only select from immediately available workorders

### 3. Test Cases

- [ ] Workorder with future delay is skipped
- [ ] Workorder with past delay is processed
- [ ] Workorder with no delay is processed immediately
- [ ] Both HTML comment and DELAY= formats work
- [ ] PM logs skip reason for delayed workorders

### 4. Usage Examples

Create a workorder that runs in 7 days:
```bash
DELAY=$(($(date +%s) + 604800))
echo "<!-- delay $DELAY -->" > workorders/ready/my_delayed_task.md
echo "# My Task" >> workorders/ready/my_delayed_task.md
```

Create a perpetual weekly upgrade check:
```bash
DELAY=$(($(date +%s) + 604800))
echo "<!-- delay $DELAY -->" > workorders/ready/gemini-cli-upgrade-check.md
echo "# Gemini CLI Weekly Upgrade Check" >> workorders/ready/gemini-cli-upgrade-check.md
# ... rest of content ...
```

## Acceptance Criteria

- [ ] Delayed workorders are skipped by PM
- [ ] Past delays are processed immediately
- [ ] Both delay tag formats supported
- [ ] No performance impact on queue scanning
- [ ] Logging shows skip reason for delayed items
- [ ] Can create perpetual workorders that reschedule themselves

---

## Agent Log

START
