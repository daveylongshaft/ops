# Test Module: builtin
agent: gemini-2.5-pro
urgency: P2

## Objective
Test all methods of the `builtin` service module via the AI command interface in #general.
Use the FIFO client at /opt/csc/tmp/csc/run/client.in to send commands.
Report which methods work, which fail, and what output they return.

## Command syntax
`AI 1 builtin <method> [args]`

## Methods to test
echo status current_time download_url_content download_url_to_file list_dir read_file_content create_directory_local delete_local move_local ftp_connect_list ftp_download_file ftp_upload_file

## Special notes


## Procedure
For each method:
1. Send: echo "AI 1 builtin help" >> /opt/csc/tmp/csc/run/client.in (get current help output)
2. Send: echo "AI 1 builtin <method>" >> /opt/csc/tmp/csc/run/client.in
3. Wait 5 seconds, check response in channel or server log:
   journalctl --user -u csc-server.service -n 20 --no-pager | grep -E "Help for builtin|<method>|Error"
4. Note: WORKS / FAILS / PARTIAL + any output or error message

## Report format (append to this file when done)
```
METHOD         | RESULT  | NOTES
---------------|---------|------
help           |         |
test           |         |
echo           |         |
status         |         |
current_time   |         |
download_url_content |         |
download_url_to_file |         |
list_dir       |         |
read_file_content |         |
create_directory_local |         |
delete_local   |         |
move_local     |         |
ftp_connect_list |         |
ftp_download_file |         |
ftp_upload_file |         |
```

## Done
When complete, write COMPLETE as the last line.
