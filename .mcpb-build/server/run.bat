@echo off
REM Windows launcher for YouTube Extract MCP Server
REM Tries multiple Python commands to find one that works

REM Try py launcher first (most reliable on Windows)
where py >nul 2>nul
if %ERRORLEVEL% == 0 (
    py -3 "%~dp0run.py" %*
    exit /b %ERRORLEVEL%
)

REM Try python3
where python3 >nul 2>nul
if %ERRORLEVEL% == 0 (
    python3 "%~dp0run.py" %*
    exit /b %ERRORLEVEL%
)

REM Try python
where python >nul 2>nul
if %ERRORLEVEL% == 0 (
    python "%~dp0run.py" %*
    exit /b %ERRORLEVEL%
)

REM No Python found
echo ERROR: Python not found in PATH 1>&2
echo. 1>&2
echo Please install Python 3.11 or later from: 1>&2
echo https://www.python.org/downloads/ 1>&2
echo. 1>&2
echo During installation, make sure to check "Add Python to PATH" 1>&2
exit /b 1
