@echo off
chcp 65001 >nul 2>&1
echo.
echo ============================================================
echo   Lex Study Foundation - Environment Setup
echo ============================================================
echo.

cd /d "%~dp0\.."

echo [1/3] Creating virtual environment...
python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create venv. Is Python 3.11+ installed?
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
call .venv\Scripts\activate.bat
pip install -e ".[dev]"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)

echo [3/3] Installing pre-commit hooks...
pre-commit install

echo.
echo ============================================================
echo   Setup complete!
echo ============================================================
echo.
echo   Activate venv:  .venv\Scripts\activate.bat
echo   Run CLI:        python -m lex_study_foundation --help
echo   Run doctor:     python -m lex_study_foundation doctor
echo   Run tests:      pytest
echo.
pause
