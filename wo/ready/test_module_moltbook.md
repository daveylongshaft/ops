# Test Module: moltbook
agent: gemini-2.5-pro
urgency: P2

## Objective
Test all methods of the `moltbook` service module via the AI command interface in #general.
Use the FIFO client at /opt/csc/tmp/csc/run/client.in to send commands.
Report which methods work, which fail, and what output they return.

## Command syntax
`AI 1 moltbook <method> [args]`

## Methods to test
setup register status post post_link comment reply upvote downvote delete_post feed submolt_feed get_post get_comments search create_submolt subscribe unsubscribe list_submolts follow unfollow profile update_profile notifications

## Special notes


## Procedure
For each method:
1. Send: echo "AI 1 moltbook help" >> /opt/csc/tmp/csc/run/client.in (get current help output)
2. Send: echo "AI 1 moltbook <method>" >> /opt/csc/tmp/csc/run/client.in
3. Wait 5 seconds, check response in channel or server log:
   journalctl --user -u csc-server.service -n 20 --no-pager | grep -E "Help for moltbook|<method>|Error"
4. Note: WORKS / FAILS / PARTIAL + any output or error message

## Report format (append to this file when done)
```
METHOD         | RESULT  | NOTES
---------------|---------|------
help           |         |
test           |         |
setup          |         |
register       |         |
status         |         |
post           |         |
post_link      |         |
comment        |         |
reply          |         |
upvote         |         |
downvote       |         |
delete_post    |         |
feed           |         |
submolt_feed   |         |
get_post       |         |
get_comments   |         |
search         |         |
create_submolt |         |
subscribe      |         |
unsubscribe    |         |
list_submolts  |         |
follow         |         |
unfollow       |         |
profile        |         |
update_profile |         |
notifications  |         |
```

## Done
When complete, write COMPLETE as the last line.


--- Agent Log ---
[run_agent] Agent: gemini-2.5-pro, Root: C:\csc, WIP: test_module_moltbook.md
[run_agent] Git pull to get work files...
[run_agent] Git pull complete
[run_agent] Starting Gemini (gemini-2.5-pro) for gemini-2.5-pro
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
Error when talking to Gemini API Full report available at: C:\Users\davey\AppData\Local\Temp\gemini-client-error-Turn.run-sendMessageStream-2026-03-13T13-58-35-744Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 18h20m48s.
    at classifyGoogleError (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:238:28)
    at retryWithBackoff (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:153:37)
    at process.processTicksAndRejections (node:internal/process/task_queues:103:5)
    at async GeminiChat.makeApiCallAndProcessStream (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:445:32)
    at async GeminiChat.streamWithRetries (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:265:40)
    at async Turn.run (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:70:30)
    at async GeminiClient.processTurn (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:478:26)
    at async GeminiClient.sendMessageStream (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:579:20)
    at async file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/dist/src/nonInteractiveCli.js:194:34
    at async main (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/dist/src/gemini.js:531:9) {
  cause: {
    code: 429,
    message: 'You have exhausted your capacity on this model. Your quota will reset after 18h20m48s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 66048159.171841,
  reason: 'QUOTA_EXHAUSTED'
}
An unexpected critical error occurred:[object Object]
[2026-03-13 08:58:36] [queue-worker] [INFO] ==================================================
[2026-03-13 08:58:36] [queue-worker] [INFO] Cycle start
[2026-03-13 08:58:36] [queue-worker] [INFO] git pull
Store data successful. Saved 1 items to 'C:\Users\davey\AppData\Local\Temp\csc\run\queue_worker_data.json'.
[2026-03-13 08:58:37] [queue-worker] [INFO] Scanned 0 pending workorders from all agents
[2026-03-13 08:58:37] [queue-worker] [INFO] Cycle end (idle)

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)


--- Agent Log ---
[run_agent] Agent: gemini-2.5-pro, Root: C:\csc, WIP: test_module_moltbook.md
[run_agent] Git pull to get work files...
[run_agent] Git pull complete
[run_agent] Starting Gemini (gemini-2.5-pro) for gemini-2.5-pro
YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
Error when talking to Gemini API Full report available at: C:\Users\davey\AppData\Local\Temp\gemini-client-error-Turn.run-sendMessageStream-2026-03-13T13-59-00-651Z.json TerminalQuotaError: You have exhausted your capacity on this model. Your quota will reset after 18h20m23s.
    at classifyGoogleError (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:238:28)
    at retryWithBackoff (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:153:37)
    at process.processTicksAndRejections (node:internal/process/task_queues:103:5)
    at async GeminiChat.makeApiCallAndProcessStream (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:445:32)
    at async GeminiChat.streamWithRetries (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:265:40)
    at async Turn.run (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:70:30)
    at async GeminiClient.processTurn (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:478:26)
    at async GeminiClient.sendMessageStream (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:579:20)
    at async file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/dist/src/nonInteractiveCli.js:194:34
    at async main (file:///C:/Users/davey/AppData/Roaming/npm/node_modules/@google/gemini-cli/dist/src/gemini.js:531:9) {
  cause: {
    code: 429,
    message: 'You have exhausted your capacity on this model. Your quota will reset after 18h20m23s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 66023233.252651,
  reason: 'QUOTA_EXHAUSTED'
}
An unexpected critical error occurred:[object Object]
[2026-03-13 08:59:01] [queue-worker] [INFO] ==================================================
[2026-03-13 08:59:01] [queue-worker] [INFO] Cycle start
[2026-03-13 08:59:01] [queue-worker] [INFO] git pull
Store data successful. Saved 1 items to 'C:\Users\davey\AppData\Local\Temp\csc\run\queue_worker_data.json'.
[2026-03-13 08:59:02] [queue-worker] [INFO] Scanned 0 pending workorders from all agents
[2026-03-13 08:59:02] [queue-worker] [INFO] Cycle end (idle)

INCOMPLETE: Agent task did not finish properly (missing COMPLETE marker)
