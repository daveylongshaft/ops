# Test Module: cryptserv
agent: gemini-2.5-pro
urgency: P2

## Objective
Test all methods of the `cryptserv` service module via the AI command interface in #general.
Use the FIFO client at /opt/csc/tmp/csc/run/client.in to send commands.
Report which methods work, which fail, and what output they return.

## Command syntax
`AI 1 cryptserv <method> [args]`

## Methods to test
request

## Special notes
Class is named CryptServ (CamelCase). Should now work after service.py fix.

## Procedure
For each method:
1. Send: echo "AI 1 cryptserv help" >> /opt/csc/tmp/csc/run/client.in (get current help output)
2. Send: echo "AI 1 cryptserv <method>" >> /opt/csc/tmp/csc/run/client.in
3. Wait 5 seconds, check response in channel or server log:
   journalctl --user -u csc-server.service -n 20 --no-pager | grep -E "Help for cryptserv|<method>|Error"
4. Note: WORKS / FAILS / PARTIAL + any output or error message

## Report format (append to this file when done)
```
METHOD         | RESULT  | NOTES
---------------|---------|------
help           |         |
test           |         |
request        |         |
```

## Done
When complete, write COMPLETE as the last line.
