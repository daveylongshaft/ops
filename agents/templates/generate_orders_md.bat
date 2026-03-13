@echo off
REM generate_orders_md.bat
REM Generates the orders.md file for an agent's queue/in directory.
REM Takes AGENT_DIR and WO_FILENAME (must be in workorders/wip/) as arguments.

setlocal enableDelayedExpansion

set AGENT_DIR=%~1
set WO_FILENAME=%~2
set WIP_RELATIVE_PATH=ops/wo/wip/%~2
set TEMPLATE_PATH=%AGENT_DIR%\orders.md-template

echo usage: generate_orders_md.bat AGENT_DIR WO_FILENAME
echo generating "%AGENT_DIR%\queue\in\orders.md" for %WIP_RELATIVE_PATH%

REM Ensure output directory exists
if not exist "%AGENT_DIR%\queue\in" mkdir "%AGENT_DIR%\queue\in"

REM Determine the actual template file to use
set FINAL_TEMPLATE=
if exist "%TEMPLATE_PATH%" (
    set "FINAL_TEMPLATE=%TEMPLATE_PATH%"
) else (
    REM Fallback to default template if agent-specific not found
    set DEFAULT_TEMPLATE=agents\templates\orders.md-template
    if exist "!DEFAULT_TEMPLATE!" (
        set "FINAL_TEMPLATE=!DEFAULT_TEMPLATE!"
    ) else (
        echo ERROR: No template found at '%TEMPLATE_PATH%' or default '%DEFAULT_TEMPLATE%'. 1>&2
        exit /b 1
    )
)

REM Generate content using sed for reliable string replacement
REM Replace <wip_file_relative_pathspec> with actual WIP path (forward slashes)
set OUTPUT_FILE=%AGENT_DIR%\queue\in\orders.md
sed "s|<wip_file_relative_pathspec>|%WIP_RELATIVE_PATH%|g" "%FINAL_TEMPLATE%" > "%OUTPUT_FILE%"

if %errorlevel% equ 0 (
    echo Successfully generated %OUTPUT_FILE%
) else (
    echo ERROR: Failed to generate %OUTPUT_FILE% 1>&2
    exit /b 1
)
