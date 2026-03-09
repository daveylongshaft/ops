The Botserv service needs to be extended to allow an IRC bot to read the contents of a specified logfile and send these contents, line by line, to a designated IRC channel. The command should be accessible via /msg BotServ LOGREAD <channel> <logfile_path>. The bot should handle reading the file efficiently, and if the file is very large, it should send it in manageable chunks or provide an option to read only a certain number of lines. Focus on the core reading and sending functionality first. Assume the bot has the necessary permissions to read the file and send messages to the channel. The bot should indicate when it starts and finishes reading the log, and if it encounters any errors.

Reading prompt 1771405618-botserv_read_logfile_to_channel.md for implementation
Examining botserv_service.py for LOGREAD implementation
Implemented basic LOGREAD in botserv_service.py, including help message update.
Imported Path in botserv_service.py to resolve NameError.
Unit tests for LOGREAD created in tests/test_botserv_logread.py, awaiting cron script execution.
