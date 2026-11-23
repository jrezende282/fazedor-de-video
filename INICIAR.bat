@echo off
setlocal
chcp 65001 >nul
title Animatik - iniciando
cd /d "%~dp0"
set PYTHONUTF8=1
set "PLAYWRIGHT_BROWSERS_PATH=%~dp0navegador"
set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Links;%PATH%"

echo.
echo  ==================================================
echo     ANIMATIK  -  videos animados com IA
echo  ==================================================
echo.

rem ---------------------------------------------------------- 1. Python 3.10+
set "PY="
py -3.12 --version >nul 2>&1 && set "PY=py -3.12"
if not defined PY py -3 -c "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)" >nul 2>&1 && set "PY=py -3"
if not defined PY python -c "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)" >nul 2>&1 && set "PY=python"
if defined PY goto python_ok
echo  [1/4] Python nao encontrado. Instalando o Python 3.12...
echo        Se o Windows perguntar se pode fazer alteracoes, clique em SIM.
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
echo.
echo  Python instalado. FECHE esta janela e abra o INICIAR.bat de novo.
pause
exit /b
:python_ok
echo  [1/4] Python OK

rem ---------------------------------------------------------- 2. FFmpeg
where ffmpeg >nul 2>&1 && goto ffmpeg_ok
echo  [2/4] Instalando o FFmpeg...
winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
where ffmpeg >nul 2>&1 && goto ffmpeg_ok
echo.
echo  FFmpeg instalado. FECHE esta janela e abra o INICIAR.bat de novo.
pause
exit /b
:ffmpeg_ok
echo  [2/4] FFmpeg OK

rem ---------------------------------------------------------- 3. Bibliotecas + navegador do gravador (so na primeira vez)
if exist ".instalado_v1" goto libs_ok
echo  [3/4] Instalando as bibliotecas e o gravador. Leva alguns minutos, so na primeira vez...
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
if errorlevel 1 goto erro_libs
%PY% -m playwright install chromium
if errorlevel 1 goto erro_libs
echo ok> .instalado_v1
:libs_ok
echo  [3/4] Bibliotecas OK

rem ---------------------------------------------------------- 4. Chave da API do Claude (opcional)
if defined ANTHROPIC_API_KEY goto chave_ok
if exist "chave_api.txt" goto chave_arquivo
if exist ".sem_chave" goto chave_ok
echo.
echo  [4/4] (Opcional) Chave da API do Claude.
echo        Com ela, a IA escreve o roteiro a partir de um tema e le o estilo dos seus exemplos.
echo        Sem ela, voce escreve o texto e o Animatik monta o video do mesmo jeito.
echo        A chave fica SO neste PC, no arquivo chave_api.txt. Nao mande ela para ninguem.
set /p "NOVA_CHAVE=        Cole a chave e aperte Enter (ou so Enter para pular): "
if "%NOVA_CHAVE%"=="" goto pular_chave
> chave_api.txt echo %NOVA_CHAVE%
:chave_arquivo
set /p ANTHROPIC_API_KEY=<chave_api.txt
goto chave_ok
:pular_chave
echo ok> .sem_chave
:chave_ok
echo  [4/4] Chave OK

rem ---------------------------------------------------------- liga
echo.
echo  Ligando o Animatik...
start "Animatik (nao feche)" cmd /k %PY% main.py iniciar
timeout /t 5 /nobreak >nul
start "" http://localhost:8100

echo.
echo  ==================================================
echo   Tudo ligado! O painel abriu no navegador:
echo     http://localhost:8100
echo   Para DESLIGAR: feche a janela "Animatik (nao feche)"
echo  ==================================================
echo.
pause
exit /b

:erro_libs
echo.
echo  ERRO ao instalar. Tire um print desta janela e mande pro Claude.
pause
exit /b
