@echo off
chcp 65001 >nul
echo ===========================================
echo   AUDITAR - Criar Instalador Completo
echo ===========================================
echo.
echo Este script ira:
echo   1. Compilar aplicativo (BUILD_EXE.bat)
echo   2. Compilar instalador Inno Setup
echo   3. Gerar: Instalar_AUDITAR_Completo.exe
echo.
pause
cls

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
set "ISS_FILE=%SCRIPT_DIR%AuditarSetup.iss"
set "INNO_COMPILER=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

echo ===========================================
echo   ETAPA 1/3 - Compilando Aplicativo
echo ===========================================
echo.

cd /d "%ROOT_DIR%"

if exist "dist\AuditarContabilidade" (
    echo [i] Pasta dist ja existe. Pulando compilacao.
    echo [i] Para recompilar, delete a pasta dist\ primeiro.
    choice /C SN /M "Deseja recompilar mesmo assim?"
    if errorlevel 2 goto SKIP_COMPILE
    if errorlevel 1 goto DO_COMPILE
)

:DO_COMPILE
call BUILD_EXE.bat
if errorlevel 1 (
    echo [ERRO] Falha ao compilar aplicativo!
    pause
    exit /b 1
)
goto CHECK_DIST

:SKIP_COMPILE
echo [OK] Usando compilacao existente.

:CHECK_DIST
echo.
echo ===========================================
echo   ETAPA 2/3 - Verificando Arquivos
echo ===========================================
echo.

if not exist "dist\AuditarContabilidade" (
    echo [ERRO] Pasta dist\AuditarContabilidade nao encontrada!
    echo Execute BUILD_EXE.bat primeiro.
    pause
    exit /b 1
)

echo [OK] Aplicativo compilado encontrado.

if not exist "%ISS_FILE%" (
    echo [ERRO] Arquivo AuditarSetup.iss nao encontrado!
    pause
    exit /b 1
)

echo [OK] Script Inno Setup encontrado.

if not exist "%INNO_COMPILER%" (
    echo [AVISO] Inno Setup nao encontrado no caminho padrao!
    echo.
    echo Onde esta instalado o Inno Setup?
    echo Padrao: C:\Program Files (x86)\Inno Setup 6\
    echo.
    set /p INNO_PATH="Digite o caminho completo para ISCC.exe: "
    set "INNO_COMPILER=%INNO_PATH%"
)

if not exist "%INNO_COMPILER%" (
    echo [ERRO] Inno Setup nao encontrado!
    echo.
    echo Para criar o instalador completo, instale o Inno Setup:
    echo   https://jrsoftware.org/isdl.php
    echo.
    echo Ou envie apenas o aplicativo compilado em:
    echo   dist\AuditarContabilidade\
    pause
    exit /b 1
)

echo [OK] Inno Setup encontrado: %INNO_COMPILER%

echo.
echo ===========================================
echo   ETAPA 3/3 - Compilando Instalador
echo ===========================================
echo.
echo Compilando... Aguarde...
echo.

"%INNO_COMPILER%" "%ISS_FILE%"
if errorlevel 1 (
    echo [ERRO] Falha ao compilar instalador!
    pause
    exit /b 1
)

echo.
echo ===========================================
echo   SUCESSO! Instalador Criado!
echo ===========================================
echo.

cd /d "%SCRIPT_DIR%"

if exist "Instalar_AUDITAR_Completo.exe" (
    for %%F in ("Instalar_AUDITAR_Completo.exe") do (
        echo [OK] Arquivo: %%F
        echo [OK] Tamanho: %%~zF bytes
    )
    echo.
    echo ===========================================
    echo   ONDE ENCONTRAR:
    echo ===========================================
    echo.
    echo Local: %SCRIPT_DIR%Instalar_AUDITAR_Completo.exe
    echo.
    echo ===========================================
    echo   PARA DISTRIBUIR:
    echo ===========================================
    echo.
    echo Envie apenas este arquivo para sua equipe:
    echo   Instalar_AUDITAR_Completo.exe
    echo.
    echo O usuario apenas executa e segue o assistente!
    echo Tudo e instalado automaticamente:
    echo   - Aplicativo AUDITAR
    echo   - Ollama (IA)
    echo   - Modelo de linguagem
    echo   - Atalhos
    echo.
    echo ===========================================
) else (
    echo [ERRO] Arquivo de saida nao encontrado!
    echo Verifique erros acima.
)

echo.
pause
