# Test Module: workorders
agent: gemini-2.5-pro
urgency: P2

## Objective
Test all methods of the `workorders` service module via the AI command interface in #general.
Use the FIFO client at /opt/csc/tmp/csc/run/client.in to send commands.
Report which methods work, which fail, and what output they return.

## Command syntax
`AI 1 workorders <method> [args]`

## Methods to test
urgency add list read edit append assign move delete status archive

## Special notes


## Procedure
For each method:
1. Send: echo "AI 1 workorders help" >> /opt/csc/tmp/csc/run/client.in (get current help output)
2. Send: echo "AI 1 workorders <method>" >> /opt/csc/tmp/csc/run/client.in
3. Wait 5 seconds, check response in channel or server log:
   journalctl --user -u csc-server.service -n 20 --no-pager | grep -E "Help for workorders|<method>|Error"
4. Note: WORKS / FAILS / PARTIAL + any output or error message

## Report format (append to this file when done)
```
METHOD         | RESULT  | NOTES
---------------|---------|------
help           |         |
test           |         |
urgency        |         |
add            |         |
list           |         |
read           |         |
edit           |         |
append         |         |
assign         |         |
move           |         |
delete         |         |
status         |         |
archive        |         |
```

## Done
When complete, write COMPLETE as the last line.
