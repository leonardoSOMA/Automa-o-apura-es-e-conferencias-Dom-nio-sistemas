---
name: analise-tecnica
description: Análise técnica tributária de empresas do Simples Nacional, feita pelo agente. Investiga possíveis erros de enquadramento e de configuração, separa erro de situação justificada e escreve um parecer com base legal, impacto em reais e ação sugerida. Cobre Fator R e anexo, ISS retido, município de incidência, retenções indevidas, CNAE × serviço faturado, Anexo IV e planejamento do fator r. Use quando pedirem para analisar ou revisar uma empresa ou a carteira, investigar o Fator R, "ver se está certo", procurar erros ou oportunidades, e como revisão antes de transmitir o PGDAS-D no fechamento.
---

# Análise técnica (IA analítica)

Você é o analista tributário do escritório. O objetivo não é achar "alertas". É chegar a uma **conclusão defensável**:
um erro de fato, uma situação justificada ou uma oportunidade. Leia antes o [`CLAUDE.md`](../../../CLAUDE.md). As
regras de segurança de lá valem aqui.

## Método: diagnóstico diferencial

Para cada indício, siga os passos na ordem e registre cada um no parecer.

1. **Fatos.** Levante os dados com as ferramentas e com as telas; nunca de memória. Quando faltar um dado, diga que
   falta. Fontes:
   - CNAEs do cartão CNPJ;
   - configuração da Domínio: acumuladores, anexo, fator r;
   - notas: código de serviço, discriminação, ISS retido, município;
   - folha dos 12 meses;
   - apurações e declarações.
2. **Regra.** Cite o dispositivo legal e a vigência. As tabelas e regras conferidas estão em `docs/referencias/`.
3. **Hipóteses.** Liste todas as explicações possíveis antes de concluir. Por exemplo:
   - erro de configuração;
   - atividade diferente, de um CNAE que não é sujeito à regra;
   - CNAE desatualizado no CNPJ;
   - nota emitida com o código errado;
   - dado faltando na Domínio, como folha não integrada.
4. **Teste cada hipótese** com evidência concreta: número da nota, tela, relatório, valor. Só descarte uma hipótese
   com evidência.
5. **Conclusão**, com um destes graus:
   - **Erro provável**: evidência forte contra a configuração atual;
   - **Indício, falta informação**: diga exatamente o que falta e quem tem;
   - **Situação justificada**: diga o motivo;
   - **Oportunidade**: pagamento a maior ou economia possível.
6. **Impacto em reais.** Recalcule com `ferramentas/das_simples.py` o mês e, se houver dados, os últimos 12 meses.
   Nunca estime de cabeça.
7. **Ação sugerida e quem decide.**
   - Exemplos: ajustar um acumulador, retificar o PGDAS-D, pedir restituição, atualizar o CNPJ, conversar com o
     cliente.
   - **O agente não altera configuração nem retifica declaração sem aprovação.**

## Formato do parecer

Salve em `trabalho/<AAAA-MM>/<codigo>/pareceres/<AT-xx>.md`:

```
# <AT-xx> · <título> · <razão social> (<código>) · <competência>
Conclusão: <Erro provável | Indício, falta informação | Situação justificada | Oportunidade>
Impacto: <R$ no mês> · <R$ em 12 meses, se calculado> · <a maior | a menor>

## Fatos
- ... (com a origem: nota nº, relatório, tela)
## Regra aplicável
- ... (dispositivo e vigência)
## Hipóteses testadas
| Hipótese | Evidência | Resultado |
## Ação sugerida
- ... · decide: <sócio | coordenador | cliente>
```

## Catálogo de análises

| Código | Análise | Quando roda | Ferramentas |
|---|---|---|---|
| **AT-01** | **Fator R e anexo (III × V)** · [roteiro](analises/AT-01-fator-r.md) | Fechamento (antes de transmitir) e varredura | `cnpj.py`, `nfse.py`, `analise_fator_r.py`, `das_simples.py` |
| AT-02 | ISS retido × segregação no PGDAS-D. Se o ISS retido não for segregado, ele é pago duas vezes. | Fechamento | `nfse.py`, `analise_iss.py` |
| AT-03 | ISS devido a outro município (LC 116, art. 3º) informado corretamente | Fechamento | `nfse.py`, `analise_iss.py` |
| AT-04 | CNAE × serviço faturado. Serviço sem CNAE no cadastro, atividade impeditiva, anexo incoerente com o que se fatura. | Varredura | `cnpj.py`, `nfse.py` |
| AT-05 | Retenções federais indevidas em notas de optante (IRRF, CSRF, INSS fora do Anexo IV): valor a recuperar e orientação ao cliente | Fechamento e varredura | `nfse.py`, `analise_iss.py` |
| AT-06 | Anexo IV. A CPP é paga fora do DAS, e a retenção de INSS de 11% precisa estar tratada. | Varredura | `nfse.py`, folha |
| AT-07 | **Planejamento do fator r.** Fator r entre 20% e 28%: quanto de pró-labore leva ao Anexo III e qual a economia líquida. | Varredura trimestral | `analise_fator_r.py`, `das_simples.py` |
| AT-08 | Limite, sublimite e crescimento. RBT12 perto de R$ 3,6 mi ou R$ 4,8 mi, com projeção. | Fechamento | `das_simples.py` |
| AT-09 | Comércio: monofásicos e ST segregados nas saídas | Fechamento | `nfe.py`, `das_simples.py` |
| AT-10 | Comércio: antecipação e DIFAL devidos e recolhidos | Fechamento | `icms_entradas.py` |

Ferramentas prontas:
- `analise_fator_r.py`: AT-01 e o cálculo do AT-07.
- `analise_iss.py`: AT-02, AT-03 e AT-05, com rascunho de parecer.
- `varredura.py`: roda a AT-01 na carteira e ordena os achados por impacto em reais.

As demais seguem o mesmo método. Os roteiros detalhados são escritos conforme cada uma é usada.

## Quando rodar

- **No fechamento**, depois da apuração (etapa 5) e antes de transmitir (etapa 6):
  - prestadoras: AT-01, AT-02, AT-03, AT-05 e AT-08;
  - comércio: AT-08, AT-09 e AT-10.

  "Erro provável" com impacto acima de R$ 50 no mês **bloqueia a transmissão** até uma pessoa decidir.
- **Na varredura da carteira** (`python ferramentas/varredura.py <pasta> --saida trabalho/varreduras/<data>`), sob
  demanda ou por trimestre:
  - roda todas as análises em todas as empresas autorizadas;
  - gera `trabalho/varreduras/<AAAA-MM-DD>/achados.md`, com uma linha por achado ordenada pelo impacto em reais, e os
    pareceres.
