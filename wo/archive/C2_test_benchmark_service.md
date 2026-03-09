# Phase C2: Write Tests for Benchmark Service Changes

## Task

Create tests for the updated benchmark_service that uses the queue system.

## Requirements

**File:** `tests/test_benchmark_service_queue.py`

Test the new queue-based workflow:
1. WIP file creation
2. Queue prompt generation
3. Queue file placement in agents/*/queue/in/
4. Polling for COMPLETE tag
5. Result archival

## Implementation

```python
import pytest
from pathlib import Path
from csc_shared.services.benchmark_service import benchmark

def test_benchmark_creates_wip_file(tmp_path):
    """Test that benchmark creates WIP file in prompts/wip/."""
    # Run benchmark.run()
    # Verify WIP file exists in prompts/wip/
    pass

def test_benchmark_creates_queue_prompt(tmp_path):
    """Test that benchmark creates queue prompt."""
    # Run benchmark.run()
    # Verify queue prompt in agents/{agent}/queue/in/
    pass

def test_queue_prompt_contains_wip_path(tmp_path):
    """Test queue prompt references WIP file path."""
    # Create benchmark
    # Check queue prompt content includes WIP path
    pass

def test_benchmark_polls_for_complete(tmp_path):
    """Test benchmark polls WIP file for COMPLETE tag."""
    # Run benchmark
    # Add COMPLETE to WIP file
    # Verify benchmark detects it
    pass

def test_benchmark_archives_on_complete(tmp_path):
    """Test result archival when COMPLETE found."""
    # Complete benchmark
    # Verify .tgz created in tools/benchmarks/results/
    pass
```

## Acceptance

- All tests pass
- Queue workflow fully tested
- Edge cases covered
- No regression in existing functionality

## Work Log
