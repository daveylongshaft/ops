@echo off
REM run_agent.bat - Universal agent runner for Windows
REM Calls run_agent.py which auto-detects agent type from directory name

setlocal

set "WORKORDER_PATH=%~1"

if "%WORKORDER_PATH%"=="" (
    echo ERROR: workorder path required
    exit /b 1
)

if not exist "%WORKORDER_PATH%" (
    echo ERROR: Workorder not found: %WORKORDER_PATH%
    exit /b 1
)

REM Run the Python script in the same directory as this batch file
python "%~dp0run_agent.py" "%WORKORDER_PATH%"
exit /b %errorlevel%
