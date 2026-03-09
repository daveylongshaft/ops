# R07: Copy Gemini AI Client

## Depends: R01

## Task
Copy Gemini AI client files into the new package.

## Steps
```bash
ls packages/csc-gemini/csc_gemini/ 2>/dev/null || ls packages/csc-gemini/*.py
cp packages/csc-gemini/csc_gemini/*.py packages/csc-service/csc_service/clients/gemini/ 2>/dev/null || \
cp packages/csc-gemini/*.py packages/csc-service/csc_service/clients/gemini/
```

Key files:
- `gemini.py` - Gemini client implementation
- `client.py` - Base client (if separate from gemini.py)
- `main.py` - Entry point
- `macros.py` - Macro support

## Verification
- `ls packages/csc-service/csc_service/clients/gemini/gemini.py` exists


DEAD END - csc-service package already consolidated and operational
