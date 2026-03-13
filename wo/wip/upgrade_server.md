---
urgency: P0
---
upgrade the server in the following way
# Plan: Server Rewrite - Data() as Universal I/O Interface

## Architectural Vision

Data() is the single point of ALL information storage and retrieval.
Nothing in the codebase should know where files are, what files exist,
or how data is stored. They call Data() methods and Data handles it.
Swap disk for tape, remote FS, or any other backend by changing only
Data._read_json_file and _write_json_file. Everything else is untouched.

## The Pattern

ServerData is a pure mixin - no parent class, just methods that use
self.* (which Data provides). Data absorbs ServerData via multiple
inheritance, becoming the complete I/O interface for the whole system.

    class ServerData:                          # pure mixin, no parent
        def load_channels(self):
            return self._read_json_file(self._file_path("channels"))
        # ... ALL IRC-specific domain methods including ALL oper methods

    class Data(Log, ServerData):               # Data absorbs all ServerData methods
        # _read_json_file and _write_json_file are the ONLY I/O primitives

## Full Inheritance Chain After Rewrite

    Root -> Log -> Data(ServerData) -> Version -> Platform -> Network -> Service -> Server

## What ServerData (mixin) Contains

ALL IRC-specific domain knowledge. Pure mixin, no parent class.
Uses only self._read_json_file, self._write_json_file, self._get_etc_dir(), self.log().

Class attributes:
    FILES = {
        "channels": "channels.json",  "users": "users.json",
        "opers": "opers.json",        "bans": "bans.json",
        "history": "history.json",    "nickserv": "nickserv.json",
        "chanserv": "chanserv.json",  "botserv": "botserv.json",
        "settings": "settings.json",
    }
    DEFAULTS = { ... default JSON for each file ... }

Methods:
    _file_path(key), _has_changed(key), _ensure_all_files(), _quarantine(filepath)
    Channels:  load_channels, save_channels, save_channels_from_manager
    Users:     load_users, save_users, set_user, remove_user, save_users_from_server
    Bans:      load_bans, save_bans, save_bans_from_manager
    History:   load_history, save_history, add_disconnection, save_history_from_server
    NickServ:  load_nickserv, save_nickserv, nickserv_register, nickserv_drop,
               nickserv_get, nickserv_check_password
    ChanServ:  load_chanserv, save_chanserv, chanserv_register, chanserv_get,
               chanserv_update, chanserv_drop
    BotServ:   load_botserv, save_botserv, botserv_register, botserv_get,
               botserv_get_for_channel, botserv_drop
    Settings:  load_settings, save_settings
    Bulk:      persist_all(server), restore_all(server)
    Restore:   restore_channels, restore_users, restore_opers, restore_bans, restore_history

    Opers (MOVED FROM data.py):
        _opers_path(), _olines_conf_path()
        _migrate_opers_v1_to_v2(data), _match_hostmask(mask, client_mask)
        _load_opers(), _save_opers(data), load_opers(), save_opers()
        get_olines(), get_active_opers(), get_active_opers_info(), get_oper_flags(nick)
        protect_local_opers (property)
        add_active_oper(nick, account, flags), remove_active_oper(nick)
        check_oper_auth(account, password, server_name, client_mask)
        write_olines_conf(olines, path)     # export only, never read back automatically
        save_opers_from_server(server)

    NOTE: No reload_olines(), no parse_olines_conf(), no REHASH support.
    olines.conf is written as export only (write_olines_conf). It is NEVER read.
    opers.json is the only authority. Edit it directly.

## What Data Has After Rewrite (general I/O only)

    _read_json_file(path), _write_json_file(path, data)  # encryption hook points
    _get_etc_dir(), _get_run_dir()
    get_data / put_data / store_data / connect / init_data
    NO oper methods, NO IRC-specific methods.

## opers.json: 2 Oper Accounts

Two accounts, both with *!*@* hostmasks:
    {
      "version": 2,
      "protect_local_opers": true,
      "active_opers": [],
      "olines": {
        "admin": [{"user":"admin","password":"changeme","servers":["*"],
                   "host_masks":["*!*@*"],"flags":"aol","comment":"default admin"}],
        "davey": [{"user":"davey","password":"dfg9538","servers":["*"],
                   "host_masks":["*!*@*"],"flags":"aOl","comment":"primary admin"}]
      }
    }

## nickserv.json: 4 Accounts (No Changes Needed)

Verified: davey, davey-hp, rucky, rucky-hp all present with password dfg9538.

## olines.conf: Remove

olines.conf served only as an alternate config source. Since opers.json is the
sole authority and reload_olines/parse_olines_conf are removed, olines.conf has
no purpose. Delete it.

## Implementation Steps

Step 1: Create shared/server_data.py (one class, one file)
    - Pure mixin class ServerData, no parent
    - Move ALL methods from storage.py PersistentStorageManager
    - Move ALL oper methods from data.py
    - restore_opers(): remove the conf_olines merge block entirely (storage.py lines 749-756)
    - No reload_olines(), no parse_olines_conf()

Step 2: Update shared/data.py
    - from .server_data import ServerData
    - class Data(Log, ServerData):
    - Remove ALL oper methods (moved to ServerData)
    - Remove debug logging from check_oper_auth (added in previous session)
    - Data.__init__: super().__init__() + self._mtimes = {} + self._ensure_all_files()

Step 3: Fix etc/opers.json
    - Keep admin (changeme, *!*@*) and davey (dfg9538, *!*@*)
    - Remove davey-hp, rucky, rucky-hp olines

Step 4: Delete etc/olines.conf
    - No longer needed. opers.json is sole authority.

Step 5: Delete server/storage.py
    - PersistentStorageManager is removed entirely. All its logic now lives in ServerData.
    - Find all imports of PersistentStorageManager and remove them.

Step 6: Update server/server.py
    - Remove self.storage = PersistentStorageManager(...)
    - Remove from .storage import PersistentStorageManager
    - Replace ~14 self.storage.X call sites with self.X

Step 7: Update server/server_message_handler.py
    - Replace ~71 self.server.storage.X with self.server.X
    - Fix any base_path references to use self.server._get_etc_dir()
    - Remove debug logging from _handle_oper (added in previous session)

## Files Changed
- shared/server_data.py        NEW - pure mixin, ALL IRC domain persistence
- shared/data.py               UPDATE - absorb ServerData, remove oper methods
- etc/opers.json               UPDATE - admin + davey, both *!*@*
- etc/olines.conf              DELETE
- server/storage.py            DELETE
- server/server.py             UPDATE - remove self.storage, ~14 call sites
- server/server_message_handler.py  UPDATE - ~71 self.server.storage.X -> self.server.X

## The Payoff
- Server.log() captures ALL output including storage ops
- No self.storage anywhere — just self
- opers.json is stable — nothing overwrites it on restart
- Single place for all IRC persistence (ServerData)
- Data is generic I/O, usable by any subsystem
- Storage backend swap: change only _read_json_file / _write_json_file

