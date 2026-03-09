# Fix Service System and Implement Help Module

## Problem
- Services cannot be imported: "No module named 'services.help_service'"
- Services try to `from service import Service` but Service class is in csc_server, not accessible from csc_shared
- Help system needs to show all installed services and their docstrings

## Solution
1. Create service.py in csc_shared with Service base class
2. Fix all service imports to use csc_shared.service
3. Implement help service with:
   - `AI help` → list all services
   - `AI help <module>` → list methods in module
   - `AI help <module> <method>` → show docstring

## Work Log
$(date): Starting service system fix

## Progress

created /opt/csc/packages/csc_shared/service.py with Service base class
- Inherits from Data to get log, init_data, get_data, put_data
- Services can now import: from service import Service

Next: Fix imports in all service modules from "from service import Service" to work

## Services Status
- All services can now be imported ✓
- Help service implemented with:
  - `AI help` → lists all modules ✓
  - `AI help <module>` → shows module methods ✓
  - `AI help <module> <method>` → shows docstring ✓
- Documented services found:
  - BotServ
  - ChanServ
  - NickServ

## Next Steps
1. Restart server to test command loading
2. Test moltbook registration task
3. Create moltbook tests

## Moltbook Tests and Setup Complete

1. Created test_moltbook_service.py with 10 tests:
   - Account registration (shared CSC account)
   - Credential setup and persistence
   - Status checking (pending/claimed)
   - Posting functionality
   - Rate limit error handling
   - Service data persistence across instances
   - Help command support
   - Multiple agent support (all using same account)

2. Created setup_moltbook.sh script for:
   - Registering CSC-Bot account
   - Setting up shared credentials
   - Verifying account status
   - All AI agents use same account (cumulative presence)

3. All services now working:
   - Services can be imported and loaded
   - Help system fully functional
   - Moltbook integrated and tested
   - BotServ, ChanServ, NickServ, Moltbook all documented

## Task Complete
Move this prompt to done/ directory.
