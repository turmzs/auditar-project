import os
from datetime import datetime
from fpdf import FPDF

class GeradorPDFAnalitico(FPDF):
    def __init__(self, nome_empresa, cnpj, periodo):
        super().__init__()
        self.nome_empresa = nome_empresa
        self.cnpj = cnpj
        self.periodo = periodo
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Esquerda: Dados da Empresa
        self.set_font('helvetica', 'B', 10)
        self.cell(100, 5, self.nome_empresa.upper(), ln=True)
        
        self.set_font('helvetica', '', 8)
        self.cell(100, 4, f"CNPJ: {self.cnpj}", ln=True)
        self.cell(100, 4, f"Período: {self.periodo}", ln=True)
        
        # Direita: Metadados (Página, Emissão, Hora)
        self.set_y(10)
        agora = datetime.now()
        self.set_font('helvetica', '', 8)
        self.cell(0, 4, f"Página:           {self.page_no():04d}", ln=True, align='R')
        self.cell(0, 4, f"Emissão:    {agora.strftime('%d/%m/%Y')}", ln=True, align='R')
        self.cell(0, 4, f"Hora:             {agora.strftime('%H:%M')}", ln=True, align='R')
        
        # Linha Divisória Superior
        self.set_y(25)
        self.line(10, 26, 200, 26)
        
        # Título Centralizado (Estilo Acompanhamento de Serviços)
        self.ln(3)
        self.set_font('helvetica', 'B', 9)
        self.cell(0, 5, "DEMONSTRATIVO DE ACOMPANHAMENTO MENSAL", ln=True, align='C')
        
        # Linha Divisória Inferior do Título
        self.line(10, 32, 200, 32)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 7)
        self.cell(0, 10, f'Sistema Auditar Tax & AI - Relatório Gerencial de Resultados', align='C')

    def criar_tabela(self, dados_mensais):
        # Cabeçalho da Tabela (Fundo branco com linhas pretas finas como na imagem)
        self.set_font('helvetica', 'B', 8)
        
        # Largura das colunas (Total 190)
        w = [25, 40, 35, 30, 35, 25]
        headers = ["Mês/Ano", "Receita Bruta", "Custos/Oper.", "Impostos", "Lucro Líquido", "Margem %"]
        
        # Linha superior da tabela
        self.line(10, self.get_y(), 200, self.get_y())
        
        for i in range(len(headers)):
            align = 'C' if i == 0 or i == 5 else 'R'
            self.cell(w[i], 6, headers[i], border=0, align=align)
        self.ln()
        
        # Linha inferior do cabeçalho
        self.line(10, self.get_y(), 200, self.get_y())

        # Dados
        self.set_font('helvetica', '', 8)
        fill = False
        
        total_receita = 0
        total_custos = 0
        total_impostos = 0
        total_lucro = 0

        for d in dados_mensais:
            # Cor de fundo zebrada (cinza bem clarinho)
            if fill:
                self.set_fill_color(242, 242, 242)
            else:
                self.set_fill_color(255, 255, 255)

            # Formatação de valores
            mes_ano = f"{str(d['mes']).zfill(2)}/{d['ano']}"
            receita = d.get('receita_bruta', 0)
            custos = d.get('custos', 0) + d.get('despesas', 0)
            impostos = d.get('impostos', 0)
            lucro = d.get('lucro_operacional', 0)
            margem = (lucro / receita * 100) if receita > 0 else 0

            # Atualizar totais
            total_receita += receita
            total_custos += custos
            total_impostos += impostos
            total_lucro += lucro

            # Linha da tabela (estilo zebra sem bordas verticais pesadas)
            self.cell(w[0], 6, mes_ano, border=0, align='C', fill=True)
            self.cell(w[1], 6, f"{receita:,.2f}", border=0, align='R', fill=True)
            self.cell(w[2], 6, f"{custos:,.2f}", border=0, align='R', fill=True)
            self.cell(w[3], 6, f"{impostos:,.2f}", border=0, align='R', fill=True)
            self.cell(w[4], 6, f"{lucro:,.2f}", border=0, align='R', fill=True)
            self.cell(w[5], 6, f"{margem:.1f}%", border=0, align='C', fill=True)
            self.ln()
            fill = not fill

        # Linha de Totais
        self.ln(2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font('helvetica', 'B', 8)
        margem_total = (total_lucro / total_receita * 100) if total_receita > 0 else 0
        
        self.cell(w[0], 7, "TOTALIZADORES", border=0, align='L')
        self.cell(w[1], 7, f"{total_receita:,.2f}", border=0, align='R')
        self.cell(w[2], 7, f"{total_custos:,.2f}", border=0, align='R')
        self.cell(w[3], 7, f"{total_impostos:,.2f}", border=0, align='R')
        self.cell(w[4], 7, f"{total_lucro:,.2f}", border=0, align='R')
        self.cell(w[5], 7, f"{margem_total:.1f}%", border=0, align='C')
        self.line(10, self.get_y() + 7, 200, self.get_y() + 7)

def gerar_relatorio_pdf(dados_mensais, nome_empresa, cnpj):
    """Função principal para gerar o arquivo PDF"""
    if not dados_mensais:
        return None
    
    # Determinar período
    inicio = f"{str(dados_mensais[0]['mes']).zfill(2)}/{dados_mensais[0]['ano']}"
    fim = f"{str(dados_mensais[-1]['mes']).zfill(2)}/{dados_mensais[-1]['ano']}"
    periodo = f"{inicio} até {fim}"
    
    pdf = GeradorPDFAnalitico(nome_empresa, cnpj, periodo)
    pdf.add_page()
    pdf.criar_tabela(dados_mensais)
    
    # Salvar na pasta de downloads ou desktop
    output_path = os.path.join(os.path.expanduser("~"), "Desktop", f"Demonstrativo_{nome_empresa.replace(' ', '_')}.pdf")
    pdf.output(output_path)
    return output_path
