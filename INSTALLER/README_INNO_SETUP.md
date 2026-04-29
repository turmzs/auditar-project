# 🚀 Instalador Único - Inno Setup

## O que é?

Este instalador cria um **único arquivo .exe** que instala:
1. ✅ Aplicativo AUDITAR (com todas as dependências)
2. ✅ Ollama (motor de IA)
3. ✅ Modelo de linguagem (llama3.2)
4. ✅ Atalhos no Menu Iniciar e Área de Trabalho

---

## 📦 Pré-requisitos para Compilar

### 1. Instalar Inno Setup
```
1. Baixe de: https://jrsoftware.org/isdl.php
2. Instale a versão "innosetup-x.x.x.exe"
3. Mantenha as opções padrão
```

### 2. Arquivos necessários
Antes de compilar, você precisa:
```
✓ app.py compilado (dist\AuditarContabilidade\)
   → Execute primeiro: BUILD_EXE.bat

✓ Inno Setup instalado
✓ Arquivo .iss (já fornecido: AuditarSetup.iss)
```

---

## 🔨 Como Compilar o Instalador

### Método 1 - Script Automático (Recomendado)

```bash
# Execute este arquivo:
INSTALLER\BUILD_INSTALLER.bat
```

Isso irá:
1. Compilar o aplicativo (BUILD_EXE.bat)
2. Compilar o instalador Inno Setup
3. Gerar: `Instalar_AUDITAR_Completo.exe`

---

### Método 2 - Manual pelo Inno Setup

```
1. Abra o Inno Setup Compiler
2. File → Open → Selecione: INSTALLER\AuditarSetup.iss
3. Build → Compile
4. Aguarde a compilação
5. Resultado: INSTALLER\Instalar_AUDITAR_Completo.exe
```

---

## 📁 Estrutura do Instalador

```
Instalar_AUDITAR_Completo.exe  (30-50MB)
├── App AUDITAR (PyInstaller)
│   ├── Python embutido
│   ├── Bibliotecas (PyQt6, pptx, etc.)
│   ├── Código do app
│   └── Assets (logo, templates)
│
├── Instalador Ollama (automático)
│   ├── Baixa OllamaSetup.exe (~200MB)
│   ├── Instala silenciosamente
│   ├── Baixa modelo llama3.2 (~2GB)
│   └── Configura tudo
│
└── Atalhos do Windows
    ├── Menu Iniciar
    ├── Área de Trabalho
    └── Desinstalador
```

**Tamanho final do instalador**: ~30-50MB
**Espaço após instalação**: ~5GB (com Ollama e modelo)

---

## 🎯 Como Usar o Instalador Gerado

### Para o usuário final:

```
1. Recebe: Instalar_AUDITAR_Completo.exe
2. Executa (clica duas vezes)
3. Segue o assistente (Next, Next, Finish)
4. Aguarda instalação automática (5-15 minutos)
5. PRONTO! 🎉
```

O usuário vê:
- Tela de boas-vindas
- Licença (se houver)
- Diretório de instalação
- Opções (incluir Ollama, criar atalho)
- Barra de progresso
- Tela de conclusão

---

## ⚙️ Opções do Instalador

Durante a instalação, o usuário pode escolher:

| Opção | Descrição | Recomendado |
|-------|-----------|-------------|
| ☑ Criar atalho na Área de Trabalho | Ícone do app | ✅ Sim |
| ☑ Instalar Ollama (IA) | Motor de IA + modelo | ✅ Sim |

Se desmarcar "Ollama":
- App instala normalmente
- Funciona com temas pré-definidos (6 opções)
- Pode instalar Ollama depois manualmente

---

## 🔧 Personalização

### Alterar nome do arquivo gerado:
```pascal
; No arquivo AuditarSetup.iss, linha:
OutputBaseFilename=Instalar_AUDITAR_Completo
```

### Alterar versão:
```pascal
; No arquivo AuditarSetup.iss:
#define AppVersion "1.0"
```

### Alterar modelo de IA:
```powershell
; No arquivo install_ollama_silent.ps1:
$modelName = "llama3.2"
; Mude para: "llama3.1", "mistral", "gemma", etc.
```

---

## 🐛 Solução de Problemas

### "Inno Setup não encontrado"
→ Instale de: https://jrsoftware.org/isdl.php

### "Erro ao compilar: dist\AuditarContabilidade não existe"
→ Execute primeiro: `BUILD_EXE.bat`

### "Instalador não incluiu Ollama"
→ Verifique se `install_ollama_silent.ps1` está na pasta INSTALLER\

---

## 💡 Dicas

### Para criar instalador leve (sem IA):
```
1. Abra AuditarSetup.iss
2. Procure: [Tasks]
3. Altere: Checked: yes para Checked: no
4. Recompile
```

### Para múltiplos idiomas:
```pascal
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
```

### Assinatura digital (profissional):
```pascal
[Setup]
SignTool=signtool
SignedUninstaller=yes
```

---

## 📞 Suporte

- Inno Setup Docs: https://jrsoftware.org/ishelp/
- Ollama Docs: https://github.com/ollama/ollama

---

**Pronto para distribuir!** 🚀
