@echo off
echo ===========================================
echo   AUDITAR - Criar Executavel
echo ===========================================
echo.
echo Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo Verificando/Instalando PyInstaller...
python -m pip install pyinstaller

echo.
echo Criando executavel...
python -m PyInstaller auditar.spec --clean

echo.
echo ===========================================
if exist "dist\AuditarContabilidade\AuditarContabilidade.exe" (
    echo   SUCESSO!
    echo   Aplicativo criado em: dist\AuditarContabilidade\
    echo   Execute: dist\AuditarContabilidade\AuditarContabilidade.exe
    echo ===========================================
    echo.
    echo Para distribuir, copie a pasta inteira:
    echo   dist\AuditarContabilidade\
) else (
    echo   ERRO ao criar executavel
    echo ===========================================
)
echo.
pause
