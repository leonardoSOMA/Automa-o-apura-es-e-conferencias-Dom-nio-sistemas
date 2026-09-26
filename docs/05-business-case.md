# 05 · Business case

O modelo completo, com fórmulas editáveis, está na aba *Business Case* do
[kit da Fase 0](../fase0/Kit_Fase0_Diagnostico.xlsx). Os valores abaixo são **estimativas iniciais**. Substitua-os
pelo baseline medido na Fase 0.

## Premissas iniciais

| Premissa | Valor | Origem |
|---|---|---|
| Analistas no fiscal | 12 | Informado por você |
| Custo médio por analista (salário + encargos + benefícios) | R$ 5.500/mês | Estimativa: trocar pela média real da folha |
| Horas produtivas por analista | 140/mês | 21 dias × 8 h × 83% |
| Analista de automação/dados | R$ 7.500/mês | Estimativa: se for alguém realocado, usar o custo da pessoa |
| Ferramentas (captura, workflow, BI, eventual auditoria de prateleira) | R$ 2.500/mês | Cotar na Fase 0 |
| Infraestrutura (servidor/nuvem, banco, backup) | R$ 800/mês | Estimativa |
| APIs e IA (Integra Contador, Claude) | R$ 800/mês | O Integra Contador custa cerca de R$ 2 por cliente do Simples/mês na 1ª faixa |
| Implantação (consultoria/desenvolvimento da fundação) | R$ 40.000, diluídos em 4 meses | Estimativa |
| Rampa do ganho | 10% (meses 1–3), 40% (4–6), 70% (7–9), 100% (10 em diante) | Acompanha as fases |

## Onde está o tempo e quanto pode ser automatizado em 12 meses

| Etapa | % do tempo (estimado) | Conservador | Base | Otimista |
|---|---|---|---|---|
| 1. Coleta e cobrança de documentos | 14% | 35% | 50% | 65% |
| 2. Importação e escrituração | 32% | 18% | 25% | 35% |
| 3. Conferência e auditoria | 11% | 30% | 45% | 55% |
| 4. Apuração e guias | 12% | 15% | 25% | 35% |
| 5. Obrigações acessórias | 12% | 10% | 15% | 20% |
| 6. Atendimento e envio ao cliente | 11% | 20% | 30% | 40% |
| 7. Outros | 8% | 0% | 0% | 0% |
| **Ganho ponderado** | 100% | **19,2%** | **28,1%** | **37,4%** |

Não há benchmark independente para esses percentuais: os números de mercado são de fornecedores. O potencial em
escrituração é moderado porque a importação de XML já existe na Domínio. O ganho maior vem de captura, conferência e
retrabalho evitado.

## Resultado

| Cenário | Capacidade liberada | Economia bruta anual* | Custo anual do ecossistema | Resultado líquido anual* | Maior exposição de caixa | Payback |
|---|---|---|---|---|---|---|
| Conservador | 2,3 FTE | R$ 151,7 mil | R$ 139,2 mil | R$ 12,5 mil | −R$ 98,9 mil (mês 9) | acima de 24 meses |
| **Base** | **3,4 FTE** | **R$ 222,2 mil** | **R$ 139,2 mil** | **R$ 83,0 mil** | **−R$ 81,8 mil (mês 6)** | **21º mês** |
| Otimista | 4,5 FTE | R$ 295,8 mil | R$ 139,2 mil | R$ 156,6 mil | −R$ 72,6 mil (mês 6) | 14º mês |

\* Em regime pleno, a partir do 10º mês, **se a capacidade liberada for convertida**.

## O que esses números dizem

1. **O projeto se paga no cenário base, mas não é dinheiro fácil.** O conservador praticamente empata. Por isso
   existem os go/no-go por fase: os custos só crescem depois que o piloto prova o ganho.
2. **Capacidade liberada não é economia automática.** Ela vira resultado de três formas:
   - **não repor desligamentos:** com a rotatividade típica do fiscal, 2 a 3 saídas por ano bastam para chegar a
     −3 FTE em 12 a 18 meses, sem demissões;
   - **crescer sem contratar:** 3,4 FTE absorvem cerca de 28% mais empresas;
   - **vender serviços novos:** recuperação de PIS/COFINS monofásico (AUD-C05), revisão anual de regime, consultoria
     da Reforma.
3. **As alavancas que mais mexem no resultado** (teste na planilha):
   - custo real por analista;
   - realocar alguém interno como analista de automação;
   - negociar ferramentas;
   - receita de serviços novos. Cada R$ 3 mil/mês de receita nova adiciona R$ 36 mil/ano.

## Benefícios fora da conta

- Menos multas, juros e retificações pagos por erro.
- Menor risco profissional: há evidência de conferência em todas as empresas, todo mês.
- Fechamento mais cedo e cliente informado antes do vencimento.
- Base de dados para planejamento tributário e para a transição da Reforma (2027–2032). Sem automação, essa
  transição tende a exigir mais gente.
