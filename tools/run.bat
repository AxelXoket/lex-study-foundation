@echo off
chcp 65001 >nul 2>&1

cd /d "%~dp0\.."

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Run tools\setup_env.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m lex_study_foundation %*
