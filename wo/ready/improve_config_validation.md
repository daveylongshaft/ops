# Add Schema Validation for JSON Config Files

**Priority**: P2 (reliability)
**Estimate**: 3 hours
**Assignee**: jules | codex | gemini
**Reviewer**: anthropic (opus)

## Problem

The system loads 10+ JSON config files from `etc/` with NO validation. Corrupt or malformed JSON files cause crashes or undefined behavior. No versioning exists to handle schema evolution.

## Objective

Add JSON schema validation for all config files with:
1. Schema definitions for each config file type
2. Validation on load with clear error messages
3. Graceful degradation on corrupt files
4. Schema versioning for future compatibility

## Context

**Current config files** (in `etc/`):
- `settings.json` - Server settings
- `platform.json` - Platform configuration
- `opers.json` - Operator credentials
- `users.json` - User database
- `channels.json` - Channel persistence
- `bans.json` - Ban list
- `nickserv.json` - NickServ data
- `chanserv.json` - ChanServ data
- `botserv.json` - BotServ data
- `history.json` - Message history

**Current loading** (no validation):
```python
with open('etc/settings.json') as f:
    config = json.load(f)  # No validation!
```

**Problems**:
- Typos in config keys go undetected
- Missing required fields cause KeyError at runtime
- Wrong value types cause cryptic errors
- No way to detect config version mismatches

## Proposed Solution

Use `jsonschema` library for validation:

```python
import json
import jsonschema
from jsonschema import validate, ValidationError

# Define schema
SETTINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "number", "minimum": 1.0},
        "server_name": {"type": "string"},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
        "max_clients": {"type": "integer", "minimum": 1},
        "motd": {"type": "string"}
    },
    "required": ["version", "server_name", "port"],
    "additionalProperties": True
}

# Validate on load
def load_config(path, schema):
    try:
        with open(path) as f:
            config = json.load(f)
        validate(instance=config, schema=schema)
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return None
    except ValidationError as e:
        logger.error(f"Schema validation failed for {path}: {e.message}")
        return None
    except FileNotFoundError:
        logger.warning(f"Config file not found: {path}, using defaults")
        return {}
```

## Schema Definitions Required

Create schemas for each config file:

1. **settings.json** - Server configuration
   - Required: version, server_name, port
   - Optional: max_clients, motd, timeout

2. **platform.json** - Platform paths
   - Required: version, csc_root
   - Optional: temp_path, log_path

3. **opers.json** - Operator list
   - Structure: Array of {username, password, hostmask}

4. **users.json** - User database
   - Structure: Dict of username -> {password_hash, email, registered}

5. **channels.json** - Channel state
   - Structure: Dict of channel_name -> {topic, modes, members}

6. **bans.json** - Ban list
   - Structure: Array of {mask, reason, expires, set_by}

7. Service configs (nickserv.json, chanserv.json, botserv.json)
   - Structure: {version, enabled, config_dict}

## Implementation Steps

1. Install jsonschema:
   ```bash
   pip install jsonschema
   ```

2. Create `irc/packages/csc-service/csc_service/shared/config_schemas.py`:
   - Define all schemas as constants
   - Export schema dict: `SCHEMAS = {"settings": SETTINGS_SCHEMA, ...}`

3. Create `irc/packages/csc-service/csc_service/shared/config_loader.py`:
   - `load_config(path, schema_name)` function
   - Validation with clear error messages
   - Fallback to defaults on failure

4. Update `data.py` to use config_loader:
   - Replace direct `json.load()` calls
   - Add error handling for validation failures
   - Log config validation results

5. Add version fields to all config files:
   ```json
   {
     "version": 1.0,
     ...
   }
   ```

6. Create migration guide for future schema changes

## Version Migration Strategy

```python
def migrate_config(config, current_version, target_version):
    """Migrate config from current_version to target_version."""
    if current_version < 1.1 and target_version >= 1.1:
        # Migration from 1.0 to 1.1
        config["new_field"] = "default_value"
    return config
```

## Acceptance Criteria

- [ ] jsonschema installed and imported
- [ ] Schemas defined for all 10 config files
- [ ] config_loader.py module created
- [ ] All config loading uses validation
- [ ] Clear error messages on validation failure
- [ ] Server starts with valid config
- [ ] Server logs error and uses defaults on invalid config
- [ ] All config files have "version" field
- [ ] Documentation for schema definitions

## Files to Create

- `irc/packages/csc-service/csc_service/shared/config_schemas.py` - Schema definitions
- `irc/packages/csc-service/csc_service/shared/config_loader.py` - Validation loader
- `docs/config-schemas.md` - Schema documentation

## Files to Modify

- `irc/packages/csc-service/csc_service/shared/data.py` - Use config_loader
- `irc/packages/csc-service/csc_service/server/server.py` - Use config_loader
- All `etc/*.json` files - Add version field

## Testing

1. **Valid config test**: Start server with valid configs, verify no errors

2. **Invalid JSON test**:
   ```bash
   echo "{ invalid json" > etc/test.json
   # Verify: Error logged, defaults used, server still starts
   ```

3. **Schema violation test**:
   ```json
   {"version": 1.0, "port": "not a number"}
   # Verify: Validation error logged with field name
   ```

4. **Missing required field test**:
   ```json
   {"version": 1.0}  # Missing "server_name"
   # Verify: Validation error specifies missing field
   ```

5. **Version migration test**:
   ```python
   # Load config with version 1.0
   # Migrate to version 1.1
   # Verify new fields added
   ```

## Notes

- Validation happens at startup AND on REHASH command
- Use strict validation in production, loose in development
- Schema evolution: always backward compatible
- Consider auto-generating schema documentation
- JSON Schema spec: https://json-schema.org/
- Future: Use Pydantic for Python-native validation

## Example Schema

```python
OPERS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "version": {"type": "number", "const": 1.0},
        "opers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "minLength": 1},
                    "password": {"type": "string", "minLength": 1},
                    "hostmask": {"type": "string", "pattern": "^.*!.*@.*$"}
                },
                "required": ["username", "password", "hostmask"]
            }
        }
    },
    "required": ["version", "opers"]
}
```

## Error Message Examples

Good error messages help operators fix config issues:

```
[ERROR] Config validation failed: etc/settings.json
  - Missing required field: 'server_name'
  - Field 'port': Expected integer, got string
  - Using default configuration
```
