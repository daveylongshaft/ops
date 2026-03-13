# Test Module: agent
agent: gemini-2.5-pro
urgency: P2

## Objective
Test all methods of the `agent` service module via the AI command interface in #general.
Use the FIFO client at /opt/csc/tmp/csc/run/client.in to send commands.
Report which methods work, which fail, and what output they return.

## Command syntax
`AI 1 agent <method> [args]`

## Methods to test
list select assign status stop kill tail

## Special notes


## Procedure
For each method:
1. Send: echo "AI 1 agent help" >> /opt/csc/tmp/csc/run/client.in (get current help output)
2. Send: echo "AI 1 agent <method>" >> /opt/csc/tmp/csc/run/client.in
3. Wait 5 seconds, check response in channel or server log:
   journalctl --user -u csc-server.service -n 20 --no-pager | grep -E "Help for agent|<method>|Error"
4. Note: WORKS / FAILS / PARTIAL + any output or error message

## Report format (append to this file when done)
```
METHOD         | RESULT  | NOTES
---------------|---------|------
help           |         |
test           |         |
list           |         |
select         |         |
assign         |         |
status         |         |
stop           |         |
kill           |         |
tail           |         |
```

## Done
When complete, write COMPLETE as the last line.
