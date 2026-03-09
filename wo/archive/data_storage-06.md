---
urgency: P3
description: Fix BridgeConfigData and BenchmarkService file I/O
cost_sensitive: true
---

# Fix: BridgeConfigData and BenchmarkService → Data Class

## Violation Locations

### BridgeMain (1 violation)
- File: `packages/csc-service/csc_service/bridge/main.py:193`
- Pattern: `with open(config_file, 'r') as f:`

### BenchmarkService (2 violations)
- File: `packages/csc-service/csc_service/shared/services/benchmark_service.py:49,63`
- Pattern:
  ```python
  with open(self.METADATA_FILE, 'r', encoding='utf-8') as f:
  with open(self.METADATA_FILE, 'w', encoding='utf-8') as f:
  ```

## Current Issues

### Bridge Config
Bridge reads config file directly without using Data class:
```python
with open(config_file, 'r') as f:
    config = json.load(f)
```

### BenchmarkService
Stores metadata in project root `benchmarks/benchmarks.json`:
```python
with open(self.METADATA_FILE, 'r', encoding='utf-8') as f:
    self.benchmarks = json.load(f)

with open(self.METADATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(self.benchmarks, f, indent=2)
```

## Should Be

### Bridge
```python
class BridgeConfigData(Data):
    def __init__(self):
        super().__init__()
        self.source_filename = "bridge_config.json"
        self.connect()

# In Bridge:
config_data = BridgeConfigData()
config = config_data.get_data("bridge_config")
```

### BenchmarkService
```python
class BenchmarkData(Data):
    def __init__(self):
        super().__init__()
        self.source_filename = "benchmarks.json"
        self.connect()

# In BenchmarkService:
class BenchmarkService(Service):
    def __init__(self, server_instance):
        super().__init__(server_instance)
        self.benchmark_data = BenchmarkData()
        # ...
    
    def save_benchmarks(self):
        self.benchmark_data.put_data("benchmarks", self.benchmarks)
    
    def load_benchmarks(self):
        self.benchmarks = self.benchmark_data.get_data("benchmarks") or {}
```

## Implementation Steps

### Bridge (Simple)
1. Create BridgeConfigData class inheriting from Data
2. Replace line 193 open() with BridgeConfigData().get_data()
3. Test bridge initialization

### BenchmarkService (Medium)
1. Create BenchmarkData class inheriting from Data
2. Move line 49 (read) to use BenchmarkData.get_data()
3. Move line 63 (write) to use BenchmarkData.put_data()
4. Remove BENCHMARKS_DIR file writes
5. Test benchmark runs work correctly

## Why This Matters
- Bridge config stored in temp/csc/run/ (not scattered)
- Benchmark metadata isolated from project root
- Consistent use of Data class across services
- Framework-aware file handling

## Acceptance Criteria
✓ Bridge reads config via BridgeConfigData
✓ BenchmarkService reads/writes via BenchmarkData
✓ All config files stored in temp/csc/run/
✓ Bridge initialization works
✓ Benchmark operations work correctly
