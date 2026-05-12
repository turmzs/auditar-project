# Instalação Silenciosa do Ollama para Inno Setup
# Chamado automaticamente durante a instalação

param(
    [string]$InstallDir = "$env:LOCALAPPDATA\Programs\Ollama"
)

$ProgressPreference = 'SilentlyContinue'
$ErrorActionPreference = 'Stop'

$logFile = "$env:TEMP\auditar_ollama_install.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logFile -Value $logEntry
    
    # Também escreve no console (visível pelo Inno Setup)
    switch ($Level) {
        "ERROR"   { Write-Host "[ERRO] $Message" -ForegroundColor Red }
        "SUCCESS" { Write-Host "[OK] $Message" -ForegroundColor Green }
        default   { Write-Host $Message }
    }
}

function Test-OllamaInstalled {
    try {
        $ollamaPath = Join-Path $InstallDir "ollama.exe"
        return Test-Path $ollamaPath
    } catch {
        return $false
    }
}

function Test-OllamaRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# ============================================================
# MAIN
# ============================================================

Write-Log "Iniciando instalacao do Ollama para AUDITAR..."
Write-Log "Diretorio de instalacao: $InstallDir"

# Verificar se já está instalado
if (Test-OllamaInstalled) {
    Write-Log "Ollama ja esta instalado! Verificando servico..." "SUCCESS"
} else {
    Write-Log "Ollama nao encontrado. Iniciando download..."
    
    # Download do Ollama
    $downloadUrl = "https://ollama.com/download/OllamaSetup.exe"
    $installerPath = "$env:TEMP\OllamaSetup.exe"
    
    try {
        Write-Log "Baixando Ollama (~200MB)..."
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        Write-Log "Download concluido!" "SUCCESS"
        
        # Instalar silenciosamente
        Write-Log "Instalando Ollama (modo silencioso)..."
        $process = Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait -PassThru
        
        if ($process.ExitCode -ne 0) {
            throw "Instalacao do Ollama retornou codigo: $($process.ExitCode)"
        }
        
        Write-Log "Ollama instalado com sucesso!" "SUCCESS"
        
        # Limpar
        Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        
    } catch {
        Write-Log "Erro ao instalar Ollama: $_" "ERROR"
        exit 1
    }
}

# Aguardar serviço
Write-Log "Aguardando servico Ollama iniciar..."
$attempts = 0
$maxAttempts = 20

while (-not (Test-OllamaRunning)) {
    $attempts++
    if ($attempts -gt $maxAttempts) {
        Write-Log "Timeout aguardando Ollama. Tentando iniciar manualmente..." "WARNING"
        
        # Tentar iniciar
        $ollamaExe = Join-Path $InstallDir "ollama.exe"
        if (Test-Path $ollamaExe) {
            Start-Process $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
            Start-Sleep -Seconds 3
        }
        
        # Tentar novamente
        if (-not (Test-OllamaRunning)) {
            Write-Log "Nao foi possivel iniciar Ollama automaticamente" "WARNING"
            Write-Log "O aplicativo funcionara sem IA (temas pre-definidos disponiveis)" "INFO"
            exit 0  # Não é erro fatal
        }
        break
    }
    
    Write-Log "Aguardando... ($attempts/$maxAttempts)"
    Start-Sleep -Seconds 2
}

Write-Log "Ollama esta rodando!" "SUCCESS"

# Baixar modelo
$modelName = "tinyllama"
Write-Log "Verificando modelo $modelName..."

try {
    $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5
    $modelExists = $models.models | Where-Object { $_.name -like "*$modelName*" }
    
    if ($modelExists) {
        Write-Log "Modelo $modelName ja existe!" "SUCCESS"
    } else {
        Write-Log "Baixando modelo $modelName (~600MB)..."
        Write-Log "Isso pode levar alguns minutos dependendo da internet."
        Write-Log "A tela pode ficar parada, mas o download esta em andamento..."
        Write-Log "Por favor, NAO feche esta janela."
        Write-Log ""
        
        # Usar stream para mostrar progresso
        $body = @{
            name = $modelName
            stream = $true
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/pull" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 900
        
        Write-Log "Modelo $modelName baixado com sucesso!" "SUCCESS"
    }
} catch {
    Write-Log "Erro ao baixar modelo: $_" "ERROR"
    Write-Log "O aplicativo funcionara, mas sem recursos de IA" "WARNING"
    exit 0  # Não é erro fatal
}

Write-Log "========================================"
Write-Log "  CONFIGURACAO CONCLUIDA COM SUCESSO!" "SUCCESS"
Write-Log "========================================"
Write-Log "Ollama e IA estao prontos para uso!"

exit 0
