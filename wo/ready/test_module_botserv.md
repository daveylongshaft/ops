# Test Module: botserv
agent: gemini-2.5-pro
urgency: P2

## Objective
Test all methods of the `botserv` service module via the AI command interface in #general.
Use the FIFO client at /opt/csc/tmp/csc/run/client.in to send commands.
Report which methods work, which fail, and what output they return.

## Command syntax
`AI 1 botserv <method> [args]`

## Methods to test
add delete list addmatch delmatch addnomatch delnomatch listfilters logread

## Special notes


## Procedure
For each method:
1. Send: echo "AI 1 botserv help" >> /opt/csc/tmp/csc/run/client.in (get current help output)
2. Send: echo "AI 1 botserv <method>" >> /opt/csc/tmp/csc/run/client.in
3. Wait 5 seconds, check response in channel or server log:
   journalctl --user -u csc-server.service -n 20 --no-pager | grep -E "Help for botserv|<method>|Error"
4. Note: WORKS / FAILS / PARTIAL + any output or error message

## Report format (append to this file when done)
```
METHOD         | RESULT  | NOTES
---------------|---------|------
help           |         |
test           |         |
add            |         |
delete         |         |
list           |         |
addmatch       |         |
delmatch       |         |
addnomatch     |         |
delnomatch     |         |
listfilters    |         |
logread        |         |
```

## Done
When complete, write COMPLETE as the last line.
