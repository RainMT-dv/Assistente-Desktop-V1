@echo off
echo ============================================
echo   SETUP - Assistente Desktop V1
echo   Criando ambiente virtual Python
echo ============================================
echo.

REM Vai pra pasta do projeto
cd /d "%~dp0"

REM Tenta encontrar o Python no PATH do sistema
set PYTHON_CMD=python

echo [1/4] Verificando Python...
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale o Python 3.10+ em https://python.org e marque "Add to PATH".
    pause
    exit /b 1
)
%PYTHON_CMD% --version
echo.

echo [2/4] Criando ambiente virtual...
if exist "venv" (
    echo venv ja existe, pulando...
) else (
    %PYTHON_CMD% -m venv venv
)
echo.

echo [3/4] Ativando venv e instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

echo [4/5] Configurando arquivos locais...
if not exist "config\emotion_profiles.json" (
    copy "config\emotion_profiles.example.json" "config\emotion_profiles.json" >nul
    echo emotion_profiles.json criado a partir do exemplo.
)
echo.

echo [5/5] Verificando instalacao...
python -c "import edge_tts; print('edge-tts OK')"
python -c "import aiohttp; print('aiohttp OK')"
python -c "import pygame; print('pygame OK')"
echo.

echo ============================================
echo   SETUP COMPLETO!
echo ============================================
echo.
echo Pra rodar o projeto:
echo   1. Edite config/settings.json e adicione sua API key
echo   2. Clique duas vezes em RUN.bat
echo   OU
echo   1. Abra o terminal nesta pasta
echo   2. Digite: venv\Scripts\activate
echo   3. Digite: python main.py
echo.
pause
