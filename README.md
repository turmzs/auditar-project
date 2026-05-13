# AUDITAR - Sistema de Gestão Contábil

Sistema desktop completo para gestão contábil de empresas, com cálculo automático de impostos, geração de apresentações em PowerPoint e integração com Inteligência Artificial.

**Versão**: 6.79.0 (Estável)

## 🎯 Funcionalidades Principais

### 1. Gestão de Empresas
- Cadastro de empresas com CNPJ, responsável, cidade e estado
- Definição do regime tributário (Simples Nacional, Lucro Presumido ou Lucro Real)
- Gerenciamento de dados mensais por empresa

#### Funções da Aba "Empresas":
- **`salvar_empresa()`** - Valida e cadastra nova empresa no banco de dados
- **`atualizar_lista_empresas()`** - Atualiza a tabela de empresas e popula os comboboxes
- **`excluir_empresa(empresa_id)`** - Remove empresa e todos seus dados mensais associados

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

#### Funções da Aba "Dados Mensais":
- **`calcular_totais()`** - Calcula automaticamente totais de custos, despesas e lucro em tempo real
- **`adicionar_dados_mensais()`** - Valida e insere dados mensais no banco de dados
- **`limpar_campos_dados()`** - Limpa todos os campos após adicionar dados com sucesso
- **`atualizar_tabela_dados(empresa_id)`** - Atualiza a visualização da tabela com dados da empresa
- **`excluir_dado(dado_id)`** - Remove um registro de dados mensais

### 4. Geração de Apresentações PowerPoint
- Geração automática de slides com dados financeiros
- Gráficos de receita, custos, despesas e lucro
- Múltiplos templates disponíveis:
  - Corporativo Escuro
  - Minimalista Branco
  - Moderno Gradiente
- Personalização de cores (fundo, header, footer, texto, etc.)
- Header e footer com identificação da empresa

#### Funções da Aba "Relatórios":
- **`gerar_relatorio()`** - Coleta dados da empresa e inicia thread de geração
- **`atualizar_progresso(valor)`** - Callback que atualiza a barra de progresso
- **`relatorio_gerado(sucesso, resultado)`** - Callback final que exibe resultado ou erro
- **`gerar_demonstrativo_pdf_action()`** - Gera relatório contábil analítico tabular em PDF

### 5. Relatórios Analíticos (PDF)
- Geração de **Demonstrativo Analítico de Resultados** em formato PDF
- Layout profissional estilo "extrato contábil" com cabeçalho completo e linhas zebradas
- Colunas: Mês/Ano, Receita Bruta, Custos/Despesas, Impostos, Lucro Líquido e Margem %
- Totalizadores automáticos no final do documento
- Salvamento automático na Área de Trabalho do usuário

### 6. Inteligência Artificial (Ollama)
- Geração de apresentações com IA local via **Chat API**
- **Extração Robusta**: Sistema de limpeza de JSON capaz de corrigir falhas de formatação de modelos pequenos
- Comandos em linguagem natural para definir estilo (ex: "Fundo escuro e detalhes em laranja")
- **Camada de Segurança**: Detecção automática de cores por palavras-chave caso a IA falhe
- Modelo Recomendado: **TinyLlama** (ultra-leve e rápido, ideal para máquinas com 8GB RAM ou menos)
- Modelo Avançado: **Llama 3.2** (para máquinas com GPU/VRAM dedicada)
- Consultoria estratégica baseada no histórico financeiro da empresa

### 6. Dashboard e Relatórios
- Visualização de dados em tabela
- Filtro por empresa
- **Filtros por período**: Todos os meses, Último trimestre, Último ano, Personalizado (por ano)
- **Gráficos interativos** com tooltips ao passar o mouse
- Gráfico de Receita vs Custos vs Despesas
- Gráfico de Lucro Operacional (com cores dinâmicas: verde para lucro, vermelho para prejuízo)
- Detalhamento completo dos cálculos de impostos
- Exportação para PowerPoint
- Relatório para excel.

## 🛠️ Funções Utilitárias

### `get_resource_path(relative_path)`
Função global que retorna o caminho absoluto para recursos (imagens, arquivos).
- Funciona tanto em desenvolvimento quanto no executável PyInstaller
- Usada para carregar a logo e outros assets
- Detecta automaticamente se está rodando do `.exe` ou em desenvolvimento

**Uso:**
```python
logo_path = get_resource_path(os.path.join("assets", "logo_auditar.png"))
```

## 📊 Fluxo de Dados

```
1. Usuário cadastra Empresa
   ↓
2. DatabaseManager salva em empresas table
   ↓
3. Usuário lança Dados Mensais
   ↓
4. calcular_totais() atualiza valores em tempo real
   ↓
5. adicionar_dados_mensais() salva em dados_mensais table
   ↓
6. Usuário gera Relatório
   ↓
7. gerar_relatorio() prepara dados
   ↓
8. Usuário gera arquivo excel.
   ↓
9. GeradorPPTXThread inicia em background
   ↓
10. Geração PPTX ou IA inteligente
   ↓
11. Arquivo salvo, mensagem de sucesso
```

## 📁 Estrutura do Projeto

```
AUDITAR_APP_DESKTOP/
├── app.py                          # Aplicação principal (PyQt6)
├── assets/
│   ├── __init__.py
│   ├── calculadora_impostos.py     # Cálculo de impostos (Simples, Lucro Presumido, Lucro Real)
│   ├── calculo_profissional.py     # Cálculos profissionais adicionais
│   ├── gerador_ia_inteligente.py   # Integração com Ollama para geração com IA
│   ├── slide_templates.py          # Templates e temas de cores para slides
│   ├── gerar_apresentacao_pdf_estilo.py  # Geração de apresentações PPTX
│   └── logo_auditar.png           # Logo da aplicação
├── data/
│   └── contabilidade.db            # Banco de dados SQLite
├── build/                          # Arquivos de build (PyInstaller)
├── INSTALLER/                      # Scripts e configurações do instalador
├── dist/                           # Executável compilado
├── auditar.spec                    # Configuração do PyInstaller
├── BUILD_EXE.bat                   # Script para compilar em executável
├── LICENSE.txt
└── README.md                       # Este arquivo
```

## 🏗️ Arquitetura e Classes Principais

### 1. **DatabaseManager** (app.py)
Gerencia conexões e operações com o banco de dados SQLite.

**Métodos principais:**
- `init_database()` - Inicializa tabelas de empresas e dados_mensais
- `execute(query, params)` - Executa queries INSERT, UPDATE, DELETE
- `fetchall(query, params)` - Recupera múltiplos registros
- `fetchone(query, params)` - Recupera um único registro

**Banco de Dados:**
- Tabela `empresas`: id, nome, cnpj, responsavel, cidade, estado, data_cadastro
- Tabela `dados_mensais`: mes, ano, receita_bruta, custos detalhados, despesas detalhadas, impostos, lucro_operacional

### 2. **GeradorPPTXThread** (app.py)
Thread para geração de apresentações de forma assíncrona, não bloqueando a interface.

**Sinais (pyqtSignal):**
- `progress(int)` - Emite progresso de 0-100%
- `finished(bool, str)` - Emite sucesso/erro e caminho/mensagem

**Funcionalidades:**
- Suporta modo IA (com Ollama) ou modo padrão com temas
- Personalização de cores via `tema_cores`
- Processamento em background com barra de progresso

### 3. **MainWindow** (app.py)
Classe principal da interface PyQt6 com 3 abas principais.

**Métodos principais:**
- `criar_aba_empresas()` - Inicializa aba de cadastro de empresas
- `criar_aba_dados()` - Inicializa aba de lançamento de dados mensais
- `criar_aba_relatorios()` - Inicializa aba de geração de relatórios
- Herda métodos de gerenciamento de dados das três abas

### 4. **GeradorIAInteligente** (assets/gerador_ia_inteligente.py)
Classe para geração inteligente de apresentações usando Ollama.

**Métodos principais:**
- `_check_ollama()` - Verifica se Ollama está disponível
- `gerar_apresentacao_inteligente()` - Gera apresentação com IA
- Suporte a comandos em linguagem natural

### 5. **CalculadoraImpostos** (assets/calculadora_impostos.py)
Calcula impostos para diferentes regimes tributários.

**Métodos estáticos:**
- `calcular_simples_nacional()` - Calcula Simples Nacional (Anexo I e III)
- `calcular_lucro_presumido_mensal()` - Calcula Lucro Presumido mensal
- `calcular_lucro_presumido_trimestral()` - Calcula Lucro Presumido trimestral
- `calcular_lucro_real()` - Calcula Lucro Real

Implementa tabelas oficiais 2024 com alíquotas corretas.

## 🎨 Temas de Cores Disponíveis

O arquivo `assets/slide_templates.py` define os temas disponíveis:

1. **Corporativo Escuro** - Tema profissional com fundo escuro
2. **Minimalista Branco** - Tema limpo e moderno
3. **Moderno Gradiente** - Tema com gradientes suaves
4. Personalizado via IA - Cores definidas por comando de linguagem natural

Cada tema inclui:
- Cor de fundo
- Cor de header/footer
- Cores de texto principal e secundário
- Cores de destaque para gráficos



---

## 🚀 Como Usar
Para não precisar instalar todas as dependências uma por uma, pode se usar o INSTALADOR específico que está no pacote disponibilizado.

### Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install PyQt6 python-pptx matplotlib httpx fpdf2
```

3. Execute a aplicação:
```bash
python app.py
```

### Uso Básico

1. **Cadastrar Empresa**
   - Vá na aba "Empresas"
   - Preencha os dados: Nome, CNPJ, Responsável, Cidade, Estado
   - Clique em "Salvar Empresa"

2. **Lançar Dados Mensais**
   - Vá na aba "Dados Mensais"
   - Selecione a empresa no combo
   - Preencha o mês e ano
   - Insira receita bruta
   - Insira custos detalhados (salários, aluguel, outros custos)
   - Insira despesas detalhadas (água/luz/telefone, material, outras)
   - O sistema calcula automaticamente os totais e lucro
   - Clique em "Adicionar Mês"

3. **Gerar Apresentação**
   - Vá na aba "Relatórios"
   - Selecione a empresa
   - Escolha entre:
     - **Apresentação PPTX (Padrão)**: Selecione um tema de cores
     - **Apresentação com IA**: Digite um comando descritivo (ex: "Elegante com fundo azul")
   - Clique em "GERAR APRESENTAÇÃO PPTX"
   - Aguarde a barra de progresso
   - A apresentação será salva automaticamente

---

## 📋 Referência Rápida de Funções

| Função | Localização | Descrição |
|--------|------------|-----------|
| `get_resource_path()` | app.py | Retorna caminho absoluto para recursos |
| `salvar_empresa()` | MainWindow | Cadastra nova empresa |
| `atualizar_lista_empresas()` | MainWindow | Atualiza tabela de empresas |
| `excluir_empresa()` | MainWindow | Remove empresa e dados associados |
| `adicionar_dados_mensais()` | MainWindow | Insere dados mensais no banco |
| `calcular_totais()` | MainWindow | Calcula custos, despesas e lucro em tempo real |
| `limpar_campos_dados()` | MainWindow | Limpa campos após adicionar dados |
| `atualizar_tabela_dados()` | MainWindow | Atualiza visualização de dados mensais |
| `excluir_dado()` | MainWindow | Remove um registro de dados mensais |
| `gerar_relatorio()` | MainWindow | Inicia geração de apresentação |
| `atualizar_progresso()` | MainWindow | Atualiza barra de progresso |
| `relatorio_gerado()` | MainWindow | Callback de conclusão da geração |
| `execute()` | DatabaseManager | Executa INSERT/UPDATE/DELETE |
| `fetchall()` | DatabaseManager | Recupera múltiplos registros |
| `fetchone()` | DatabaseManager | Recupera um registro |
| `calcular_simples_nacional()` | CalculadoraImpostos | Calcula Simples Nacional |
| `calcular_lucro_presumido_mensal()` | CalculadoraImpostos | Calcula Lucro Presumido mensal |
| `calcular_lucro_real()` | CalculadoraImpostos | Calcula Lucro Real |

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

A aplicação utiliza o **Ollama** para processamento de linguagem natural local, garantindo privacidade total dos dados.

1. **Instalação**: Baixe o Ollama em [ollama.ai](https://ollama.ai)
2. **Modelo**: O sistema utiliza o **TinyLlama** (~600MB), ideal para rodar em qualquer máquina com rapidez e baixo consumo de RAM.
3. **Funcionalidades**:
   - **Estilo de Slides**: Comandos como "Fundo azul marinho com dourado" são interpretados para criar temas personalizados.
   - **Consultoria Financeira**: O botão "Consultoria IA" no Dashboard gera um diagnóstico estratégico baseado nos últimos 6 meses de dados da empresa.

## 📊 Exemplos de Cálculo (Validados)

O sistema segue rigorosamente a legislação vigente para os cálculos automáticos:

### 1. Simples Nacional (com Fator R)
Exemplo para empresa de serviços (Anexo III/V):
- **Receita Mensal**: R$ 20.000,00
- **Folha de Pagamento**: R$ 6.000,00 (Fator R = 30%)
- **Resultado**: Enquadramento no **Anexo III** (6% de alíquota inicial)
- **DAS**: R$ 1.200,00
- *Nota: Se a folha fosse inferior a 28% da receita, o sistema aplicaria o Anexo V (15.5%).*

### 2. Lucro Presumido (Mensal)
Exemplo para prestadora de serviços (32% de presunção):
- **Receita Mensal**: R$ 50.000,00
- **IRPJ (15% sobre 32%)**: R$ 2.400,00
- **CSLL (9% sobre 32%)**: R$ 1.440,00
- **PIS/COFINS (3.65%)**: R$ 1.825,00
- **Total Federal**: R$ 5.665,00

### 3. Lucro Real (com Adicional de IRPJ)
Exemplo de lucro elevado no mês:
- **Lucro Operacional**: R$ 100.000,00
- **IRPJ Normal (15%)**: R$ 15.000,00
- **Adicional IRPJ (10% sobre o excedente de R$ 20k)**: R$ 8.000,00
- **CSLL (9%)**: R$ 9.000,00
- **Total de Imposto sobre o Lucro**: R$ 32.000,00

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
- httpx (para comunicação com Ollama)
- fpdf2 (para relatórios analíticos em PDF)
- mplcursors (opcional, para tooltips interativos nos gráficos)
- Ollama (opcional, para funcionalidades de IA)

## ✨ O Que Há de Novo (v6.79.0)

### Novas Funções Adicionadas (v6.79.0)
- **`gerar_relatorio_pdf()`** - Gerador técnico de PDF analítico com tabelas zebradas e cabeçalho formal
- **`extrair_json_robusto()`** - Motor de parsing para tratar respostas imperfeitas de modelos locais (Ollama)
- **Seleção Dinâmica de Template** - Alternância automática entre 'Claro' e 'Escuro' conforme o comando do usuário
- **Dicionário de Cores Universal** - Suporte para dezenas de cores em português (Flamengo, Verde, Roxo, etc.)
- **`calcular_totais()`** - Cálculo automático em tempo real de custos, despesas e lucro
- **`limpar_campos_dados()`** - Limpeza automatizada de campos após lançamento de dados
- **`atualizar_tabela_dados()`** - Atualização dinâmica da tabela de dados mensais
- **`excluir_dado()`** - Exclusão de registros de dados mensais
- **`atualizar_progresso()`** - Callback para barra de progresso em geração assíncrona
- **`relatorio_gerado()`** - Callback para tratamento de sucesso/erro na geração

### Melhorias Implementadas
- Interface melhorada com 3 abas bem definidas (Empresas, Dados Mensais, Relatórios)
- Cálculos de custos e despesas detalhados com subtotais automáticos
- Temas de cores predefinidos (Corporativo, Minimalista, Moderno)
- Integração com IA Ollama para geração inteligente de apresentações
- Barra de progresso para geração assíncrona de relatórios
- Múltiplos regimes tributários com tabelas 2024 atualizadas

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
