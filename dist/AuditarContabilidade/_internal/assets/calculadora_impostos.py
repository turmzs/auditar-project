"""
Calculadora de Impostos Brasileiros
Implementa cálculos para Simples Nacional, Lucro Presumido e Lucro Real
"""

class CalculadoraImpostos:
    """Calculadora de impostos para diferentes regimes tributários"""

    @staticmethod
    def calcular_simples_nacional(receita_bruta, faturamento_anual=0):
        """
        Calcula impostos pelo Simples Nacional
        Baseado nas alíquotas da tabela 2024 (Anexo III - Serviços)
        
        Args:
            receita_bruta: Receita bruta mensal
            faturamento_anual: Faturamento acumulado no ano (para definir a alíquota)
        
        Returns:
            dict: Detalhamento dos impostos
        """
        # Tabela Simples Nacional 2024 - Anexo III (Serviços)
        # RBT12 (Receita Bruta acumulada nos 12 meses anteriores)
        if faturamento_anual <= 180000:
            aliquota = 0.06  # 6%
        elif faturamento_anual <= 360000:
            aliquota = 0.09  # 9%
        elif faturamento_anual <= 720000:
            aliquota = 0.105  # 10,5%
        elif faturamento_anual <= 1800000:
            aliquota = 0.14  # 14%
        elif faturamento_anual <= 3600000:
            aliquota = 0.16  # 16%
        elif faturamento_anual <= 4800000:
            aliquota = 0.19  # 19%
        else:
            aliquota = 0.207  # 20,7% (teto)

        # DAS (Documento de Arrecadação do Simples)
        das = receita_bruta * aliquota

        # ISS (Imposto Sobre Serviços) - geralmente 2-5% (média 3%)
        # No Simples, o ISS já está incluído no DAS, mas vamos detalhar
        iss = receita_bruta * 0.03

        # ICMS (Imposto sobre Circulação de Mercadorias) - para comércio
        # Para serviços, geralmente não aplica
        icms = 0

        return {
            'regime': 'Simples Nacional',
            'aliquota_efetiva': aliquota * 100,
            'das': das,
            'iss': iss,
            'icms': icms,
            'total_impostos': das,
            'descricao': f'Alíquota de {aliquota * 100:.1f}% sobre R$ {receita_bruta:,.2f}'
        }

    @staticmethod
    def calcular_lucro_presumido(receita_bruta, tipo_atividade='servicos'):
        """
        Calcula impostos pelo Lucro Presumido
        
        Args:
            receita_bruta: Receita bruta mensal
            tipo_atividade: 'servicos' ou 'comercio'
        
        Returns:
            dict: Detalhamento dos impostos
        """
        # Presunção de lucro
        if tipo_atividade == 'servicos':
            presuncao_lucro = 0.32  # 32% para serviços
            aliquota_pis_cofins = 0.0465  # 4,65% (PIS 0,65% + COFINS 4%)
        else:  # comercio
            presuncao_lucro = 0.08  # 8% para comércio
            aliquota_pis_cofins = 0.0925  # 9,25% (PIS 0,65% + COFINS 3% + ICMS 4-18%)
        
        # IRPJ (Imposto de Renda Pessoa Jurídica)
        # 15% sobre o lucro presumido + 10% sobre o excedente de R$ 20.000 mensais
        lucro_presumido = receita_bruta * presuncao_lucro
        irpj_base = lucro_presumido
        
        if irpj_base > 20000:
            irpj = (20000 * 0.15) + ((irpj_base - 20000) * 0.25)
        else:
            irpj = irpj_base * 0.15

        # CSLL (Contribuição Social sobre o Lucro Líquido)
        # 9% sobre o lucro presumido
        csll = lucro_presumido * 0.09

        # PIS e COFINS
        pis_cofins = receita_bruta * aliquota_pis_cofins

        # ISS (para serviços) - geralmente 2-5%
        if tipo_atividade == 'servicos':
            iss = receita_bruta * 0.03
            icms = 0
        else:
            iss = 0
            # ICMS varia por estado (4-18%), usando média 12%
            icms = receita_bruta * 0.12

        total_impostos = irpj + csll + pis_cofins + iss + icms

        return {
            'regime': 'Lucro Presumido',
            'presuncao_lucro': presuncao_lucro * 100,
            'irpj': irpj,
            'csll': csll,
            'pis_cofins': pis_cofins,
            'iss': iss,
            'icms': icms,
            'total_impostos': total_impostos,
            'descricao': f'Presunção de {presuncao_lucro * 100:.0f}% sobre R$ {receita_bruta:,.2f}'
        }

    @staticmethod
    def calcular_lucro_real(receita_bruta, custos, despesas):
        """
        Calcula impostos pelo Lucro Real
        
        Args:
            receita_bruta: Receita bruta mensal
            custos: Total de custos operacionais
            despesas: Total de despesas operacionais
        
        Returns:
            dict: Detalhamento dos impostos
        """
        # Lucro real = Receita - Custos - Despesas
        lucro_real = receita_bruta - custos - despesas

        # Se houver prejuízo, não paga IRPJ e CSLL
        if lucro_real <= 0:
            irpj = 0
            csll = 0
        else:
            # IRPJ: 15% sobre o lucro real + 10% sobre excedente de R$ 20.000
            if lucro_real > 20000:
                irpj = (20000 * 0.15) + ((lucro_real - 20000) * 0.25)
            else:
                irpj = lucro_real * 0.15

            # CSLL: 9% sobre o lucro real
            csll = lucro_real * 0.09

        # PIS e COFINS - cumulativo (1,65% + 7,6% = 9,25%)
        pis_cofins = receita_bruta * 0.0925

        # ISS (média 3% para serviços)
        iss = receita_bruta * 0.03

        # ICMS (média 12% para comércio)
        icms = receita_bruta * 0.12

        total_impostos = irpj + csll + pis_cofins + iss + icms

        return {
            'regime': 'Lucro Real',
            'lucro_real': lucro_real,
            'irpj': irpj,
            'csll': csll,
            'pis_cofins': pis_cofins,
            'iss': iss,
            'icms': icms,
            'total_impostos': total_impostos,
            'descricao': f'Lucro real de R$ {lucro_real:,.2f} sobre R$ {receita_bruta:,.2f}'
        }

    @staticmethod
    def calcular_impostos(receita_bruta, regime, custos=0, despesas=0, faturamento_anual=0, tipo_atividade='servicos'):
        """
        Calcula impostos baseado no regime tributário
        
        Args:
            receita_bruta: Receita bruta mensal
            regime: 'simples', 'presumido' ou 'real'
            custos: Total de custos (para lucro real)
            despesas: Total de despesas (para lucro real)
            faturamento_anual: Faturamento acumulado (para simples)
            tipo_atividade: 'servicos' ou 'comercio' (para presumido)
        
        Returns:
            dict: Detalhamento dos impostos
        """
        if regime == 'simples':
            return CalculadoraImpostos.calcular_simples_nacional(receita_bruta, faturamento_anual)
        elif regime == 'presumido':
            return CalculadoraImpostos.calcular_lucro_presumido(receita_bruta, tipo_atividade)
        elif regime == 'real':
            return CalculadoraImpostos.calcular_lucro_real(receita_bruta, custos, despesas)
        else:
            raise ValueError(f"Regime tributário inválido: {regime}")


# Função auxiliar para uso rápido
def calcular_impostos_auto(receita_bruta, regime, **kwargs):
    """Função de conveniência para calcular impostos"""
    calc = CalculadoraImpostos()
    return calc.calcular_impostos(receita_bruta, regime, **kwargs)
