@echo off
REM run_agent.bat - Local agent runner for dmr_qwen_task_runner (uses cagent exec)
REM Usage: run_agent.bat <path-to-orders.md>

setlocal

set "WORKORDER_PATH=%~1"
set "SCRIPT_DIR=%~dp0"
set "AGENT_ROOT=%SCRIPT_DIR%.."
set "CSC_ROOT=%AGENT_ROOT%\..\.."

if "%WORKORDER_PATH%"=="" (
    echo ERROR: workorder path required
    exit /b 1
)

REM If relative path, try from CSC_ROOT
if not exist "%WORKORDER_PATH%" (
    if exist "%CSC_ROOT%\%WORKORDER_PATH%" (
        set "WORKORDER_PATH=%CSC_ROOT%\%WORKORDER_PATH%"
    )
)

if not exist "%WORKORDER_PATH%" (
    echo ERROR: Workorder not found: %WORKORDER_PATH%
    exit /b 1
)

set "YAML_PATH=%AGENT_ROOT%\cagent.yaml"
if not exist "%YAML_PATH%" (
    echo ERROR: cagent.yaml not found at %YAML_PATH%
    exit /b 1
)

echo [run_agent] Starting cagent exec for dmr_qwen_task_runner
echo [run_agent] YAML: %YAML_PATH%
echo [run_agent] Workorder: %WORKORDER_PATH%

REM Invoke cagent with the YAML config, piping workorder content
type "%WORKORDER_PATH%" | cagent exec "%YAML_PATH%" --working-dir "%CSC_ROOT%"

echo.
echo [INFO] Agent execution completed
exit /b %errorlevel%
