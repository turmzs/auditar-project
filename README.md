# AUDITAR - Sistema de Gestão Contábil

Sistema desktop completo para gestão contábil de empresas, com cálculo automático de impostos, geração de apresentações em PowerPoint e integração com Inteligência Artificial.

## 🎯 Funcionalidades Principais

### 1. Gestão de Empresas
- Cadastro de empresas com CNPJ, responsável, cidade e estado
- Definição do regime tributário (Simples Nacional, Lucro Presumido ou Lucro Real)
- Gerenciamento de dados mensais por empresa

### 2. Cálculo Automático de Impostos
- **Simples Nacional**: Cálculo baseado nas tabelas oficiais 2024 com faixas progressivas e parcela a deduzir
  - Anexo I (Comércio)
  - Anexo III (Serviços)
  - Fórmula: `(Receita × Alíquota) - (Parcela a Deduzir / 12)`

- **Lucro Presumido (Mensal)**: Cálculo com presunções por tipo de atividade
  - Serviços: 32% para IRPJ e CSLL
  - Comércio/Indústria: 8% para IRPJ, 12% para CSLL
  - Transporte: 16% para IRPJ e CSLL
  - IRPJ: 15% + adicional de 10% acima de R$ 20.000 (base de cálculo mensal)
  - CSLL: 9%
  - PIS: 0,65%
  - COFINS: 3%

- **Lucro Presumido (Trimestral)**: Cálculo específico para DARF trimestral
  - Soma das receitas dos 3 meses do trimestre
  - IRPJ: 15% + adicional de 10% acima de R$ 60.000 (base de cálculo trimestral)
  - CSLL: 9%
  - PIS: 0,65%
  - COFINS: 3%
  - Exibe total trimestral e média mensal para provisionamento

- **Lucro Real**: Cálculo sobre o lucro efetivo
  - Base: Receita - Custos - Despesas
  - IRPJ: 15% + adicional de 10% acima de R$ 20.000
  - CSLL: 9%
  - PIS: 0,65%
  - COFINS: 3%

### 3. Lançamento de Dados Mensais
- Receita bruta
- Custos detalhados (salários, aluguel, outros)
- Despesas detalhadas (água/luz/telefone, material, outros)
- Cálculo automático de totais e lucro operacional
- Cálculo automático de impostos baseado no regime

### 4. Geração de Apresentações PowerPoint
- Geração automática de slides com dados financeiros
- Gráficos de receita, custos, despesas e lucro
- Múltiplos templates disponíveis:
  - Corporativo Escuro
  - Minimalista Branco
  - Moderno Gradiente
- Personalização de cores (fundo, header, footer, texto, etc.)
- Header e footer com identificação da empresa

### 5. Inteligência Artificial (Ollama)
- Geração de apresentações com IA local
- Comandos em linguagem natural para definir estilo
- Análise automática de cores e layout
- Fallback automático caso a IA não esteja disponível
- Modelos suportados: llama3.2, deepseek, e outros do Ollama

### 6. Dashboard e Relatórios
- Visualização de dados em tabela
- Filtro por empresa
- **Filtros por período**: Todos os meses, Último trimestre, Último ano, Personalizado (por ano)
- **Gráficos interativos** com tooltips ao passar o mouse
- Gráfico de Receita vs Custos vs Despesas
- Gráfico de Lucro Operacional (com cores dinâmicas: verde para lucro, vermelho para prejuízo)
- Detalhamento completo dos cálculos de impostos
- Exportação para PowerPoint

## 📁 Estrutura do Projeto

```
AUDITAR_APP_DESKTOP/
├── app.py                          # Aplicação principal (PyQt6)
├── assets/
│   ├── calculadora_impostos.py     # Cálculo de impostos
│   ├── gerador_ia_inteligente.py   # Integração com Ollama
│   ├── slide_templates.py          # Templates de slides
│   ├── gerar_apresentacao_pdf_estilo.py  # Geração de PPTX
│   └── logo_auditar.png           # Logo da aplicação
├── data/
│   └── contabilidade.db            # Banco de dados SQLite
├── dist/                           # Executável compilado
└── README.md                       # Este arquivo
```

## 🚀 Como Usar

### Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install PyQt6 python-pptx matplotlib httpx
```

3. Execute a aplicação:
```bash
python app.py
```

### Uso Básico

1. **Cadastrar Empresa**
   - Vá na aba "Empresas"
   - Clique em "Adicionar Empresa"
   - Preencha os dados e selecione o regime tributário

2. **Lançar Dados Mensais**
   - Vá na aba "Dados Mensais"
   - Selecione a empresa
   - Preencha receita, custos e despesas
   - Clique em "Adicionar Mês"
   - O sistema calcula automaticamente os impostos

3. **Gerar Apresentação**
   - Vá na aba "Gerar Apresentação"
   - Selecione a empresa e o período
   - Escolha o template e cores
   - Opcional: Use IA para gerar com estilo personalizado
   - Clique em "Gerar Apresentação"

## 🎨 Personalização de Cores

O sistema permite personalizar as cores das apresentações:
- **Fundo**: Cor de fundo dos slides
- **Header**: Cor da barra superior
- **Footer**: Cor da barra inferior
- **Texto**: Cor do texto principal
- **Texto Secundário**: Cor do texto secundário
- **Destaque**: Cor para elementos de destaque

As cores podem ser definidas manualmente ou via IA usando comandos como:
- "Fundo azul marinho com dourado"
- "Fundo branco e texto preto"
- "Estilo corporativo verde e cinza"

## 🤖 Integração com IA (Ollama)

Para usar a funcionalidade de IA:

1. Instale o Ollama: https://ollama.ai
2. Baixe um modelo (ex: `ollama pull llama3.2`)
3. Inicie o Ollama: `ollama serve`
4. A aplicação detectará automaticamente o Ollama

Comandos de IA suportados:
- Descrição de cores em linguagem natural
- Escolha de template
- Análise de estilo

## 📊 Exemplos de Cálculo

### Simples Nacional
- Receita: R$ 2.000,00 (Comércio)
- Faixa 1: 4%
- DAS: R$ 80,00

### Lucro Presumido
- Receita: R$ 1.734,00 (Serviços)
- Base IRPJ: R$ 554,88 (32%)
- IRPJ: R$ 83,23
- CSLL: R$ 49,94
- PIS: R$ 11,27
- COFINS: R$ 52,02
- Total: R$ 196,46

### Lucro Real
- Receita: R$ 10.000,00
- Custos: R$ 6.000,00
- Despesas: R$ 2.000,00
- Lucro: R$ 2.000,00
- IRPJ: R$ 300,00
- CSLL: R$ 180,00
- Total: R$ 480,00

## 🔧 Compilação

Para compilar o aplicativo em executável:

1. Instale PyInstaller: `pip install pyinstaller`
2. Execute o script de compilação
3. O executável será gerado na pasta `dist/`

## 📝 Requisitos

- Python 3.8+
- PyQt6
- python-pptx
- matplotlib
- httpx
- mplcursors (opcional, para tooltips interativos nos gráficos)
- Ollama (opcional, para funcionalidades de IA)

## 🐛 Troubleshooting

### Erro: "Ollama não disponível"
- Verifique se o Ollama está rodando: `ollama serve`
- Teste em: http://localhost:11434/api/tags

### Cálculo incorreto de impostos
- Verifique o regime tributário da empresa
- Confirme o tipo de atividade (comércio/serviços)
- Para Lucro Presumido, o padrão é "serviços"

### Cores não aplicadas
- Verifique se o tema está configurado como "personalizado"
- Para IA, use comandos explícitos de cores

## 📄 Licença

Este projeto é propriedade da AUDITAR Contabilidade.

## 👥 Suporte

Para suporte, entre em contato com a equipe de desenvolvimento.
