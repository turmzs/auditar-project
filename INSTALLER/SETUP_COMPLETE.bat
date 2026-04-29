@echo off
chcp 65001 >nul
echo ===========================================
echo   AUDITAR - Instalador Completo
echo ===========================================
echo.
echo Este instalador ira:
echo  1. Instalar Python (se necessario)
echo  2. Instalar dependencias do AUDITAR
echo  3. Instalar e configurar Ollama (IA)
echo  4. Baixar modelo de IA
echo.
echo Pressione qualquer tecla para iniciar...
pause >nul
cls

echo ===========================================
echo   ETAPA 1/4 - Python e Dependencias
echo ===========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.9+ de https://python.org
    echo Certifique-se de marcar "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.
echo Instalando dependencias...
cd /d "%~dp0.."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas!
echo.

echo ===========================================
echo   ETAPA 2/4 - Instalando Ollama (IA)
echo ===========================================
echo.
echo Isso pode levar alguns minutos...
echo.

REM Verificar se PowerShell está disponível
powershell -Command "Get-Host" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] PowerShell nao disponivel
    echo Pulando instalacao do Ollama.
    echo Voce pode instalar manualmente de ollama.com
    goto SKIP_OLLAMA
)

REM Executar instalador do Ollama
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "install_ollama.ps1"
if errorlevel 1 (
    echo [AVISO] Ollama nao foi instalado automaticamente
    echo O aplicativo funcionara, mas sem recursos de IA.
    echo Voce pode instalar manualmente depois em: https://ollama.com
) else (
    echo [OK] Ollama instalado e configurado!
)

:SKIP_OLLAMA

echo.
echo ===========================================
echo   ETAPA 3/4 - Verificando Instalacao
echo ===========================================
echo.

cd /d "%~dp0.."
python -c "import PyQt6, pptx, pandas, sqlite3; print('[OK] Todas as bibliotecas OK')"
if errorlevel 1 (
    echo [ERRO] Algumas bibliotecas nao foram instaladas corretamente
    pause
    exit /b 1
)

echo.
echo ===========================================
echo   ETAPA 4/4 - Finalizando
echo ===========================================
echo.

REM Criar atalho na area de trabalho
echo Criando atalho na Area de Trabalho...

set "TARGET=%~dp0..\app.py"
set "WORKINGDIR=%~dp0.."
set "ICON=%~dp0..\assets\logo_auditar.png"
set "SHORTCUT=%USERPROFILE%\Desktop\AUDITAR.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%TARGET%\"'; $Shortcut.WorkingDirectory = '%WORKINGDIR%'; $Shortcut.IconLocation = '%ICON%'; $Shortcut.Save()"

echo.
echo ===========================================
echo   INSTALACAO CONCLUIDA!
echo ===========================================
echo.
echo [✓] AUDITAR esta pronto para usar!
echo [✓] Atalho criado na Area de Trabalho
echo [✓] Ollama instalado (se aplicavel)
echo.
echo Para iniciar:
echo   - Clique duas vezes em AUDITAR na Area de Trabalho
echo   - Ou execute: EXECUTAR.bat
echo.
echo ===========================================
pause
