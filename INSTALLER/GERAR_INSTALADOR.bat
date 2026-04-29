@echo off
echo ===========================================
echo   AUDITAR - Gerar Instalador Unico
echo ===========================================
echo.
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..
set ISS_FILE=%SCRIPT_DIR%AuditarSetup.iss

REM Buscar Inno Setup em varios locais possiveis
set INNO_COMPILER=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if not exist "%INNO_COMPILER%" set INNO_COMPILER=C:\Program Files\Inno Setup 6\ISCC.exe
if not exist "%INNO_COMPILER%" set INNO_COMPILER=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe
if not exist "%INNO_COMPILER%" set INNO_COMPILER=%USERPROFILE%\AppData\Local\Programs\Inno Setup 6\ISCC.exe

echo Verificando caminho: %ROOT_DIR%\dist\AuditarContabilidade
if not exist "%ROOT_DIR%\dist\AuditarContabilidade" (
    echo [ERRO] Aplicativo ainda nao compilado!
    echo.
    echo Caminho verificado: %ROOT_DIR%\dist\AuditarContabilidade
    echo Diretorio atual: %CD%
    echo SCRIPT_DIR: %SCRIPT_DIR%
    echo ROOT_DIR: %ROOT_DIR%
    echo.
    echo Execute primeiro: BUILD_EXE.bat
    pause
    exit /b 1
)

echo [OK] Aplicativo encontrado.

if not exist "%INNO_COMPILER%" (
    echo [ERRO] Inno Setup nao encontrado!
    echo.
    echo Caminhos verificados:
    echo   C:\Program Files (x86)\Inno Setup 6\
    echo   C:\Program Files\Inno Setup 6\
    echo   %%LOCALAPPDATA%%\Programs\Inno Setup 6\
    echo.
    echo Instale o Inno Setup de:
    echo   https://jrsoftware.org/isdl.php
    echo.
    echo Ou informe o caminho manualmente:
    set /p INNO_COMPILER="Caminho completo para ISCC.exe: "
    if not exist "%INNO_COMPILER%" (
        echo [ERRO] Caminho invalido!
        pause
        exit /b 1
    )
)

echo [OK] Inno Setup encontrado.
echo.
echo Gerando instalador...
"%INNO_COMPILER%" "%ISS_FILE%"
if errorlevel 1 (
    echo [ERRO] Falha ao criar instalador!
    pause
    exit /b 1
)
cd /d "%SCRIPT_DIR%"
echo.
echo ===========================================
echo   INSTALADOR CRIADO COM SUCESSO!
echo ===========================================
echo.
if exist "Instalar_AUDITAR_Completo.exe" (
    echo [OK] Arquivo: Instalar_AUDITAR_Completo.exe
    echo [OK] Local: %SCRIPT_DIR%
    echo.
    echo Envie este arquivo ao colega!
) else (
    echo [ERRO] Arquivo nao foi criado.
)
pause
