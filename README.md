# Scripts de Recompilação - AUDITAR

Esta pasta contém os scripts atualizados para recompilar o aplicativo AUDITAR com as melhorias implementadas.

## Arquivos Incluídos

- **BUILD_EXE.bat** - Script para compilar o aplicativo com PyInstaller
- **auditar.spec** - Configuração do PyInstaller (com console habilitado para debug)
- **GERAR_INSTALADOR.bat** - Script para gerar o instalador Inno Setup

## Como Usar

### Passo 1: Compilar o Aplicativo

1. Copie os arquivos desta pasta para a raiz do projeto (`AUDITAR_APP_DESKTOP\`)
2. Execute `BUILD_EXE.bat`
3. O executável será gerado em `dist\AuditarContabilidade\AuditarContabilidade.exe`

### Passo 2: Gerar o Instalador (Opcional)

1. Certifique-se de que o Inno Setup 6 está instalado
2. Execute `GERAR_INSTALADOR.bat`
3. O instalador será gerado em `INSTALLER\Instalar_AUDITAR_Completo.exe`

## Configurações Atuais

### auditar.spec
- **Console habilitado** (`console=True`) - Permite ver logs de debug
- **Modo pasta** (`onedir`) - Mais estável para PyQt6
- **Ícone**: `assets/logo_auditar.png`

### Melhorias Implementadas

- Logs detalhados no gerador de IA para identificar erros
- Correções automáticas de JSON malformado
- Detecção de "preto" e "branco" nos comandos de IA
- Proteção contra erros para evitar fechamento do app

## Observações

- Para distribuição final, altere `console=True` para `console=False` no `auditar.spec`
- Sempre limpe as pastas `build` e `dist` antes de recompilar (o script faz isso automaticamente)
- O script `GERAR_INSTALADOR.bat` assume que o app já foi compilado

## Troubleshooting

### Erro: "Ollama não disponível"
- Verifique se o Ollama está instalado e rodando
- Acesse `http://localhost:11434/api/tags` para testar

### Erro: "JSON inválido"
- Os logs do console vão mostrar o JSON problemático
- O fallback será usado automaticamente

### Cores não mudam
- Use comandos explícitos como "Fundo branco e texto preto"
- Verifique os logs no console para ver as cores escolhidas pela IA
