# R08: Copy ChatGPT AI Client

## Depends: R01

## Task
Copy ChatGPT AI client files into the new package.

## Steps
```bash
ls packages/csc-chatgpt/csc_chatgpt/ 2>/dev/null || ls packages/csc-chatgpt/*.py
cp packages/csc-chatgpt/csc_chatgpt/*.py packages/csc-service/csc_service/clients/chatgpt/ 2>/dev/null || \
cp packages/csc-chatgpt/*.py packages/csc-service/csc_service/clients/chatgpt/
```

Key files:
- `chatgpt.py` - ChatGPT client implementation
- `main.py` - Entry point

## Verification
- `ls packages/csc-service/csc_service/clients/chatgpt/chatgpt.py` exists


DEAD END - csc-service package already consolidated and operational
