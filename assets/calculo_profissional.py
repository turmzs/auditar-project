"""
Módulo de Cálculo Profissional de Impostos
Implementa memória de cálculo, créditos e DRE
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json


@dataclass
class MemoriaCalculoItem:
    """Item de memória de cálculo para um imposto específico"""
    imposto: str
    base_calculo: float
    aliquota: float
    valor_debito: float
    valor_credito: float
    valor_total: float
    detalhamento: Dict = field(default_factory=dict)


@dataclass
class ResultadoImpostos:
    """Resultado completo do cálculo de impostos"""
    regime: str
    mes: int
    ano: int
    
    # Receita e Lucro
    receita_bruta: float = 0
    receita_liquida: float = 0
    custos: float = 0
    despesas: float = 0
    lucro_real: float = 0
    
    # Impostos sobre Lucro
    irpj: float = 0
    csll: float = 0
    subtotal_lucro: float = 0
    
    # Impostos sobre Faturamento
    pis_debito: float = 0
    pis_credito: float = 0
    pis_total: float = 0
    cofins_debito: float = 0
    cofins_credito: float = 0
    cofins_total: float = 0
    
    # ICMS
    icms_saida: float = 0
    icms_entrada: float = 0
    icms_total: float = 0
    
    # ISS (serviços)
    iss: float = 0
    
    # Totais
    total_impostos: float = 0
    lucro_liquido: float = 0
    
    # Memória de cálculo
    memoria: List[MemoriaCalculoItem] = field(default_factory=list)
    
    # Prejuízo compensado
    prejuizo_compensado: float = 0
    base_irpj_apos_compensacao: float = 0


class CalculoProfissional:
    """Calculadora profissional com memória de cálculo"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager
    
    def calcular_lucro_real_profissional(
        self,
        empresa_id: int,
        mes: int,
        ano: int,
        receita_bruta: float,
        custos: float,
        despesas: float,
        creditos_pis: float = 0,
        creditos_cofins: float = 0,
        icms_saida: float = 0,
        icms_entrada: float = 0,
        prejuizo_a_compensar: float = 0,
        tipo_atividade: str = 'servicos'
    ) -> ResultadoImpostos:
        """
        Cálculo profissional de Lucro Real com memória detalhada
        """
        resultado = ResultadoImpostos(
            regime='Lucro Real',
            mes=mes,
            ano=ano,
            receita_bruta=receita_bruta,
            custos=custos,
            despesas=despesas
        )
        
        # 1. CALCULAR IMPOSTOS SOBRE FATURAMENTO PRIMEIRO
        # Esses impostos são deduções para chegar no Lucro Real
        
        # PIS: 1,65% sobre receita
        resultado.pis_debito = receita_bruta * 0.0165
        resultado.pis_credito = creditos_pis
        resultado.pis_total = max(0, resultado.pis_debito - resultado.pis_credito)
        
        memoria_pis = MemoriaCalculoItem(
            imposto='PIS',
            base_calculo=receita_bruta,
            aliquota=1.65,
            valor_debito=resultado.pis_debito,
            valor_credito=resultado.pis_credito,
            valor_total=resultado.pis_total,
            detalhamento={
                'regime': 'nao_cumulativo',
                'deducao_lucro_real': 'Sim - imposto deduzido antes do lucro'
            }
        )
        resultado.memoria.append(memoria_pis)
        
        # COFINS: 7,6% sobre receita
        resultado.cofins_debito = receita_bruta * 0.076
        resultado.cofins_credito = creditos_cofins
        resultado.cofins_total = max(0, resultado.cofins_debito - resultado.cofins_credito)
        
        memoria_cofins = MemoriaCalculoItem(
            imposto='COFINS',
            base_calculo=receita_bruta,
            aliquota=7.6,
            valor_debito=resultado.cofins_debito,
            valor_credito=resultado.cofins_credito,
            valor_total=resultado.cofins_total,
            detalhamento={
                'regime': 'nao_cumulativo',
                'deducao_lucro_real': 'Sim - imposto deduzido antes do lucro'
            }
        )
        resultado.memoria.append(memoria_cofins)
        
        # ICMS (apenas comércio/indústria - NÃO aplica com ISS)
        if tipo_atividade in ['comercio', 'industria', 'transporte']:
            resultado.icms_saida = icms_saida
            resultado.icms_entrada = icms_entrada
            resultado.icms_total = max(0, icms_saida - icms_entrada)
            
            memoria_icms = MemoriaCalculoItem(
                imposto='ICMS',
                base_calculo=receita_bruta,
                aliquota=12.0,
                valor_debito=icms_saida,
                valor_credito=icms_entrada,
                valor_total=resultado.icms_total,
                detalhamento={
                    'tipo': 'comercio/industria',
                    'metodo': 'credito_entrada',
                    'deducao_lucro_real': 'Sim - imposto deduzido antes do lucro',
                    'observacao': 'ISS não aplicado - ICMS é imposto estadual sobre produtos'
                }
            )
            resultado.memoria.append(memoria_icms)
        else:
            # Serviços: ICMS = 0
            resultado.icms_saida = 0
            resultado.icms_entrada = 0
            resultado.icms_total = 0
        
        # ISS (apenas serviços - NÃO aplica com ICMS)
        if tipo_atividade == 'servicos':
            resultado.iss = receita_bruta * 0.03
            memoria_iss = MemoriaCalculoItem(
                imposto='ISS',
                base_calculo=receita_bruta,
                aliquota=3.0,
                valor_debito=resultado.iss,
                valor_credito=0,
                valor_total=resultado.iss,
                detalhamento={
                    'tipo': 'municipal',
                    'deducao_lucro_real': 'Sim - imposto deduzido antes do lucro',
                    'observacao': 'ICMS não aplicado - ISS é imposto municipal sobre serviços'
                }
            )
            resultado.memoria.append(memoria_iss)
        else:
            # Comércio/Indústria: ISS = 0
            resultado.iss = 0
        
        # 2. CALCULAR LUCRO REAL (deduzindo impostos operacionais)
        # Lucro Real = Receita - Impostos_Faturamento - Custos - Despesas
        impostos_faturamento = resultado.pis_total + resultado.cofins_total + resultado.icms_total + resultado.iss
        lucro_real = receita_bruta - impostos_faturamento - custos - despesas
        
        # 🔒 Trava: lucro não pode ser negativo
        resultado.lucro_real = max(0, lucro_real)
        base_calculo = resultado.lucro_real
        
        # 3. RECEITA LÍQUIDA (para DRE)
        resultado.receita_liquida = receita_bruta - impostos_faturamento
        
        # 4. IMPOSTOS SOBRE LUCRO (IRPJ/CSLL)
        # Compensação de prejuízo (limite 30% do lucro do período)
        limite_compensacao = base_calculo * 0.30
        prejuizo_utilizado = min(prejuizo_a_compensar, limite_compensacao)
        base_irpj_apos_compensacao = base_calculo - prejuizo_utilizado
        
        resultado.prejuizo_compensado = prejuizo_utilizado
        resultado.base_irpj_apos_compensacao = base_irpj_apos_compensacao
        
        # 🔒 Trava: se lucro <= 0, não há IRPJ/CSLL
        irpj_normal = 0
        irpj_adicional = 0
        if base_calculo <= 0:
            resultado.irpj = 0
            resultado.csll = 0
            resultado.subtotal_lucro = 0
        else:
            # IRPJ: 15% + adicional 10% acima de R$ 60.000 (trimestral)
            irpj_normal = base_irpj_apos_compensacao * 0.15
            irpj_adicional = 0
            if base_irpj_apos_compensacao > 60000:
                irpj_adicional = (base_irpj_apos_compensacao - 60000) * 0.10
            resultado.irpj = irpj_normal + irpj_adicional
            
            # CSLL: 9% (sem compensação de prejuízo)
            resultado.csll = base_calculo * 0.09
            resultado.subtotal_lucro = resultado.irpj + resultado.csll
        
        # Memória IRPJ
        if base_calculo <= 0:
            memoria_irpj = MemoriaCalculoItem(
                imposto='IRPJ',
                base_calculo=0,
                aliquota=15.0,
                valor_debito=0,
                valor_credito=0,
                valor_total=0,
                detalhamento={
                    'observacao': '⚠️ Não houve IRPJ - Lucro Real menor ou igual a zero',
                    'base_lucro': base_calculo
                }
            )
        else:
            memoria_irpj = MemoriaCalculoItem(
                imposto='IRPJ',
                base_calculo=base_irpj_apos_compensacao,
                aliquota=15.0,
                valor_debito=resultado.irpj,
                valor_credito=0,
                valor_total=resultado.irpj,
                detalhamento={
                    'base_original': base_calculo,
                    'prejuizo_compensado': prejuizo_utilizado,
                    'irpj_normal': irpj_normal,
                    'irpj_adicional': irpj_adicional,
                    'limite_30': limite_compensacao,
                    'observacao': 'Base já deduziu impostos operacionais (PIS/COFINS/ICMS/ISS)'
                }
            )
        resultado.memoria.append(memoria_irpj)
        
        # Memória CSLL
        if base_calculo <= 0:
            memoria_csll = MemoriaCalculoItem(
                imposto='CSLL',
                base_calculo=0,
                aliquota=9.0,
                valor_debito=0,
                valor_credito=0,
                valor_total=0,
                detalhamento={
                    'observacao': '⚠️ Não houve CSLL - Lucro Real menor ou igual a zero',
                    'base_lucro': base_calculo
                }
            )
        else:
            memoria_csll = MemoriaCalculoItem(
                imposto='CSLL',
                base_calculo=base_calculo,
                aliquota=9.0,
                valor_debito=resultado.csll,
                valor_credito=0,
                valor_total=resultado.csll,
                detalhamento={
                    'base_lucro': base_calculo,
                    'observacao': 'Base já deduziu impostos operacionais (PIS/COFINS/ICMS/ISS)'
                }
            )
        resultado.memoria.append(memoria_csll)
        
        # 5. TOTAIS (com travas de impostos negativos)
        resultado.pis_total = max(0, resultado.pis_total)
        resultado.cofins_total = max(0, resultado.cofins_total)
        resultado.icms_total = max(0, resultado.icms_total)
        resultado.iss = max(0, resultado.iss)
        resultado.irpj = max(0, resultado.irpj)
        resultado.csll = max(0, resultado.csll)
        
        resultado.total_impostos = (
            resultado.subtotal_lucro +
            resultado.pis_total +
            resultado.cofins_total +
            resultado.icms_total +
            resultado.iss
        )
        
        # 🔒 Trava: lucro líquido não pode ser negativo
        resultado.lucro_liquido = max(0, lucro_real - resultado.subtotal_lucro)
        
        return resultado
    
    def gerar_dre(self, resultado: ResultadoImpostos) -> str:
        """
        Gera Demonstração do Resultado do Exercício (DRE)
        """
        dre = f"""
═══════════════════════════════════════════════════════════════
         DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO (DRE)
                    {resultado.mes:02d}/{resultado.ano}
═══════════════════════════════════════════════════════════════

RECEITA BRUTA                                            R$ {resultado.receita_bruta:>15,.2f}
(-) Impostos sobre Faturamento:
    PIS                                                R$ {resultado.pis_total:>15,.2f}
    COFINS                                             R$ {resultado.cofins_total:>15,.2f}
    ICMS                                               R$ {resultado.icms_total:>15,.2f}
    ISS                                                R$ {resultado.iss:>15,.2f}
                                                        ─────────────────────
(=) RECEITA LÍQUIDA                                      R$ {resultado.receita_liquida:>15,.2f}

(-) CUSTOS OPERACIONAIS                                  R$ {resultado.custos:>15,.2f}
(-) DESPESAS OPERACIONAIS                                R$ {resultado.despesas:>15,.2f}
                                                        ─────────────────────
(=) LUCRO REAL (BASE DE CÁLCULO)                         R$ {resultado.lucro_real:>15,.2f}

(-) IMPOSTOS SOBRE O LUCRO:
    IRPJ                                               R$ {resultado.irpj:>15,.2f}
    CSLL                                               R$ {resultado.csll:>15,.2f}
                                                        ─────────────────────
(=) LUCRO LÍQUIDO DO PERÍODO                             R$ {resultado.lucro_liquido:>15,.2f}

═══════════════════════════════════════════════════════════════
RESUMO DE IMPOSTOS:
  Sobre Faturamento:  R$ {(resultado.pis_total + resultado.cofins_total + resultado.icms_total + resultado.iss):>15,.2f}
  Sobre Lucro:        R$ {resultado.subtotal_lucro:>15,.2f}
  ─────────────────────────────────────────
  TOTAL GERAL:       R$ {resultado.total_impostos:>15,.2f}
═══════════════════════════════════════════════════════════════
"""
        return dre
    
    def gerar_memoria_calculo(self, resultado: ResultadoImpostos) -> str:
        """
        Gera memória de cálculo detalhada
        """
        memoria_texto = f"""
═══════════════════════════════════════════════════════════════
              MEMÓRIA DE CÁLCULO DETALHADA
                 {resultado.regime} - {resultado.mes:02d}/{resultado.ano}
═══════════════════════════════════════════════════════════════

"""
        
        for item in resultado.memoria:
            memoria_texto += f"""
┌─────────────────────────────────────────────────────────────┐
│ {item.imposto:^59} │
├─────────────────────────────────────────────────────────────┤
│ Base de Cálculo:      R$ {item.base_calculo:>15,.2f}              │
│ Alíquota:             {item.aliquota:>15.2f}%                      │
├─────────────────────────────────────────────────────────────┤
│ DÉBITO:               R$ {item.valor_debito:>15,.2f}              │
│ CRÉDITO:              R$ {item.valor_credito:>15,.2f}              │
├─────────────────────────────────────────────────────────────┤
│ TOTAL A PAGAR:        R$ {item.valor_total:>15,.2f}              │
└─────────────────────────────────────────────────────────────┘
"""
            
            # Adicionar detalhamento se existir
            if item.detalhamento:
                memoria_texto += "\n  Detalhamento:\n"
                for chave, valor in item.detalhamento.items():
                    if isinstance(valor, float):
                        memoria_texto += f"    • {chave}: R$ {valor:,.2f}\n"
                    else:
                        memoria_texto += f"    • {chave}: {valor}\n"
                memoria_texto += "\n"
        
        # Resumo de compensações
        if resultado.prejuizo_compensado > 0:
            memoria_texto += f"""
┌─────────────────────────────────────────────────────────────┐
│ COMPENSAÇÃO DE PREJUÍZO FISCAL                              │
├─────────────────────────────────────────────────────────────┤
│ Prejuízo Compensado:  R$ {resultado.prejuizo_compensado:>15,.2f}              │
│ Base IRPJ Original:   R$ {resultado.lucro_real:>15,.2f}              │
│ Base IRPJ Após Comp.: R$ {resultado.base_irpj_apos_compensacao:>15,.2f}              │
│ Limite Aplicado (30%): Utilizado                            │
└─────────────────────────────────────────────────────────────┘
"""
        
        memoria_texto += f"""
═══════════════════════════════════════════════════════════════
                    TOTAL DE IMPOSTOS: R$ {resultado.total_impostos:>15,.2f}
═══════════════════════════════════════════════════════════════
"""
        return memoria_texto


# Função auxiliar para salvar resultado no banco
def salvar_resultado_calculo(db_manager, empresa_id: int, resultado: ResultadoImpostos):
    """Salva o resultado do cálculo e a memória no banco de dados"""
    if db_manager is None:
        return
    
    # Salvar memória de cálculo para cada imposto
    for item in resultado.memoria:
        detalhamento_json = json.dumps(item.detalhamento, ensure_ascii=False)
        db_manager.execute('''
            INSERT INTO memoria_calculo 
            (empresa_id, mes, ano, regime, tipo_imposto, base_calculo, aliquota, 
             valor_debito, valor_credito, valor_total, detalhamento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            empresa_id, resultado.mes, resultado.ano, resultado.regime,
            item.imposto, item.base_calculo, item.aliquota,
            item.valor_debito, item.valor_credito, item.valor_total,
            detalhamento_json
        ))
