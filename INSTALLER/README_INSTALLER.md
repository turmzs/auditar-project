# 🚀 Instalador Completo AUDITAR

## O que faz este instalador?

Este é um **instalador all-in-one** que configura tudo automaticamente:

### ✅ Instala automaticamente:
1. **Python** (se necessário) - avisa para instalar manualmente
2. **Todas as dependências** - PyQt6, python-pptx, pandas, etc.
3. **Ollama** (motor de IA) - baixa e instala silenciosamente
4. **Modelo LLM** (llama3.2) - baixa ~2GB de modelo de IA
5. **Atalho na Área de Trabalho** - pronto para usar!

---

## 🎯 Como Usar

### Método 1 - Instalação Completa (Recomendado)
```
1. Execute: INSTALLER\SETUP_COMPLETE.bat
2. Aguarde a instalação (5-10 minutos)
3. Pronto! Use o atalho na Área de Trabalho
```

### Método 2 - Apenas Dependências (sem IA)
```
1. Execute: INSTALAR.bat
2. Instala apenas o básico
3. Funciona sem Ollama (temas pré-definidos)
```

### Método 3 - Para Desenvolvedores
```bash
pip install -r requirements.txt
python app.py
```

---

## 📦 Estrutura do Instalador

```
INSTALLER/
├── README_INSTALLER.md      ← Este arquivo
├── SETUP_COMPLETE.bat       ← Instalador principal
├── install_ollama.ps1       ← Script PowerShell (automático)
└── UNINSTALL.bat           ← Removedor (futuro)
```

---

## 🔧 Requisitos do Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| Windows | 10 | 11 |
| RAM | 4GB | 8GB+ |
| Espaço | 3GB | 5GB+ |
| Internet | Sim (para Ollama) | Banda larga |

---

## ⚠️ Notas Importantes

### Sobre o Ollama:
- **Download**: ~200MB (instalador) + ~2GB (modelo)
- **Tempo**: 5-15 minutos dependendo da internet
- **Offline**: Depois de instalado, funciona sem internet
- **Opcional**: O app funciona sem Ollama (temas pré-definidos)

### Sem Privilégios de Admin:
- O instalador tenta instalar sem admin
- Se falhar, pedirá elevação automaticamente
- Ollama requer admin na primeira instalação

---

## 🐛 Solução de Problemas

### "Python não encontrado"
→ Instale Python 3.9+ de https://python.org
→ **IMPORTANTE**: Marque "Add Python to PATH"

### "Ollama falhou ao instalar"
→ Instale manualmente: https://ollama.com/download
→ O app funcionará sem IA (temas pré-definidos)

### "Modelo não baixou"
→ Execute no terminal: `ollama pull llama3.2`
→ Ou use sem IA (funciona perfeitamente!)

---

## 🎨 Após Instalação

### Modos de Funcionamento:

1. **Com IA (Ollama instalado)**
   - Escolha "Apresentação com IA Inteligente"
   - Digite comandos como: "fundo escuro, verde"
   - IA gera designs personalizados

2. **Sem IA (modo padrão)**
   - Escolha tema no dropdown: "Auditar Clássico", "Escuro", etc.
   - 6 temas pré-definidos disponíveis
   - Funciona 100% offline

---

## 📝 Changelog do Instalador

### v1.0 (Atual)
- Instalação automática de Ollama
- Download automático de modelo LLM
- Verificação de dependências
- Criação de atalho na Área de Trabalho
- Fallback para funcionar sem IA

---

## 💡 Dica Pro

**Para distribuir para sua equipe:**
1. Execute `BUILD_EXE.bat` após instalar
2. Distribua a pasta `dist/AuditarContabilidade/`
3. Os usuários NÃO precisam instalar nada!
4. O executável inclui tudo (Python, dependências, assets)

**Nota**: O executável ainda precisa de Ollama instalado na máquina para usar IA. Para incluir Ollama no executável, seria necessário ~2GB extras.
