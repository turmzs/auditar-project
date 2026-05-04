; Inno Setup Script - Instalador Completo AUDITAR
; Gera um único arquivo .exe que instala tudo automaticamente

#define AppName "AUDITAR - Planejamento Tributário"
#define AppVersion "3.0"
#define AppPublisher "AUDITAR S/S"
#define AppURL "https://auditar.com.br"
#define AppExeName "AuditarContabilidade.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\AuditarContabilidade
DefaultGroupName=AUDITAR Contabilidade
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE.txt
OutputDir=.
OutputBaseFilename=Instalar_AUDITAR_Completo
SetupIconFile=..\assets\logo_auditar.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName=AUDITAR Contabilidade
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "installollama"; Description: "Instalar Ollama (IA Inteligente) - Recomendado"; GroupDescription: "Componentes Opcionais:"; Flags: checkedonce

[Files]
; Arquivos principais do aplicativo
Source: "..\dist\AuditarContabilidade\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Scripts de instalação
Source: "install_ollama_silent.ps1"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Instalar Ollama silenciosamente (se marcado)
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; \
    Parameters: "-ExecutionPolicy Bypass -File ""{tmp}\install_ollama_silent.ps1"" -InstallDir ""{app}"""; \
    Description: "Instalando Ollama e configurando IA..."; \
    Flags: runascurrentuser waituntilterminated; \
    Tasks: installollama; \
    StatusMsg: "Configurando Ollama (IA Inteligente)... Isso pode levar alguns minutos..."

; Executar o aplicativo após instalação
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Opcional: Remover Ollama no desinstalar (desativado por padrão)
; Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-Command ""Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force; & $env:LOCALAPPDATA\Programs\Ollama\uninstall.exe /S"""; Flags: runhidden

[Registry]
; Adicionar informações ao registro para facilitar atualizações futuras
Root: HKCU; Subkey: "Software\AuditarContabilidade"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\AuditarContabilidade"; ValueType: string; ValueName: "Version"; ValueData: "{#AppVersion}"

[Messages]
; Mensagens personalizadas em português
brazilianportuguese.WelcomeLabel1=Bem-vindo ao Instalador do [name]
brazilianportuguese.WelcomeLabel2=Este instalador vai instalar o [name] no seu computador.%n%nO aplicativo inclui:%n• Sistema de Contabilidade Consultiva%n• Geração de Apresentações Profissionais%n• IA Inteligente (Ollama) - Opcional%n%nClique em Avançar para continuar.
brazilianportuguese.FinishedLabel=O [name] foi instalado com sucesso!%n%nClique em Concluir para abrir o aplicativo.

[Code]
// Código Pascal para eventos do instalador
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;
