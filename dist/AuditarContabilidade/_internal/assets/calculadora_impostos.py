"""
Calculadora de Impostos Brasileiros
Implementa cálculos para Simples Nacional, Lucro Presumido e Lucro Real
"""

class CalculadoraImpostos:
    """Calculadora de impostos para diferentes regimes tributários"""

    # Tabelas do Simples Nacional 2024
    TABELA_ANEXO_I_COMERCIO = {
        1: {'faixa_anual': 180_000, 'aliquota': 0.04, 'parcela_deduzir': 0},
        2: {'faixa_anual': 360_000, 'aliquota': 0.073, 'parcela_deduzir': 5_940},
        3: {'faixa_anual': 720_000, 'aliquota': 0.095, 'parcela_deduzir': 13_860},
        4: {'faixa_anual': 1_800_000, 'aliquota': 0.107, 'parcela_deduzir': 22_500},
        5: {'faixa_anual': 3_600_000, 'aliquota': 0.143, 'parcela_deduzir': 87_300},
        6: {'faixa_anual': 4_800_000, 'aliquota': 0.19, 'parcela_deduzir': 378_000},
    }

    TABELA_ANEXO_III_SERVICOS = {
        1: {'faixa_anual': 180_000, 'aliquota': 0.06, 'parcela_deduzir': 0},
        2: {'faixa_anual': 360_000, 'aliquota': 0.112, 'parcela_deduzir': 9_360},
        3: {'faixa_anual': 720_000, 'aliquota': 0.135, 'parcela_deduzir': 17_640},
        4: {'faixa_anual': 1_800_000, 'aliquota': 0.16, 'parcela_deduzir': 35_640},
        5: {'faixa_anual': 3_600_000, 'aliquota': 0.21, 'parcela_deduzir': 125_640},
        6: {'faixa_anual': 4_800_000, 'aliquota': 0.33, 'parcela_deduzir': 648_000},
    }

    @staticmethod
    def calcular_simples_nacional(receita_bruta, faturamento_anual=0, tipo_atividade='comercio'):
        """
        Calcula impostos pelo Simples Nacional
        Baseado nas alíquotas da tabela 2024 com parcela a deduzir

        Args:
            receita_bruta: Receita bruta mensal
            faturamento_anual: Faturamento acumulado no ano (para definir a alíquota)
            tipo_atividade: 'comercio' (Anexo I) ou 'servicos' (Anexo III)

        Returns:
            dict: Detalhamento dos impostos
        """
        # Se faturamento_anual não fornecido, estimar com base na receita mensal
        if faturamento_anual == 0:
            faturamento_anual = receita_bruta * 12

        # Escolher a tabela correta baseada no tipo de atividade
        if tipo_atividade == 'comercio':
            tabela = CalculadoraImpostos.TABELA_ANEXO_I_COMERCIO
        else:  # servicos
            tabela = CalculadoraImpostos.TABELA_ANEXO_III_SERVICOS

        # Encontrar a faixa correta
        faixa_encontrada = None
        num_faixa = 0
        for num, dados in tabela.items():
            if faturamento_anual <= dados['faixa_anual']:
                faixa_encontrada = dados
                num_faixa = num
                break

        # Se a receita for muito alta (última faixa), pega a última faixa
        if faixa_encontrada is None:
            faixa_encontrada = list(tabela.values())[-1]
            num_faixa = list(tabela.keys())[-1]

        # Calcular o DAS Mensal com a fórmula correta
        aliquota = faixa_encontrada['aliquota']
        # Converte a parcela a deduzir ANUAL para mensal
        parcela_deduzir_mensal = faixa_encontrada['parcela_deduzir'] / 12

        valor_das = (receita_bruta * aliquota) - parcela_deduzir_mensal

        # Garante que o valor não seja negativo
        valor_das = max(0, valor_das)

        # Detalhamento dos impostos incluídos no DAS
        # Para comércio: ICMS está incluído, para serviços: ISS está incluído
        if tipo_atividade == 'comercio':
            icms_estimado = valor_das * 0.4  # Aproximadamente 40% do DAS é ICMS
            iss = 0
        else:
            iss = valor_das * 0.3  # Aproximadamente 30% do DAS é ISS
            icms_estimado = 0

        return {
            'regime': 'Simples Nacional',
            'faixa': num_faixa,
            'aliquota_nominal': aliquota * 100,
            'parcela_deduzir_anual': faixa_encontrada['parcela_deduzir'],
            'parcela_deduzir_mensal': parcela_deduzir_mensal,
            'das': valor_das,
            'iss': iss,
            'icms': icms_estimado,
            'total_impostos': valor_das,
            'descricao': f'Faixa {num_faixa}: {aliquota * 100:.1f}% - R$ {parcela_deduzir_mensal:.2f} dedução mensal'
        }

    @staticmethod
    def calcular_lucro_presumido(receita_bruta, tipo_atividade='servicos'):
        """
        Calcula impostos pelo Lucro Presumido
        Baseado nas regras da Receita Federal

        Args:
            receita_bruta: Receita bruta mensal
            tipo_atividade: 'servicos', 'comercio', 'industria' ou 'transporte'

        Returns:
            dict: Detalhamento dos impostos
        """
        # Definir percentuais de presunção por tipo de atividade
        presuncoes = {
            'servicos': {'irpj': 0.32, 'csll': 0.32},      # Serviços
            'comercio': {'irpj': 0.08, 'csll': 0.12},      # Comércio
            'industria': {'irpj': 0.08, 'csll': 0.12},     # Indústria
            'transporte': {'irpj': 0.16, 'csll': 0.16}     # Transporte
        }

        pres = presuncoes.get(tipo_atividade, presuncoes['servicos'])

        # Calcular bases de cálculo
        base_irpj = receita_bruta * pres['irpj']
        base_csll = receita_bruta * pres['csll']

        # Calcular IRPJ: 15% sobre a base
        irpj = base_irpj * 0.15
        # Adicional de IRPJ (10% sobre o excedente de R$ 20.000/mês)
        if base_irpj > 20000:
            irpj += (base_irpj - 20000) * 0.10

        # Calcular CSLL: 9% sobre a base
        csll = base_csll * 0.09

        # PIS: 0,65% sobre receita bruta
        pis = receita_bruta * 0.0065

        # COFINS: 3% sobre receita bruta
        cofins = receita_bruta * 0.03

        # ISS (para serviços) - geralmente 2-5% - informativo, não entra no total federal
        if tipo_atividade == 'servicos':
            iss = receita_bruta * 0.03
            icms = 0
        else:
            iss = 0
            # ICMS varia por estado (4-18%), usando média 12% - informativo
            icms = receita_bruta * 0.12

        # Total de impostos federais (IRPJ + CSLL + PIS + COFINS) - conforme expectativa do usuário
        total_impostos = irpj + csll + pis + cofins

        return {
            'regime': 'Lucro Presumido',
            'tipo_atividade': tipo_atividade,
            'presuncao_irpj': pres['irpj'] * 100,
            'presuncao_csll': pres['csll'] * 100,
            'base_irpj': base_irpj,
            'base_csll': base_csll,
            'irpj': irpj,
            'csll': csll,
            'pis': pis,
            'cofins': cofins,
            'pis_cofins': pis + cofins,
            'iss': iss,
            'icms': icms,
            'total_impostos': total_impostos,
            'descricao': f'Presunção IRPJ: {pres["irpj"]*100:.0f}% | CSLL: {pres["csll"]*100:.0f}%'
        }

    @staticmethod
    def calcular_lucro_real(receita_bruta, custos, despesas):
        """
        Calcula impostos pelo Lucro Real
        Baseado nas regras da Receita Federal

        Args:
            receita_bruta: Receita bruta mensal
            custos: Total de custos operacionais
            despesas: Total de despesas operacionais

        Returns:
            dict: Detalhamento dos impostos
        """
        # Calcular o lucro líquido (base de cálculo)
        lucro_liquido = receita_bruta - custos - despesas

        # Se prejuízo, a base é zero para cálculo
        base_calculo = max(0, lucro_liquido)

        # Calcular IRPJ: 15% sobre a base
        irpj = base_calculo * 0.15
        # Adicional de 10% sobre lucro acima de R$ 20.000/mês
        if base_calculo > 20000:
            irpj += (base_calculo - 20000) * 0.10

        # Calcular CSLL: 9% sobre a base
        csll = base_calculo * 0.09

        # PIS: 0,65% sobre receita bruta
        pis = receita_bruta * 0.0065

        # COFINS: 3% sobre receita bruta
        cofins = receita_bruta * 0.03

        # ISS (média 3% para serviços) - informativo, não entra no total federal
        iss = receita_bruta * 0.03

        # ICMS (média 12% para comércio) - informativo, não entra no total federal
        icms = receita_bruta * 0.12

        # Total de impostos sobre o lucro (IRPJ + CSLL) - conforme expectativa do usuário
        total_impostos = irpj + csll

        return {
            'regime': 'Lucro Real',
            'lucro_liquido': lucro_liquido,
            'base_calculo': base_calculo,
            'irpj': irpj,
            'csll': csll,
            'pis': pis,
            'cofins': cofins,
            'pis_cofins': pis + cofins,
            'iss': iss,
            'icms': icms,
            'total_impostos': total_impostos,
            'descricao': f'Lucro Líquido: R$ {lucro_liquido:,.2f} | Base Cálculo: R$ {base_calculo:,.2f}'
        }

    @staticmethod
    def calcular_impostos(receita_bruta, regime, custos=0, despesas=0, faturamento_anual=0, tipo_atividade='comercio'):
        """
        Calcula impostos baseado no regime tributário

        Args:
            receita_bruta: Receita bruta mensal
            regime: 'simples', 'presumido' ou 'real'
            custos: Total de custos (para lucro real)
            despesas: Total de despesas (para lucro real)
            faturamento_anual: Faturamento acumulado (para simples)
            tipo_atividade: 'comercio' ou 'servicos' (para simples e presumido)

        Returns:
            dict: Detalhamento dos impostos
        """
        if regime == 'simples':
            return CalculadoraImpostos.calcular_simples_nacional(receita_bruta, faturamento_anual, tipo_atividade)
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
