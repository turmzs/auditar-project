# PowerShell Script - Instalação Automática do Ollama
# Executa em modo silencioso e instala/configura tudo

param(
    [switch]$Silent = $true
)

$ProgressPreference = 'SilentlyContinue'
$ErrorActionPreference = 'Stop'

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    $timestamp = Get-Date -Format "HH:mm:ss"
    switch ($Type) {
        "Success" { Write-Host "[$timestamp] ✓ $Message" -ForegroundColor Green }
        "Error"   { Write-Host "[$timestamp] ✗ $Message" -ForegroundColor Red }
        "Warning" { Write-Host "[$timestamp] ⚠ $Message" -ForegroundColor Yellow }
        default   { Write-Host "[$timestamp] ℹ $Message" -ForegroundColor Cyan }
    }
}

function Test-OllamaInstalled {
    try {
        $ollama = Get-Command "ollama" -ErrorAction SilentlyContinue
        return $null -ne $ollama
    } catch {
        return $false
    }
}

function Test-OllamaRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# ============================================================
# MAIN INSTALLATION
# ============================================================

Write-Status "Iniciando instalacao do Ollama para AUDITAR..." "Info"

# Verificar se já está instalado
if (Test-OllamaInstalled) {
    Write-Status "Ollama ja esta instalado!" "Success"
} else {
    Write-Status "Ollama nao encontrado. Iniciando download..." "Warning"
    
    # Download do Ollama para Windows
    $downloadUrl = "https://ollama.com/download/OllamaSetup.exe"
    $installerPath = "$env:TEMP\OllamaSetup.exe"
    
    try {
        Write-Status "Baixando Ollama (aprox. 200MB)..." "Info"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        Write-Status "Download concluido!" "Success"
        
        # Instalar silenciosamente
        Write-Status "Instalando Ollama (pode levar alguns minutos)..." "Info"
        Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait -NoNewWindow
        Write-Status "Ollama instalado com sucesso!" "Success"
        
        # Limpar arquivo temporário
        Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        
    } catch {
        Write-Status "Erro ao instalar Ollama: $_" "Error"
        exit 1
    }
}

# Verificar/Aguardar serviço rodando
Write-Status "Verificando servico Ollama..." "Info"
$attempts = 0
$maxAttempts = 30

while (-not (Test-OllamaRunning)) {
    $attempts++
    if ($attempts -gt $maxAttempts) {
        Write-Status "Timeout aguardando Ollama iniciar" "Error"
        exit 1
    }
    
    # Tentar iniciar o Ollama se não estiver rodando
    if ($attempts -eq 5) {
        Write-Status "Tentando iniciar Ollama..." "Warning"
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    }
    
    Write-Status "Aguardando Ollama iniciar... (tentativa $attempts/$maxAttempts)" "Info"
    Start-Sleep -Seconds 2
}

Write-Status "Ollama esta rodando!" "Success"

# ============================================================
# BAIXAR MODELO
# ============================================================

Write-Status "Verificando modelo LLM..." "Info"

$modelName = "llama3.2"  # Modelo leve e eficiente

try {
    # Verificar se modelo já existe
    $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET
    $modelExists = $models.models | Where-Object { $_.name -like "*$modelName*" }
    
    if ($modelExists) {
        Write-Status "Modelo $modelName ja existe!" "Success"
    } else {
        Write-Status "Baixando modelo $modelName (aprox. 2GB)..." "Info"
        Write-Status "Isso pode levar alguns minutos dependendo da sua conexao..." "Warning"
        
        # Baixar modelo
        $body = @{
            name = $modelName
            stream = $false
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/pull" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 600
        
        Write-Status "Modelo $modelName baixado com sucesso!" "Success"
    }
} catch {
    Write-Status "Erro ao verificar/baixar modelo: $_" "Error"
    # Não é fatal, o app pode funcionar sem IA
}

# ============================================================
# FINALIZAR
# ============================================================

Write-Status "" "Info"
Write-Status "==========================================" "Success"
Write-Status "  OLLAMA CONFIGURADO COM SUCESSO!" "Success"
Write-Status "==========================================" "Success"
Write-Status "" "Info"
Write-Status "Ollama esta pronto para uso com AUDITAR." "Info"
Write-Status "O aplicativo pode usar IA inteligente agora!" "Success"

exit 0
