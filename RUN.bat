@echo off
cd /d "%~dp0"

REM Ativa o venv
call venv\Scripts\activate.bat

REM Roda o projeto
python main.py

pause
