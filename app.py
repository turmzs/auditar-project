"""
AUDITAR CONTABILIDADE - Versão Padrão
"""

import sys
import os
import sqlite3
import json
import asyncio
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QTabWidget, QFrame, QFileDialog, QMessageBox, QProgressBar,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QTextEdit,
    QGroupBox, QRadioButton, QButtonGroup, QGridLayout, QScrollArea,
    QColorDialog, QPushButton,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from pptx.dml.color import RGBColor

# Importar calculadora de impostos
sys.path.append(os.path.join(os.path.dirname(__file__), 'assets'))
from calculadora_impostos import CalculadoraImpostos
from calculo_profissional import CalculoProfissional, salvar_resultado_calculo

# Adicionar paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"))

# ============================================================
# FUNÇÃO PARA CARREGAR RECURSOS (imagens, arquivos, etc)
# Funciona tanto em desenvolvimento quanto no executável PyInstaller
# ============================================================
def get_resource_path(relative_path):
    """Retorna caminho absoluto para recursos, funcionando no .exe ou desenvolvimento"""
    if hasattr(sys, '_MEIPASS'):
        # Está rodando do executável PyInstaller
        base_path = sys._MEIPASS
    else:
        # Está rodando em desenvolvimento
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# Caminho da logo (já incluso automaticamente)
LOGO_PATH = get_resource_path(os.path.join("assets", "logo_auditar.png"))
print(f"Logo carregada de: {LOGO_PATH}")

from assets.gerar_apresentacao_pdf_estilo import gerar_apresentacao_pptx_pdf
from assets.slide_templates import OPCOES_CORES
from assets.gerador_pdf import gerar_relatorio_pdf

try:
    from assets.gerador_ia_inteligente import GeradorIAInteligente, gerar_apresentacao_ia
    IA_INTELIGENTE_DISPONIVEL = True
except ImportError:
    IA_INTELIGENTE_DISPONIVEL = False


class DatabaseManager:
    def __init__(self, db_path="data/contabilidade.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT,
                responsavel TEXT,
                cidade TEXT,
                estado TEXT,
                regime_tributario TEXT DEFAULT 'simples',
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Verificar e adicionar colunas se não existirem (migração)
        cursor.execute("PRAGMA table_info(dados_mensais)")
        colunas_dados = [col[1] for col in cursor.fetchall()]
        if 'creditos_pis_cofins' not in colunas_dados:
            cursor.execute("ALTER TABLE dados_mensais ADD COLUMN creditos_pis_cofins REAL DEFAULT 0")
            
        cursor.execute("PRAGMA table_info(empresas)")
        colunas_emp = [col[1] for col in cursor.fetchall()]
        if 'regime_tributario' not in colunas_emp:
            cursor.execute("ALTER TABLE empresas ADD COLUMN regime_tributario TEXT DEFAULT 'simples'")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dados_mensais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                mes INTEGER,
                ano INTEGER,
                receita_bruta REAL DEFAULT 0,
                -- CUSTOS DETALHADOS
                custo_salarios REAL DEFAULT 0,
                custo_aluguel REAL DEFAULT 0,
                custo_outros REAL DEFAULT 0,
                -- DESPESAS DETALHADAS
                despesa_agua_luz_tel REAL DEFAULT 0,
                despesa_material REAL DEFAULT 0,
                despesa_outros REAL DEFAULT 0,
                -- TOTAIS
                custos REAL DEFAULT 0,
                despesas REAL DEFAULT 0,
                impostos REAL DEFAULT 0,
                lucro_operacional REAL DEFAULT 0,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        ''')

        # Tabela de lançamentos fiscais (entradas/saídas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lancamentos_fiscais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                mes INTEGER,
                ano INTEGER,
                tipo TEXT,  -- 'entrada' (compra) ou 'saida' (venda)
                descricao TEXT,
                valor REAL DEFAULT 0,
                valor_icms REAL DEFAULT 0,  -- ICMS incluso no valor
                valor_pis REAL DEFAULT 0,   -- PIS incluso
                valor_cofins REAL DEFAULT 0, -- COFINS incluso
                is_credito INTEGER DEFAULT 0,  -- 1 = gera crédito, 0 = não
                data_lancamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        ''')

        # Tabela de créditos de impostos acumulados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS creditos_impostos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                ano INTEGER,
                mes INTEGER,
                tipo_imposto TEXT,  -- 'PIS', 'COFINS', 'ICMS', 'IRPJ', 'CSLL'
                valor_credito REAL DEFAULT 0,
                valor_utilizado REAL DEFAULT 0,
                saldo REAL DEFAULT 0,
                origem TEXT,  -- 'prejuizo', 'compra', 'ajuste', etc.
                descricao TEXT,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        ''')

        # Tabela de prejuízos fiscais para compensação
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prejuizos_fiscais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                ano_origem INTEGER,
                valor_prejuizo REAL DEFAULT 0,
                valor_compensado REAL DEFAULT 0,
                saldo_restante REAL DEFAULT 0,
                limite_30_percent INTEGER DEFAULT 1,  -- se aplica limite de 30%
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        ''')

        # Tabela de memória de cálculo (histórico detalhado)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memoria_calculo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                mes INTEGER,
                ano INTEGER,
                regime TEXT,
                tipo_imposto TEXT,
                base_calculo REAL DEFAULT 0,
                aliquota REAL DEFAULT 0,
                valor_debito REAL DEFAULT 0,
                valor_credito REAL DEFAULT 0,
                valor_total REAL DEFAULT 0,
                detalhamento TEXT,  -- JSON com detalhes
                data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        ''')
        conn.commit()
        conn.close()

    def execute(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetchall(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def fetchone(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result


class GeradorPPTXThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, dados_mensais, nome_empresa, responsavel, bundle_dir, use_ia=False, comando_ia="", tema_cores=None, cores_personalizadas=None):
        super().__init__()
        self.dados_mensais = dados_mensais
        self.nome_empresa = nome_empresa
        self.responsavel = responsavel
        self.bundle_dir = bundle_dir
        self.use_ia = use_ia
        self.comando_ia = comando_ia
        self.tema_cores = tema_cores
        self.cores_personalizadas = cores_personalizadas

    def run(self):
        try:
            self.progress.emit(20)
            if self.use_ia and IA_INTELIGENTE_DISPONIVEL:
                # Preparar cores personalizadas se tema for personalizado
                cores_ia = None
                if self.tema_cores == "personalizado":
                    cores_ia = self.cores_personalizadas
                    print(f"🎨 Usando cores personalizadas com IA")

                filepath = asyncio.run(gerar_apresentacao_ia(
                    dados_mensais=self.dados_mensais,
                    nome_empresa=self.nome_empresa,
                    responsavel=self.responsavel,
                    bundle_dir=self.bundle_dir,
                    comando_estilo=self.comando_ia,
                    cores_personalizadas=cores_ia
                ))
            else:
                # Usar tema de cores pré-definido ou personalizadas
                from assets.slide_templates import OPCOES_CORES
                cores_personalizadas = None

                if self.tema_cores == "personalizado":
                    # Usar cores personalizadas selecionadas pelo usuário
                    cores_personalizadas = self.cores_personalizadas
                    print(f"🎨 Usando cores personalizadas")
                elif self.tema_cores and self.tema_cores in OPCOES_CORES:
                    # Usar tema pré-definido
                    _, cores_personalizadas = OPCOES_CORES[self.tema_cores]
                    print(f"🎨 Usando tema: {self.tema_cores}")

                filepath = gerar_apresentacao_pptx_pdf(
                    self.dados_mensais, self.nome_empresa, self.responsavel, self.bundle_dir, cores_personalizadas
                )
            self.progress.emit(100)
            self.finished.emit(True, filepath)
        except Exception as e:
            self.finished.emit(False, str(e))


class AnalisadorIAFinanceiraThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, dados_mensais, nome_empresa, comando_personalizado=""):
        super().__init__()
        self.dados_mensais = dados_mensais
        self.nome_empresa = nome_empresa
        self.comando_personalizado = comando_personalizado

    def run(self):
        try:
            ia = GeradorIAInteligente()
            # Rodar async dentro da thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            diagnostico = loop.run_until_complete(ia.analisar_financas(self.dados_mensais, self.nome_empresa, self.comando_personalizado))
            self.finished.emit(diagnostico)
        except Exception as e:
            self.finished.emit(f"Erro na análise: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auditar Planejamento Tributário - v6.79.0")
        self.setGeometry(100, 100, 900, 700)

        self.db = DatabaseManager()

        # Inicializar cores padrão (para evitar erro ao gerar relatório sem visitar aba de relatórios)
        from pptx.dml.color import RGBColor
        self.cor_fundo = RGBColor(255, 255, 255)  # Branco padrão
        self.cor_header = RGBColor(0, 0, 128)  # Azul escuro padrão
        self.cor_footer = RGBColor(0, 0, 128)  # Azul escuro padrão
        self.cor_texto = RGBColor(0, 0, 0)  # Preto padrão
        self.cor_destaque = RGBColor(212, 175, 55)  # Dourado padrão
        
        # Widget central com abas
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        titulo = QLabel("Auditar Planejamento Tributário")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Aplicar estilo global Cinza Clássico / Limpo
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f0f0f0;
                color: #000000;
                font-family: 'Segoe UI', Arial;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #b0b0b0;
                margin-top: 1.1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit, QTableWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                color: #000000;
            }
            QPushButton {
                background-color: #e1e1e1;
                border: 1px solid #adadad;
                padding: 5px 15px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #e5f1fb;
                border: 1px solid #0078d7;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #cccccc;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                border: 1px solid #cccccc;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: none;
            }
            QRadioButton, QCheckBox {
                spacing: 8px;
                color: #000000;
                font-size: 13px;
            }
            QRadioButton::indicator, QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #555555;
                background-color: #ffffff;
            }
            QRadioButton::indicator {
                border-radius: 10px;
            }
            QCheckBox::indicator {
                border-radius: 3px;
            }
            QRadioButton::indicator:checked {
                background-color: #0078d7;
                border: 2px solid #005a9e;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d7;
                border: 2px solid #005a9e;
            }
        """)

        # Abas
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Criar paginas
        self.criar_aba_empresas()
        self.criar_aba_dados()
        self.criar_aba_dashboard()
        self.criar_aba_relatorios()
        
        self.atualizar_lista_empresas()

    def criar_aba_empresas(self):
        page = QWidget()
        self.tabs.addTab(page, "Empresas")
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        
        # Grupo: Nova Empresa
        grupo_novo = QGroupBox("Cadastrar Nova Empresa")
        layout.addWidget(grupo_novo)
        
        form = QFormLayout(grupo_novo)
        
        self.txt_nome = QLineEdit()
        self.txt_cnpj = QLineEdit()
        self.txt_responsavel = QLineEdit()
        self.txt_cidade = QLineEdit()
        self.txt_estado = QLineEdit()
        self.combo_regime = QComboBox()
        self.combo_regime.addItem("Simples Nacional", "simples")
        self.combo_regime.addItem("Lucro Presumido", "presumido")
        self.combo_regime.addItem("Lucro Real", "real")

        form.addRow("Nome:", self.txt_nome)
        form.addRow("CNPJ:", self.txt_cnpj)
        form.addRow("Responsavel:", self.txt_responsavel)
        form.addRow("Cidade:", self.txt_cidade)
        form.addRow("Estado:", self.txt_estado)
        form.addRow("Regime Tributário:", self.combo_regime)
        
        btn_salvar = QPushButton("Salvar Empresa")
        btn_salvar.clicked.connect(self.salvar_empresa)
        form.addRow(btn_salvar)
        
        # Grupo: Lista de Empresas
        grupo_lista = QGroupBox("Empresas Cadastradas")
        layout.addWidget(grupo_lista, stretch=1)
        
        lista_layout = QVBoxLayout(grupo_lista)
        
        self.tabela_empresas = QTableWidget()
        self.tabela_empresas.setColumnCount(5)
        self.tabela_empresas.setHorizontalHeaderLabels(["ID", "Nome", "CNPJ", "Responsavel", "Acao"])
        lista_layout.addWidget(self.tabela_empresas)

    def criar_aba_dados(self):
        page = QWidget()
        self.tabs.addTab(page, "Dados Mensais")
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        # Criar área com scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Widget interno para o scroll
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Selecionar empresa
        selecao_layout = QHBoxLayout()
        selecao_layout.addWidget(QLabel("Empresa:"))
        self.combo_empresa_dados = QComboBox()
        self.combo_empresa_dados.setMinimumWidth(300)
        selecao_layout.addWidget(self.combo_empresa_dados)
        selecao_layout.addStretch()
        scroll_layout.addLayout(selecao_layout)

        # Grupo: Novo Mes
        grupo_novo = QGroupBox("Adicionar Mes")
        scroll_layout.addWidget(grupo_novo)
        
        form = QFormLayout(grupo_novo)
        
        self.spin_mes = QSpinBox()
        self.spin_mes.setRange(1, 12)
        self.spin_ano = QSpinBox()
        self.spin_ano.setRange(2020, 2030)
        self.spin_ano.setValue(datetime.now().year)
        
        # === RECEITA ===
        self.txt_receita = QLineEdit("0")
        
        # === CUSTOS DETALHADOS ===
        self.txt_custo_salarios = QLineEdit("0")
        self.txt_custo_aluguel = QLineEdit("0")
        self.txt_custo_outros = QLineEdit("0")
        self.txt_custos_total = QLineEdit("0")
        self.txt_custos_total.setReadOnly(True)
        
        # === DESPESAS DETALHADAS ===
        self.txt_despesa_agua_luz_tel = QLineEdit("0")
        self.txt_despesa_material = QLineEdit("0")
        self.txt_despesa_outros = QLineEdit("0")
        self.txt_despesas_total = QLineEdit("0")
        self.txt_despesas_total.setReadOnly(True)
        
        # === IMPOSTOS E LUCRO ===
        self.txt_creditos = QLineEdit("0")
        self.txt_impostos = QLineEdit("0")
        self.txt_impostos.setReadOnly(True)
        self.txt_lucro = QLineEdit("0")
        self.txt_lucro.setReadOnly(True)

        # Botão para calcular impostos automaticamente
        self.btn_calcular_impostos = QPushButton(" Calcular Impostos (Auto)")
        self.btn_calcular_impostos.clicked.connect(self.calcular_impostos_automatico)
        
        # Conectar sinais para calcular automaticamente
        campos_calculo = [
            self.txt_receita, self.txt_custo_salarios, self.txt_custo_aluguel, 
            self.txt_custo_outros, self.txt_despesa_agua_luz_tel, 
            self.txt_despesa_material, self.txt_despesa_outros, self.txt_creditos
        ]
        
        for campo in campos_calculo:
            campo.textChanged.connect(self.calcular_totais)
        
        # === LAYOUT DO FORMULÁRIO ===
        form.addRow("Mes:", self.spin_mes)
        form.addRow("Ano:", self.spin_ano)
        form.addRow("", QLabel(""))  # Espaço
        
        # Receita
        form.addRow(QLabel(" RECEITA:"))
        form.addRow("  Receita Bruta:", self.txt_receita)
        form.addRow("", QLabel(""))  # Espaço
        
        # Custos Detalhados
        form.addRow(QLabel(" CUSTOS (Detalhados):"))
        form.addRow("  Salarios:", self.txt_custo_salarios)
        form.addRow("  Aluguel:", self.txt_custo_aluguel)
        form.addRow("  Outros Custos:", self.txt_custo_outros)
        form.addRow("  TOTAL Custos:", self.txt_custos_total)
        form.addRow("", QLabel(""))  # Espaço
        
        # Despesas Detalhadas
        form.addRow(QLabel(" DESPESAS (Detalhadas):"))
        form.addRow("  Agua/Luz/Telefone:", self.txt_despesa_agua_luz_tel)
        form.addRow("  Material/Escritorio:", self.txt_despesa_material)
        form.addRow("  Outras Despesas:", self.txt_despesa_outros)
        form.addRow("  TOTAL Despesas:", self.txt_despesas_total)
        form.addRow("", QLabel(""))  # Espaço
        
        # Impostos e Lucro
        form.addRow(QLabel(" TRIBUTOS E RESULTADO:"))
        form.addRow("  Créditos PIS/COFINS (Lucro Real):", self.txt_creditos)
        form.addRow("  Impostos Estimados:", self.txt_impostos)
        form.addRow("  LUCRO OPERACIONAL:", self.txt_lucro)
        form.addRow("", self.btn_calcular_impostos)
        
        btn_adicionar = QPushButton("Adicionar Mes")
        btn_adicionar.clicked.connect(self.adicionar_dados_mensais)
        form.addRow(btn_adicionar)

        # Grupo: Dados
        grupo_dados = QGroupBox("Dados Mensais Cadastrados")
        scroll_layout.addWidget(grupo_dados)

        dados_layout = QVBoxLayout(grupo_dados)
        self.tabela_dados = QTableWidget()
        self.tabela_dados.setColumnCount(7)
        self.tabela_dados.setHorizontalHeaderLabels(["Mes/Ano", "Receita", "Custos*", "Despesas*", "Impostos", "Lucro", "Acao"])
        self.tabela_dados.setToolTip("* Custos e Despesas com detalhamento completo (salários, aluguel, água/luz, etc.)")
        dados_layout.addWidget(self.tabela_dados)

        # Grupo: Cálculo Trimestral (apenas para Lucro Presumido)
        self.grupo_trimestral = QGroupBox("📊 Cálculo Trimestral - Lucro Presumido")
        self.grupo_trimestral.setVisible(False)  # Inicialmente oculto
        scroll_layout.addWidget(self.grupo_trimestral)

        trimestral_layout = QVBoxLayout(self.grupo_trimestral)

        # Seleção de trimestre e ano
        selecao_trimestral_layout = QHBoxLayout()
        selecao_trimestral_layout.addWidget(QLabel("Trimestre:"))
        self.combo_trimestre = QComboBox()
        self.combo_trimestre.addItem("1º Trimestre (Jan/Fev/Mar)", 1)
        self.combo_trimestre.addItem("2º Trimestre (Abr/Mai/Jun)", 2)
        self.combo_trimestre.addItem("3º Trimestre (Jul/Ago/Set)", 3)
        self.combo_trimestre.addItem("4º Trimestre (Out/Nov/Dez)", 4)
        selecao_trimestral_layout.addWidget(self.combo_trimestre)

        selecao_trimestral_layout.addWidget(QLabel("  Ano:"))
        self.combo_ano_trimestral = QComboBox()
        self.combo_ano_trimestral.addItem("2024", 2024)
        self.combo_ano_trimestral.addItem("2025", 2025)
        self.combo_ano_trimestral.addItem("2026", 2026)
        selecao_trimestral_layout.addWidget(self.combo_ano_trimestral)

        selecao_trimestral_layout.addStretch()
        trimestral_layout.addLayout(selecao_trimestral_layout)

        # Tipo de atividade
        atividade_trimestral_layout = QHBoxLayout()
        atividade_trimestral_layout.addWidget(QLabel("Tipo de Atividade:"))
        self.combo_atividade_trimestral = QComboBox()
        self.combo_atividade_trimestral.addItem("Serviços (32% presunção)", "servicos")
        self.combo_atividade_trimestral.addItem("Comércio (8% IRPJ, 12% CSLL)", "comercio")
        self.combo_atividade_trimestral.addItem("Indústria (8% IRPJ, 12% CSLL)", "industria")
        self.combo_atividade_trimestral.addItem("Transporte (16% presunção)", "transporte")
        atividade_trimestral_layout.addWidget(self.combo_atividade_trimestral)
        atividade_trimestral_layout.addStretch()
        trimestral_layout.addLayout(atividade_trimestral_layout)

        # Campos de receita mensal
        grupo_receitas_trimestral = QGroupBox("Receita Bruta Mensal (R$)")
        trimestral_layout.addWidget(grupo_receitas_trimestral)
        receitas_trimestral_layout = QGridLayout(grupo_receitas_trimestral)

        receitas_trimestral_layout.addWidget(QLabel("Mês 1:"), 0, 0)
        self.txt_receita_mes1 = QLineEdit()
        self.txt_receita_mes1.setPlaceholderText("0,00")
        receitas_trimestral_layout.addWidget(self.txt_receita_mes1, 0, 1)

        receitas_trimestral_layout.addWidget(QLabel("Mês 2:"), 1, 0)
        self.txt_receita_mes2 = QLineEdit()
        self.txt_receita_mes2.setPlaceholderText("0,00")
        receitas_trimestral_layout.addWidget(self.txt_receita_mes2, 1, 1)

        receitas_trimestral_layout.addWidget(QLabel("Mês 3:"), 2, 0)
        self.txt_receita_mes3 = QLineEdit()
        self.txt_receita_mes3.setPlaceholderText("0,00")
        receitas_trimestral_layout.addWidget(self.txt_receita_mes3, 2, 1)

        # Botão calcular
        btn_calcular_trimestral = QPushButton("Calcular Impostos Trimestrais")
        btn_calcular_trimestral.clicked.connect(self.calcular_impostos_trimestral)
        trimestral_layout.addWidget(btn_calcular_trimestral)

        # Área de resultados
        self.resultados_trimestral = QGroupBox("Resultados do Trimestre")
        self.resultados_trimestral.setVisible(False)
        trimestral_layout.addWidget(self.resultados_trimestral)

        resultados_trimestral_layout = QVBoxLayout(self.resultados_trimestral)
        self.lbl_resultados_trimestral = QLabel()
        self.lbl_resultados_trimestral.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        resultados_trimestral_layout.addWidget(self.lbl_resultados_trimestral)

        # === GRUPO LUCRO REAL TRIMESTRAL ===
        self.grupo_trimestral_real = QGroupBox("📊 Cálculo Trimestral - Lucro Real")
        self.grupo_trimestral_real.setVisible(False)
        scroll_layout.addWidget(self.grupo_trimestral_real)
        
        layout_real = QVBoxLayout(self.grupo_trimestral_real)
        grid_real = QGridLayout()
        layout_real.addLayout(grid_real)
        
        # Cabeçalhos
        grid_real.addWidget(QLabel("Mês"), 0, 0)
        grid_real.addWidget(QLabel("Receita (R$)"), 0, 1)
        grid_real.addWidget(QLabel("Custos (R$)"), 0, 2)
        grid_real.addWidget(QLabel("Despesas (R$)"), 0, 3)
        grid_real.addWidget(QLabel("Créditos* (R$)"), 0, 4)
        
        self.real_inputs = []
        for i in range(1, 4):
            grid_real.addWidget(QLabel(f"Mês {i}:"), i, 0)
            rec = QLineEdit("0"); grid_real.addWidget(rec, i, 1)
            cus = QLineEdit("0"); grid_real.addWidget(cus, i, 2)
            des = QLineEdit("0"); grid_real.addWidget(des, i, 3)
            cre = QLineEdit("0"); grid_real.addWidget(cre, i, 4)
            self.real_inputs.append({'rec': rec, 'cus': cus, 'des': des, 'cre': cre})
            
        btn_calc_real = QPushButton("Calcular Fechamento Trimestral (Real)")
        btn_calc_real.clicked.connect(self.calcular_lucro_real_trimestral_action)
        layout_real.addWidget(btn_calc_real)
        
        self.lbl_resultados_real = QLabel()
        self.lbl_resultados_real.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        layout_real.addWidget(self.lbl_resultados_real)
        layout_real.addWidget(QLabel("* Créditos de PIS/COFINS (compras, energia, aluguel PJ, etc.)"))

        # Conectar mudança de empresa para verificar regime
        self.combo_empresa_dados.currentIndexChanged.connect(self.verificar_regime_para_trimestral)

    def criar_aba_dashboard(self):
        page = QWidget()
        self.tabs.addTab(page, "Dashboard")
        layout = QVBoxLayout(page)
        layout.setSpacing(15)

        # Selecionar empresa e período
        selecao_layout = QHBoxLayout()
        selecao_layout.addWidget(QLabel("Empresa:"))
        self.combo_empresa_dash = QComboBox()
        self.combo_empresa_dash.setMinimumWidth(250)
        self.combo_empresa_dash.currentIndexChanged.connect(self.atualizar_dashboard)
        selecao_layout.addWidget(self.combo_empresa_dash)

        selecao_layout.addWidget(QLabel("  Período:"))
        self.combo_periodo_dash = QComboBox()
        self.combo_periodo_dash.setMinimumWidth(150)
        self.combo_periodo_dash.addItem("Todos os meses", "todos")
        self.combo_periodo_dash.addItem("Último trimestre", "trimestral")
        self.combo_periodo_dash.addItem("Último ano", "anual")
        self.combo_periodo_dash.addItem("Personalizado", "personalizado")
        self.combo_periodo_dash.currentIndexChanged.connect(self.atualizar_dashboard)
        selecao_layout.addWidget(self.combo_periodo_dash)

        # Filtro de ano (para período personalizado)
        selecao_layout.addWidget(QLabel("  Ano:"))
        self.combo_ano_dash = QComboBox()
        self.combo_ano_dash.setMinimumWidth(100)
        self.combo_ano_dash.currentIndexChanged.connect(self.atualizar_dashboard)
        self.combo_ano_dash.setEnabled(False)
        selecao_layout.addWidget(self.combo_ano_dash)

        # Botões de Ação (Excel e IA)
        self.btn_exportar_excel = QPushButton("Exportar Excel")
        self.btn_exportar_excel.setStyleSheet("background-color: #ffffff; color: black; font-weight: bold; padding: 5px;")
        self.btn_exportar_excel.clicked.connect(self.exportar_excel)
        selecao_layout.addWidget(self.btn_exportar_excel)

        self.btn_analise_ia = QPushButton("Consultoria IA")
        self.btn_analise_ia.setStyleSheet("background-color: #ffffff; color: black; font-weight: bold; padding: 5px;")
        self.btn_analise_ia.clicked.connect(self.gerar_analise_ia_financeira)
        selecao_layout.addWidget(self.btn_analise_ia)

        selecao_layout.addStretch()
        layout.addLayout(selecao_layout)

        # Container para gráficos
        self.graficos_container = QWidget()
        layout.addWidget(self.graficos_container, stretch=1)

        # Layout para gráficos
        graficos_layout = QVBoxLayout(self.graficos_container)

        # Tentar importar matplotlib
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            import matplotlib.pyplot as plt

            self.figure = Figure(figsize=(12, 8))
            self.canvas = FigureCanvas(self.figure)
            graficos_layout.addWidget(self.canvas)
            self.matplotlib_disponivel = True
        except ImportError as e:
            # Matplotlib não está instalado
            self.lbl_sem_matplotlib = QLabel("Matplotlib não está instalado.\nPara usar o Dashboard, instale com: pip install matplotlib")
            self.lbl_sem_matplotlib.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_sem_matplotlib.setStyleSheet("font-size: 14px; color: #dc3545; padding: 20px;")
            graficos_layout.addWidget(self.lbl_sem_matplotlib)
            self.matplotlib_disponivel = False
            self.canvas = None

        # Label de mensagem quando não há dados
        self.lbl_sem_dados = QLabel("Selecione uma empresa para visualizar o dashboard")
        self.lbl_sem_dados.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sem_dados.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(self.lbl_sem_dados)

        # Inicialmente esconder o canvas
        if self.canvas:
            self.canvas.hide()

    def atualizar_dashboard(self):
        """Atualiza o dashboard com os dados da empresa selecionada"""
        # Verificar se matplotlib está disponível
        if not self.matplotlib_disponivel:
            self.lbl_sem_dados.hide()
            if hasattr(self, 'lbl_sem_matplotlib'):
                self.lbl_sem_matplotlib.show()
            return

        empresa_id = self.combo_empresa_dash.currentData()
        if not empresa_id:
            self.lbl_sem_dados.setText("Selecione uma empresa para visualizar o dashboard")
            self.lbl_sem_dados.show()
            self.canvas.hide()
            return

        # Habilitar/desabilitar filtro de ano baseado no período selecionado
        periodo = self.combo_periodo_dash.currentData()
        if periodo == "personalizado":
            self.combo_ano_dash.setEnabled(True)
            # Preencher anos disponíveis
            anos = self.db.fetchall("SELECT DISTINCT ano FROM dados_mensais WHERE empresa_id = ? ORDER BY ano DESC", (empresa_id,))
            self.combo_ano_dash.clear()
            for ano in anos:
                self.combo_ano_dash.addItem(str(ano[0]), ano[0])
        else:
            self.combo_ano_dash.setEnabled(False)

        # Buscar dados mensais da empresa
        query = "SELECT mes, ano, receita_bruta, custos, despesas, impostos, lucro_operacional FROM dados_mensais WHERE empresa_id = ?"
        params = (empresa_id,)

        # Aplicar filtro de período
        if periodo == "trimestral":
            # Últimos 3 meses
            query += " ORDER BY ano DESC, mes DESC LIMIT 3"
        elif periodo == "anual":
            # Último ano (12 meses)
            query += " ORDER BY ano DESC, mes DESC LIMIT 12"
        elif periodo == "personalizado":
            # Filtro por ano específico
            ano_selecionado = self.combo_ano_dash.currentData()
            if ano_selecionado:
                query += " AND ano = ?"
                params = (empresa_id, ano_selecionado)
            query += " ORDER BY mes"
        else:  # todos
            query += " ORDER BY ano, mes"

        dados = self.db.fetchall(query, params)

        if not dados:
            self.lbl_sem_dados.setText("Nenhum dado mensal cadastrado para esta empresa.\nAdicione dados na aba 'Dados Mensais' primeiro.")
            self.lbl_sem_dados.show()
            self.canvas.hide()
            return

        # Inverter dados se necessário (para ordenação correta no gráfico)
        if periodo in ["trimestral", "anual"]:
            dados = dados[::-1]

        self.lbl_sem_dados.hide()
        if hasattr(self, 'lbl_sem_matplotlib'):
            self.lbl_sem_matplotlib.hide()
        self.canvas.show()

        # Preparar dados para o gráfico
        meses = [f"{d[0]}/{d[1]}" for d in dados]
        receita = [d[2] for d in dados]
        custos = [d[3] for d in dados]
        despesas = [d[4] for d in dados]
        lucro = [d[6] for d in dados]

        # Limpar figura anterior
        self.figure.clear()

        # Criar subplots
        ax1 = self.figure.add_subplot(2, 1, 1)
        ax2 = self.figure.add_subplot(2, 1, 2)

        # Gráfico 1: Receita vs Custos vs Despesas (interativo)
        line1, = ax1.plot(meses, receita, marker='o', label='Receita', color='green', linewidth=2, markersize=8)
        line2, = ax1.plot(meses, custos, marker='s', label='Custos', color='red', linewidth=2, markersize=8)
        line3, = ax1.plot(meses, despesas, marker='^', label='Despesas', color='orange', linewidth=2, markersize=8)
        
        # Adicionar tooltips interativos
        try:
            from mplcursors import cursor
            cursor([line1, line2, line3], hover=True)
        except ImportError:
            pass  # mplcursors não está instalado, gráfico sem tooltips
        
        ax1.set_title('Receita, Custos e Despesas por Mês', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Valor (R$)', fontsize=10)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)

        # Gráfico 2: Lucro Operacional (interativo)
        bars = ax2.bar(meses, lucro, color=['green' if l >= 0 else 'red' for l in lucro], alpha=0.7)
        
        # Adicionar tooltips nas barras
        try:
            from mplcursors import cursor
            cursor(bars, hover=True)
        except ImportError:
            pass
        
        ax2.set_title('Lucro Operacional por Mês', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Lucro (R$)', fontsize=10)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()

    def verificar_regime_para_trimestral(self):
        """Verifica o regime da empresa e mostra o painel trimestral correto"""
        empresa_id = self.combo_empresa_dados.currentData()
        if not empresa_id:
            self.grupo_trimestral.setVisible(False)
            self.grupo_trimestral_real.setVisible(False)
            return

        empresa = self.db.fetchone(
            "SELECT regime_tributario FROM empresas WHERE id = ?",
            (empresa_id,)
        )

        if empresa:
            regime = empresa[0]
            self.grupo_trimestral.setVisible(regime == 'presumido')
            self.grupo_trimestral_real.setVisible(regime == 'real')
        else:
            self.grupo_trimestral.setVisible(False)
            self.grupo_trimestral_real.setVisible(False)

    def calcular_impostos_trimestral(self):
        """Calcula os impostos trimestrais do Lucro Presumido"""
        try:
            # Obter valores das receitas
            receita1 = float(self.txt_receita_mes1.text().replace(',', '.') or 0)
            receita2 = float(self.txt_receita_mes2.text().replace(',', '.') or 0)
            receita3 = float(self.txt_receita_mes3.text().replace(',', '.') or 0)

            receita_trimestral = receita1 + receita2 + receita3
            tipo_atividade = self.combo_atividade_trimestral.currentData()

            if receita_trimestral == 0:
                QMessageBox.warning(self, "Aviso", "Digite pelo menos uma receita mensal.")
                return

            # Calcular impostos
            calc = CalculadoraImpostos()
            resultado = calc.calcular_lucro_presumido_trimestral(receita_trimestral, tipo_atividade)

            # Exibir resultados
            trimestre_text = self.combo_trimestre.currentText()
            ano = self.combo_ano_trimestral.currentText()

            texto_resultado = f"""
═══════════════════════════════════════════════════════════
  RESULTADO: {trimestre_text} de {ano}
═══════════════════════════════════════════════════════════

Receita Bruta Trimestral:       R$ {resultado['receita_bruta_trimestral']:,.2f}

───────────────────────────────────────────────────────────
BASES DE CÁLCULO
───────────────────────────────────────────────────────────
Base IRPJ ({resultado['presuncao_irpj']:.0f}%):          R$ {resultado['base_irpj_trimestral']:,.2f}
Base CSLL ({resultado['presuncao_csll']:.0f}%):          R$ {resultado['base_csll_trimestral']:,.2f}

───────────────────────────────────────────────────────────
IMPOSTOS FEDERAIS TRIMESTRAIS
───────────────────────────────────────────────────────────
IRPJ Normal (15%):               R$ {resultado['irpj_normal']:,.2f}
IRPJ Adicional (10% s/ excedente): R$ {resultado['irpj_adicional']:,.2f}
IRPJ TOTAL:                       R$ {resultado['irpj_total']:,.2f}

CSLL (9%):                       R$ {resultado['csll_total']:,.2f}
PIS (0,65%):                     R$ {resultado['pis_total']:,.2f}
COFINS (3%):                     R$ {resultado['cofins_total']:,.2f}

───────────────────────────────────────────────────────────
TOTAL DE IMPOSTOS FEDERAIS
───────────────────────────────────────────────────────────
✅ Total Trimestral:              R$ {resultado['total_impostos_trimestral']:,.2f}
💡 Média Mensal (provisionamento): R$ {resultado['media_mensal_impostos']:,.2f}

───────────────────────────────────────────────────────────
INFORMATIVO (Não entra no total federal)
───────────────────────────────────────────────────────────
ISS (municipal):                  R$ {resultado['iss_total']:,.2f}
ICMS (estadual):                 R$ {resultado['icms_total']:,.2f}
═══════════════════════════════════════════════════════════
            """

            self.lbl_resultados_trimestral.setText(texto_resultado)
            self.resultados_trimestral.setVisible(True)

        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite valores numéricos válidos para as receitas.")

    def calcular_lucro_real_trimestral_action(self):
        """Ação para calcular o lucro real trimestral a partir dos inputs da interface"""
        try:
            dados_trimestre = []
            for row in self.real_inputs:
                dados_trimestre.append({
                    'receita': float(row['rec'].text().replace(',', '.') or 0),
                    'custos': float(row['cus'].text().replace(',', '.') or 0),
                    'despesas': float(row['des'].text().replace(',', '.') or 0),
                    'creditos': float(row['cre'].text().replace(',', '.') or 0)
                })
            
            calc = CalculadoraImpostos()
            res = calc.calcular_lucro_real_trimestral(dados_trimestre)
            
            texto = f"""
═══════════════════════════════════════════════════════════
  FECHAMENTO TRIMESTRAL - LUCRO REAL
═══════════════════════════════════════════════════════════

Receita Bruta Total:           R$ {res['receita_total']:,.2f}
(-) Custos e Despesas:         R$ {res['custos_total'] + res['despesas_total']:,.2f}
───────────────────────────────────────────────────────────
LUCRO REAL DO TRIMESTRE:       R$ {res['lucro_trimestral']:,.2f}
───────────────────────────────────────────────────────────

IMPOSTOS SOBRE O LUCRO (IRPJ/CSLL)
IRPJ Normal (15%):             R$ {res['irpj_normal']:,.2f}
IRPJ Adicional (10% s/ 60k):   R$ {res['irpj_adicional']:,.2f}
CSLL (9%):                     R$ {res['csll_total']:,.2f}

IMPOSTOS SOBRE FATURAMENTO (PIS/COFINS)
PIS (1,65% liq.):              R$ {res['pis_total']:,.2f}
COFINS (7,6% liq.):            R$ {res['cofins_total']:,.2f}

───────────────────────────────────────────────────────────
✅ TOTAL TRIMESTRAL:            R$ {res['total_impostos_trimestral']:,.2f}
💡 Média Mensal:                R$ {res['media_mensal_impostos']:,.2f}
═══════════════════════════════════════════════════════════
            """
            self.lbl_resultados_real.setText(texto)
            
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite valores numéricos válidos.")

    def criar_aba_relatorios(self):
        page = QWidget()
        self.tabs.addTab(page, "Relatorios")
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        # Selecionar empresa
        selecao_layout = QHBoxLayout()
        selecao_layout.addWidget(QLabel("Empresa:"))
        self.combo_empresa_rel = QComboBox()
        self.combo_empresa_rel.setMinimumWidth(300)
        selecao_layout.addWidget(self.combo_empresa_rel)
        selecao_layout.addStretch()
        layout.addLayout(selecao_layout)
        
        # Opcoes de relatorio
        grupo_opcoes = QGroupBox("Tipo de Relatorio")
        layout.addWidget(grupo_opcoes)
        
        opcoes_layout = QVBoxLayout(grupo_opcoes)
        
        self.radio_pdf = QRadioButton("Apresentacao PPTX (Padrao)")
        self.radio_pdf.setChecked(True)
        opcoes_layout.addWidget(self.radio_pdf)
        
        # Seletor de Tema/Cores
        tema_layout = QHBoxLayout()
        tema_layout.addWidget(QLabel("Tema de Cores:"))
        self.combo_tema = QComboBox()
        self.combo_tema.setMinimumWidth(280)
        
        # Adicionar opções de cores pré-definidas
        for key, (nome, _) in OPCOES_CORES.items():
            self.combo_tema.addItem(nome, key)
        
        # Adicionar opção de cores personalizadas
        self.combo_tema.addItem("🎨 Cores Personalizadas", "personalizado")

        tema_layout.addWidget(self.combo_tema)
        tema_layout.addStretch()
        opcoes_layout.addLayout(tema_layout)

        # Seletor de Cores Personalizadas (inicialmente oculto)
        self.grupo_cores_personalizadas = QGroupBox("Cores Personalizadas")
        self.grupo_cores_personalizadas.setVisible(False)
        opcoes_layout.addWidget(self.grupo_cores_personalizadas)

        cores_layout = QGridLayout(self.grupo_cores_personalizadas)

        # Cor de Fundo
        cores_layout.addWidget(QLabel("Fundo:"), 0, 0)
        self.btn_cor_fundo = QPushButton("Selecionar")
        self.btn_cor_fundo.clicked.connect(self.selecionar_cor_fundo)
        self.btn_cor_fundo.setStyleSheet("background-color: #FFFFFF; min-width: 100px;")
        cores_layout.addWidget(self.btn_cor_fundo, 0, 1)
        self.cor_fundo = RGBColor(255, 255, 255)  # Branco padrão

        # Cor do Header
        cores_layout.addWidget(QLabel("Header:"), 1, 0)
        self.btn_cor_header = QPushButton("Selecionar")
        self.btn_cor_header.clicked.connect(self.selecionar_cor_header)
        self.btn_cor_header.setStyleSheet("background-color: #000080; color: white; min-width: 100px;")
        cores_layout.addWidget(self.btn_cor_header, 1, 1)
        self.cor_header = RGBColor(0, 0, 128)  # Azul escuro padrão

        # Cor do Footer
        cores_layout.addWidget(QLabel("Footer:"), 2, 0)
        self.btn_cor_footer = QPushButton("Selecionar")
        self.btn_cor_footer.clicked.connect(self.selecionar_cor_footer)
        self.btn_cor_footer.setStyleSheet("background-color: #000080; color: white; min-width: 100px;")
        cores_layout.addWidget(self.btn_cor_footer, 2, 1)
        self.cor_footer = RGBColor(0, 0, 128)  # Azul escuro padrão

        # Cor do Texto
        cores_layout.addWidget(QLabel("Texto:"), 3, 0)
        self.btn_cor_texto = QPushButton("Selecionar")
        self.btn_cor_texto.clicked.connect(self.selecionar_cor_texto)
        self.btn_cor_texto.setStyleSheet("background-color: #000000; color: white; min-width: 100px;")
        cores_layout.addWidget(self.btn_cor_texto, 3, 1)
        self.cor_texto = RGBColor(0, 0, 0)  # Preto padrão

        # Cor de Destaque
        cores_layout.addWidget(QLabel("Destaque:"), 4, 0)
        self.btn_cor_destaque = QPushButton("Selecionar")
        self.btn_cor_destaque.clicked.connect(self.selecionar_cor_destaque)
        self.btn_cor_destaque.setStyleSheet("background-color: #D4AF37; color: white; min-width: 100px;")
        cores_layout.addWidget(self.btn_cor_destaque, 4, 1)
        self.cor_destaque = RGBColor(212, 175, 55)  # Dourado padrão

        # Conectar mudança no combo para mostrar/ocultar cores personalizadas
        self.combo_tema.currentIndexChanged.connect(self.on_tema_changed)
        
        self.radio_ia = QRadioButton("Apresentacao com IA Inteligente (requer Ollama)")
        opcoes_layout.addWidget(self.radio_ia)
        
        # Comando IA
        opcoes_layout.addWidget(QLabel("Comando para IA (opcional):"))
        self.txt_comando_ia = QTextEdit()
        self.txt_comando_ia.setMaximumHeight(60)
        self.txt_comando_ia.setPlaceholderText("Ex: Elegante com fundo branco, titulos em dourado...")
        opcoes_layout.addWidget(self.txt_comando_ia)
        
        # Botao gerar PPTX
        layout.addSpacing(10)
        btn_gerar = QPushButton("GERAR APRESENTACAO PPTX")
        btn_gerar.setMinimumHeight(40)
        btn_gerar.clicked.connect(self.gerar_relatorio)
        layout.addWidget(btn_gerar)
        
        # Botao gerar PDF
        btn_gerar_pdf = QPushButton("GERAR DEMONSTRATIVO PDF")
        btn_gerar_pdf.setMinimumHeight(40)
        btn_gerar_pdf.setStyleSheet("background-color: #f0f0f0; color: #333;")
        btn_gerar_pdf.clicked.connect(self.gerar_demonstrativo_pdf_action)
        layout.addWidget(btn_gerar_pdf)
        
        # Progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()

    def salvar_empresa(self):
        nome = self.txt_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "Digite o nome da empresa")
            return

        regime = self.combo_regime.currentData()

        self.db.execute(
            "INSERT INTO empresas (nome, cnpj, responsavel, cidade, estado, regime_tributario) VALUES (?, ?, ?, ?, ?, ?)",
            (nome, self.txt_cnpj.text(), self.txt_responsavel.text(),
             self.txt_cidade.text(), self.txt_estado.text(), regime)
        )

        self.txt_nome.clear()
        self.txt_cnpj.clear()
        self.txt_responsavel.clear()
        self.txt_cidade.clear()
        self.txt_estado.clear()
        
        self.atualizar_lista_empresas()
        QMessageBox.information(self, "Sucesso", "Empresa cadastrada!")

    def atualizar_lista_empresas(self):
        empresas = self.db.fetchall("SELECT id, nome, cnpj, responsavel FROM empresas ORDER BY nome")
        
        self.tabela_empresas.setRowCount(len(empresas))
        for i, emp in enumerate(empresas):
            for j, val in enumerate(emp):
                self.tabela_empresas.setItem(i, j, QTableWidgetItem(str(val)))
            
            btn_excluir = QPushButton("Excluir")
            btn_excluir.clicked.connect(lambda checked, id=emp[0]: self.excluir_empresa(id))
            self.tabela_empresas.setCellWidget(i, 4, btn_excluir)
        
        # Atualizar combos
        self.combo_empresa_dados.clear()
        self.combo_empresa_rel.clear()
        self.combo_empresa_dash.clear()
        for emp in empresas:
            texto = f"{emp[1]} (CNPJ: {emp[2] or 'N/A'})"
            self.combo_empresa_dados.addItem(texto, emp[0])
            self.combo_empresa_rel.addItem(texto, emp[0])
            self.combo_empresa_dash.addItem(texto, emp[0])

        # Verificar regime para mostrar/ocultar cálculo trimestral
        if empresas:
            self.verificar_regime_para_trimestral()

    def excluir_empresa(self, empresa_id):
        resposta = QMessageBox.question(self, "Confirmar", "Deseja excluir esta empresa?")
        if resposta == QMessageBox.StandardButton.Yes:
            self.db.execute("DELETE FROM dados_mensais WHERE empresa_id = ?", (empresa_id,))
            self.db.execute("DELETE FROM empresas WHERE id = ?", (empresa_id,))
            self.atualizar_lista_empresas()

    def calcular_totais(self):
        """Calcula totais de custos, despesas e lucro automaticamente"""
        try:
            # Custos detalhados
            salarios = float(self.txt_custo_salarios.text() or 0)
            aluguel = float(self.txt_custo_aluguel.text() or 0)
            outros_custos = float(self.txt_custo_outros.text() or 0)
            total_custos = salarios + aluguel + outros_custos
            self.txt_custos_total.setText(f"{total_custos:.2f}")

            # Despesas detalhadas
            agua_luz_tel = float(self.txt_despesa_agua_luz_tel.text() or 0)
            material = float(self.txt_despesa_material.text() or 0)
            outras_despesas = float(self.txt_despesa_outros.text() or 0)
            total_despesas = agua_luz_tel + material + outras_despesas
            self.txt_despesas_total.setText(f"{total_despesas:.2f}")

            # Lucro
            receita = float(self.txt_receita.text() or 0)
            impostos = float(self.txt_impostos.text() or 0)
            lucro = receita - total_custos - total_despesas - impostos
            self.txt_lucro.setText(f"{lucro:.2f}")
        except ValueError:
            self.txt_custos_total.setText("0")
            self.txt_despesas_total.setText("0")
            self.txt_lucro.setText("0")

    def calcular_impostos_automatico(self):
        """Calcula impostos automaticamente baseado no regime tributário da empresa"""
        empresa_id = self.combo_empresa_dados.currentData()
        if not empresa_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma empresa primeiro")
            return

        # Buscar regime tributário da empresa
        empresa = self.db.fetchone(
            "SELECT regime_tributario FROM empresas WHERE id = ?",
            (empresa_id,)
        )

        if not empresa:
            QMessageBox.warning(self, "Erro", "Empresa não encontrada")
            return

        regime = empresa[0]

        # Pegar receita bruta
        try:
            receita = float(self.txt_receita.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite um valor válido para receita bruta")
            return

        # Pegar custos e despesas (para lucro real)
        try:
            custos = float(self.txt_custos_total.text() or 0)
            despesas = float(self.txt_despesas_total.text() or 0)
        except ValueError:
            custos = 0
            despesas = 0

        # Calcular impostos
        try:
            calc = CalculadoraImpostos()
            # Para Lucro Presumido, usar 'servicos' como padrão (pode ser ajustado no futuro)
            tipo_atividade = 'servicos' if regime == 'presumido' else 'comercio'
            resultado = calc.calcular_impostos(
                receita_bruta=receita,
                regime=regime,
                custos=custos,
                despesas=despesas,
                tipo_atividade=tipo_atividade
            )

            # Mostrar detalhes
            detalhes = f"""
Regime: {resultado['regime']}
{resultado['descricao']}

Detalhamento:
"""
            if regime == 'simples':
                detalhes += f"Anexo: {resultado['anexo']} | Faixa: {resultado['faixa']}\n"
                detalhes += f"RBT12 (Faturamento 12m):   R$ {resultado['faturamento_anual']:,.2f}\n"
                detalhes += f"Alíquota Nominal:           {resultado['aliquota_nominal']:.2f}%\n"
                detalhes += f"Parcela a Deduzir (anual):  R$ {resultado['parcela_deduzir_anual']:,.2f}\n"
                detalhes += f"─────────────────────────────────────\n"
                detalhes += f"Alíquota Efetiva:           {resultado['aliquota_efetiva']:.2f}%\n"
                detalhes += f"─────────────────────────────────────\n"
                detalhes += f"DAS (Guia Mensal):          R$ {resultado['das']:,.2f}\n"
                if resultado['iss'] > 0:
                    detalhes += f"  ISS (incluso no DAS):    R$ {resultado['iss']:,.2f}\n"
                if resultado['icms'] > 0:
                    detalhes += f"  ICMS (incluso no DAS):   R$ {resultado['icms']:,.2f}\n"
                # Preencher campo de impostos para Simples
                self.txt_impostos.setText(f"{resultado['total_impostos']:.2f}")
            elif regime == 'presumido':
                detalhes += f"Tipo de Atividade: {resultado['tipo_atividade']}\n"
                detalhes += f"Base IRPJ: R$ {resultado['base_irpj']:.2f}\n"
                detalhes += f"Base CSLL: R$ {resultado['base_csll']:.2f}\n"
                detalhes += f"IRPJ: R$ {resultado['irpj']:.2f}\n"
                detalhes += f"CSLL: R$ {resultado['csll']:.2f}\n"
                detalhes += f"PIS: R$ {resultado['pis']:.2f}\n"
                detalhes += f"COFINS: R$ {resultado['cofins']:.2f}\n"
                detalhes += f"PIS/COFINS: R$ {resultado['pis_cofins']:.2f}\n"
                if resultado['iss'] > 0:
                    detalhes += f"ISS: R$ {resultado['iss']:.2f}\n"
                if resultado['icms'] > 0:
                    detalhes += f"ICMS: R$ {resultado['icms']:.2f}\n"
                # Preencher campo de impostos para Presumido
                self.txt_impostos.setText(f"{resultado['total_impostos']:.2f}")
            elif regime == 'real':
                # Pegar créditos informados
                try:
                    creditos_v = float(self.txt_creditos.text().replace(',', '.') or 0)
                except ValueError:
                    creditos_v = 0

                # Usar cálculo profissional para Lucro Real
                calc_prof = CalculoProfissional(self.db)
                resultado_prof = calc_prof.calcular_lucro_real_profissional(
                    empresa_id=empresa_id,
                    mes=self.spin_mes.value(),
                    ano=self.spin_ano.value(),
                    receita_bruta=receita,
                    custos=custos,
                    despesas=despesas,
                    creditos_pis=creditos_v, 
                    creditos_cofins=creditos_v, # No simplificado usamos o mesmo valor base
                    icms_saida=(receita / 1.12) * 0.12,
                    icms_entrada=0,
                    prejuizo_a_compensar=0,
                    tipo_atividade='servicos'
                )

                # Gerar DRE e Memória
                dre = calc_prof.gerar_dre(resultado_prof)
                memoria = calc_prof.gerar_memoria_calculo(resultado_prof)

                detalhes += f"═══ CÁLCULO PROFISSIONAL - LUCRO REAL ═══\n\n"
                detalhes += f"Lucro Real: R$ {resultado_prof.lucro_real:,.2f}\n\n"
                detalhes += "─ IMPOSTOS SOBRE O LUCRO ─\n"
                detalhes += f"  IRPJ (15% + adicional): R$ {resultado_prof.irpj:,.2f}\n"
                detalhes += f"  CSLL (9%):              R$ {resultado_prof.csll:,.2f}\n"
                detalhes += f"  Subtotal:               R$ {resultado_prof.subtotal_lucro:,.2f}\n\n"
                detalhes += "─ IMPOSTOS SOBRE FATURAMENTO ─\n"
                detalhes += f"  PIS (1,65%):    Déb. R$ {resultado_prof.pis_debito:,.2f} - Créd. R$ {resultado_prof.pis_credito:,.2f} = R$ {resultado_prof.pis_total:,.2f}\n"
                detalhes += f"  COFINS (7,6%):  Déb. R$ {resultado_prof.cofins_debito:,.2f} - Créd. R$ {resultado_prof.cofins_credito:,.2f} = R$ {resultado_prof.cofins_total:,.2f}\n"
                detalhes += f"  ICMS:           Déb. R$ {resultado_prof.icms_saida:,.2f} - Créd. R$ {resultado_prof.icms_entrada:,.2f} = R$ {resultado_prof.icms_total:,.2f}\n"
                detalhes += f"  ISS (3%):       R$ {resultado_prof.iss:,.2f}\n\n"

                # Salvar resultado para possível exportação
                self.ultimo_resultado_lucro_real = resultado_prof
                self.dre_lucro_real = dre
                self.memoria_lucro_real = memoria

                # Preencher campo de impostos para Lucro Real
                self.txt_impostos.setText(f"{resultado_prof.total_impostos:.2f}")
                # Atualizar resultado para mostrar total correto
                resultado = {'total_impostos': resultado_prof.total_impostos}

            detalhes += f"\n═══════════════════════════════════\n"
            if regime == 'real':
                detalhes += f"TOTAL DE IMPOSTOS: R$ {resultado_prof.total_impostos:,.2f}\n"
            else:
                detalhes += f"TOTAL DE IMPOSTOS: R$ {resultado['total_impostos']:,.2f}\n"
            detalhes += f"═══════════════════════════════════"

            QMessageBox.information(self, "Cálculo de Impostos", detalhes)

            # Recalcular lucro
            self.calcular_totais()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao calcular impostos: {str(e)}")

    def adicionar_dados_mensais(self):
        empresa_id = self.combo_empresa_dados.currentData()
        if not empresa_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma empresa")
            return
        
        try:
            # Receita
            receita = float(self.txt_receita.text() or 0)
            
            # Custos detalhados
            custo_salarios = float(self.txt_custo_salarios.text() or 0)
            custo_aluguel = float(self.txt_custo_aluguel.text() or 0)
            custo_outros = float(self.txt_custo_outros.text() or 0)
            
            # Despesas detalhadas
            despesa_agua_luz_tel = float(self.txt_despesa_agua_luz_tel.text() or 0)
            despesa_material = float(self.txt_despesa_material.text() or 0)
            despesa_outros = float(self.txt_despesa_outros.text() or 0)
            
            # Totais
            custos = custo_salarios + custo_aluguel + custo_outros
            despesas = despesa_agua_luz_tel + despesa_material + despesa_outros
            
            impostos = float(self.txt_impostos.text() or 0)
            lucro = float(self.txt_lucro.text() or 0)
            creditos = float(self.txt_creditos.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valores numericos invalidos")
            return
        
        self.db.execute('''
            INSERT INTO dados_mensais (
                empresa_id, mes, ano, 
                receita_bruta, 
                custo_salarios, custo_aluguel, custo_outros,
                despesa_agua_luz_tel, despesa_material, despesa_outros,
                custos, despesas, impostos, lucro_operacional, creditos_pis_cofins
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            empresa_id, self.spin_mes.value(), self.spin_ano.value(),
            receita,
            custo_salarios, custo_aluguel, custo_outros,
            despesa_agua_luz_tel, despesa_material, despesa_outros,
            custos, despesas, impostos, lucro, creditos
        ))
        
        self.atualizar_tabela_dados(empresa_id)
        self.limpar_campos_dados()
        QMessageBox.information(self, "Sucesso", "Dados adicionados!")

    def limpar_campos_dados(self):
        """Limpa os campos de entrada após adicionar dados"""
        self.txt_receita.setText("0")
        self.txt_custo_salarios.setText("0")
        self.txt_custo_aluguel.setText("0")
        self.txt_custo_outros.setText("0")
        self.txt_despesa_agua_luz_tel.setText("0")
        self.txt_despesa_material.setText("0")
        self.txt_despesa_outros.setText("0")
        self.txt_impostos.setText("0")
        self.txt_lucro.setText("0")
        self.txt_creditos.setText("0")
        self.calcular_totais()

    def atualizar_tabela_dados(self, empresa_id):
        dados = self.db.fetchall(
            "SELECT mes, ano, receita_bruta, custos, despesas, impostos, lucro_operacional, id FROM dados_mensais WHERE empresa_id = ? ORDER BY ano, mes",
            (empresa_id,)
        )
        
        self.tabela_dados.setRowCount(len(dados))
        for i, d in enumerate(dados):
            self.tabela_dados.setItem(i, 0, QTableWidgetItem(f"{d[0]:02d}/{d[1]}"))
            self.tabela_dados.setItem(i, 1, QTableWidgetItem(f"R$ {d[2]:,.2f}"))
            self.tabela_dados.setItem(i, 2, QTableWidgetItem(f"R$ {d[3]:,.2f}"))
            self.tabela_dados.setItem(i, 3, QTableWidgetItem(f"R$ {d[4]:,.2f}"))
            self.tabela_dados.setItem(i, 4, QTableWidgetItem(f"R$ {d[5]:,.2f}"))
            self.tabela_dados.setItem(i, 5, QTableWidgetItem(f"R$ {d[6]:,.2f}"))
            
            btn_excluir = QPushButton("Excluir")
            btn_excluir.clicked.connect(lambda checked, id=d[7]: self.excluir_dado(id))
            self.tabela_dados.setCellWidget(i, 6, btn_excluir)

    def excluir_dado(self, dado_id):
        self.db.execute("DELETE FROM dados_mensais WHERE id = ?", (dado_id,))
        empresa_id = self.combo_empresa_dados.currentData()
        self.atualizar_tabela_dados(empresa_id)

    def gerar_relatorio(self):
        empresa_id = self.combo_empresa_rel.currentData()
        if not empresa_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma empresa")
            return
        
        empresa = self.db.fetchone("SELECT nome, responsavel FROM empresas WHERE id = ?", (empresa_id,))
        dados = self.db.fetchall(
            """SELECT mes, ano, receita_bruta, 
                custo_salarios, custo_aluguel, custo_outros,
                despesa_agua_luz_tel, despesa_material, despesa_outros,
                custos, despesas, impostos, lucro_operacional 
                FROM dados_mensais WHERE empresa_id = ? ORDER BY ano, mes""",
            (empresa_id,)
        )
        
        if not dados:
            QMessageBox.warning(self, "Aviso", "Nenhum dado mensal cadastrado")
            return
        
        dados_formatados = [
            {
                "mes": d[0], "ano": d[1], "receita_bruta": d[2],
                # Custos detalhados
                "custo_salarios": d[3], "custo_aluguel": d[4], "custo_outros": d[5],
                # Despesas detalhadas
                "despesa_agua_luz_tel": d[6], "despesa_material": d[7], "despesa_outros": d[8],
                # Totais
                "custos": d[9], "despesas": d[10], "impostos": d[11], "lucro_operacional": d[12]
            }
            for d in dados
        ]
        
        use_ia = self.radio_ia.isChecked()
        comando_ia = self.txt_comando_ia.toPlainText().strip()
        tema_key = self.combo_tema.currentData()

        bundle_dir = os.path.dirname(os.path.abspath(__file__))

        # Se tema personalizado, criar dicionário de cores personalizadas
        cores_personalizadas = None
        if tema_key == "personalizado":
            cores_personalizadas = {
                'primaria': self.cor_header,
                'secundaria': self.cor_footer,
                'header': self.cor_header,
                'footer': self.cor_footer,
                'fundo': self.cor_fundo,
                'texto': self.cor_texto,
                'texto_secundario': self.cor_texto,
                'destaque': self.cor_destaque
            }

        self.thread = GeradorPPTXThread(dados_formatados, empresa[0], empresa[1] or "", bundle_dir, use_ia, comando_ia, tema_key, cores_personalizadas)
        self.thread.progress.connect(self.atualizar_progresso)
        self.thread.finished.connect(self.relatorio_gerado)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.thread.start()

    def gerar_demonstrativo_pdf_action(self):
        """Ação ao clicar no botão de gerar PDF Analítico"""
        empresa_id = self.combo_empresa_rel.currentData()
        if not empresa_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma empresa")
            return

        empresa = self.db.fetchone("SELECT nome, cnpj FROM empresas WHERE id = ?", (empresa_id,))
        dados = self.db.fetchall(
            "SELECT mes, ano, receita_bruta, custos, despesas, impostos, lucro_operacional FROM dados_mensais WHERE empresa_id = ? ORDER BY ano, mes",
            (empresa_id,)
        )
        
        if not dados:
            QMessageBox.warning(self, "Aviso", "Nenhum dado mensal cadastrado")
            return
            
        dados_formatados = [
            {
                "mes": d[0], "ano": d[1], "receita_bruta": d[2],
                "custos": d[3], "despesas": d[4], "impostos": d[5], "lucro_operacional": d[6]
            }
            for d in dados
        ]
        
        try:
            path = gerar_relatorio_pdf(dados_formatados, empresa[0], empresa[1] or "Não informado")
            if path:
                QMessageBox.information(self, "Sucesso", f"Demonstrativo PDF gerado com sucesso na Área de Trabalho:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar PDF: {e}")

    def atualizar_progresso(self, valor):
        self.progress_bar.setValue(valor)

    def relatorio_gerado(self, sucesso, resultado):
        self.progress_bar.setVisible(False)
        if sucesso:
            QMessageBox.information(self, "Sucesso", f"Relatorio gerado:\n{resultado}")
        else:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar:\n{resultado}")

    def on_tema_changed(self, index):
        """Mostra/oculta o grupo de cores personalizadas quando selecionado"""
        tema_key = self.combo_tema.currentData()
        if tema_key == "personalizado":
            self.grupo_cores_personalizadas.setVisible(True)
        else:
            self.grupo_cores_personalizadas.setVisible(False)

    def selecionar_cor_fundo(self):
        cor = QColorDialog.getColor()
        if cor.isValid():
            self.cor_fundo = RGBColor(cor.red(), cor.green(), cor.blue())
            self.btn_cor_fundo.setStyleSheet(f"background-color: {cor.name()}; min-width: 100px;")

    def selecionar_cor_header(self):
        cor = QColorDialog.getColor()
        if cor.isValid():
            self.cor_header = RGBColor(cor.red(), cor.green(), cor.blue())
            self.btn_cor_header.setStyleSheet(f"background-color: {cor.name()}; color: white; min-width: 100px;")

    def selecionar_cor_footer(self):
        cor = QColorDialog.getColor()
        if cor.isValid():
            self.cor_footer = RGBColor(cor.red(), cor.green(), cor.blue())
            self.btn_cor_footer.setStyleSheet(f"background-color: {cor.name()}; color: white; min-width: 100px;")

    def selecionar_cor_texto(self):
        cor = QColorDialog.getColor()
        if cor.isValid():
            self.cor_texto = RGBColor(cor.red(), cor.green(), cor.blue())
            self.btn_cor_texto.setStyleSheet(f"background-color: {cor.name()}; color: white; min-width: 100px;")

    def selecionar_cor_destaque(self):
        cor = QColorDialog.getColor()
        if cor.isValid():
            self.cor_destaque = RGBColor(cor.red(), cor.green(), cor.blue())
            self.btn_cor_destaque.setStyleSheet(f"background-color: {cor.name()}; color: white; min-width: 100px;")

    def exportar_excel(self):
        """Exporta os dados filtrados no Dashboard para um arquivo Excel"""
        empresa_id = self.combo_empresa_dash.currentData()
        if not empresa_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma empresa primeiro.")
            return

        nome_empresa = self.combo_empresa_dash.currentText()
        
        # Buscar dados (mesma lógica do dashboard)
        periodo = self.combo_periodo_dash.currentData()
        query = "SELECT mes, ano, receita_bruta, custos, despesas, impostos, lucro_operacional FROM dados_mensais WHERE empresa_id = ?"
        params = (empresa_id,)

        if periodo == "trimestral":
            query += " ORDER BY ano DESC, mes DESC LIMIT 3"
        elif periodo == "anual":
            query += " ORDER BY ano DESC, mes DESC LIMIT 12"
        elif periodo == "personalizado":
            ano_selecionado = self.combo_ano_dash.currentData()
            if ano_selecionado:
                query += " AND ano = ?"
                params = (empresa_id, ano_selecionado)
            query += " ORDER BY mes"
        else:
            query += " ORDER BY ano, mes"

        dados = self.db.fetchall(query, params)
        if not dados:
            QMessageBox.warning(self, "Aviso", "Não há dados para exportar.")
            return

        try:
            # Criar DataFrame
            df = pd.DataFrame(dados, columns=["Mês", "Ano", "Receita Bruta", "Custos", "Despesas", "Impostos", "Lucro Operacional"])
            
            # Diálogo para salvar
            filename, _ = QFileDialog.getSaveFileName(
                self, "Salvar Relatório Excel", 
                f"Relatorio_{nome_empresa.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "Excel Files (*.xlsx)"
            )

            if filename:
                df.to_excel(filename, index=False)
                QMessageBox.information(self, "Sucesso", f"Relatório exportado com sucesso para:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar Excel: {str(e)}")

    def gerar_analise_ia_financeira(self):
        """Gera um diagnóstico financeiro usando IA baseada nos dados do dashboard"""
        empresa_id = self.combo_empresa_dash.currentData()
        if not empresa_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma empresa primeiro.")
            return

        if not IA_INTELIGENTE_DISPONIVEL:
            QMessageBox.warning(self, "Aviso", "Funcionalidades de IA não estão disponíveis.")
            return

        # Buscar dados recentes
        dados_raw = self.db.fetchall(
            "SELECT mes, ano, receita_bruta, custos, despesas, impostos, lucro_operacional FROM dados_mensais WHERE empresa_id = ? ORDER BY ano DESC, mes DESC LIMIT 6",
            (empresa_id,)
        )
        
        if not dados_raw:
            QMessageBox.warning(self, "Aviso", "Dados insuficientes para análise de IA.")
            return

        # Converter para lista de dicionários
        dados_mensais = []
        for d in dados_raw:
            dados_mensais.append({
                "mes": d[0], "ano": d[1], "receita_bruta": d[2],
                "custos": d[3], "despesas": d[4], "impostos": d[5],
                "lucro_operacional": d[6]
            })

        # Perguntar o que a IA deve fazer (comando personalizado)
        from PyQt6.QtWidgets import QInputDialog
        
        default_prompt = "forneça um diagnóstico estratégico curto, identifique 1 tendência clara e dê 2 sugestões estratégicas."
        
        comando, ok = QInputDialog.getMultiLineText(
            self, "Consultoria IA", 
            "O que a IA deve fazer? (Deixe como está para o padrão)",
            default_prompt
        )
        
        if not ok:
            return

        # Mostrar diálogo de progresso
        self.dlg_progress_ia = QDialog(self)
        self.dlg_progress_ia.setWindowTitle("Análise Inteligente")
        self.dlg_progress_ia.setFixedSize(300, 100)
        prog_layout = QVBoxLayout(self.dlg_progress_ia)
        prog_layout.addWidget(QLabel("O consultor IA está analisando seus dados..."))
        self.bar_ia = QProgressBar()
        self.bar_ia.setRange(0, 0)
        prog_layout.addWidget(self.bar_ia)
        
        # Iniciar thread com o comando personalizado
        comando_final = comando if comando != default_prompt else ""
        self.thread_ia = AnalisadorIAFinanceiraThread(dados_mensais, self.combo_empresa_dash.currentText(), comando_final)
        self.thread_ia.finished.connect(self.analise_ia_concluida)
        self.thread_ia.start()
        
        self.dlg_progress_ia.exec()

    def analise_ia_concluida(self, diagnostico):
        """Chamado quando a thread de IA termina"""
        if hasattr(self, 'dlg_progress_ia'):
            self.dlg_progress_ia.close()
        
        if not diagnostico or diagnostico.strip() == "":
            diagnostico = "A IA não conseguiu gerar uma resposta. Verifique se o Ollama está funcionando corretamente."
            
        self.exibir_analise_ia(diagnostico)

    def exibir_analise_ia(self, texto):
        """Abre um diálogo para exibir o diagnóstico da IA no estilo clássico"""
        dlg = QDialog(self)
        dlg.setWindowTitle("Relatório de Consultoria IA")
        dlg.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dlg)
        
        # Grupo de Resultado (Estilo Clássico)
        group = QGroupBox("Diagnóstico Estratégico")
        group_layout = QVBoxLayout(group)
        
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setPlainText(texto)
        group_layout.addWidget(txt)
        
        layout.addWidget(group)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(dlg.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        dlg.exec()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
