# 00 · Sumário executivo

> **Atualização 26/09/2026:** a visão passou a ser um agente de IA que opera a Domínio e fecha o mês das empresas
> menores, com a equipe só aprovando. Veja [09 · Agente fiscal autônomo](09-agente-fiscal-autonomo.md). Este sumário
> descreve a versão 1.

**Plano diretor de automação do departamento fiscal · versão 1.0 · 26/09/2026**

## O problema

- O fiscal concentra 12 das 32 pessoas do escritório. A maior parte do tempo vai para coletar documentos,
  importar, conferir, apurar, transmitir e enviar guias.
- A auditoria das apurações é parcial e manual. Um erro de CFOP, uma nota faltante ou uma segregação esquecida
  no Simples pode chegar ao cliente e ao fisco sem ser visto.
- A Reforma Tributária aumenta a carga de trabalho. Em 2027 a CBS entra de verdade e o PIS/COFINS acaba. De 2029 a 2032,
  ICMS/ISS e IBS convivem. Sem automação, a transição tende a exigir **mais** gente no fiscal, e não menos.

## A tese: gestão por exceção

Hoje o analista olha tudo. No modelo proposto:

1. **Robôs** capturam 100% dos documentos e cruzam tudo, todo mês.
2. **O analista** trabalha só o que o motor de regras aponta como divergente.
3. **O revisor** aprova o que é crítico (empresas classe A e achados de risco alto).

O ganho vem de três lugares: menos coleta e digitação, conferência feita por regra em vez de olho, e menos
retrabalho, porque o erro é pego antes do fechamento.

## O que a pesquisa mostrou sobre a Domínio Web (setembro/2026)

| Fato | Consequência para o plano |
|---|---|
| A Domínio Web é o programa desktop transmitido pelo navegador (GraphOn). Robô de tela só enxerga a imagem. | Robô de tela é frágil e **não** deve ser a base do ecossistema. |
| Existe **API oficial de entrada** (Onvio BR Accounting API): envia XML de NF-e, NFC-e, NFS-e, CT-e e CF-e para a Escrita Fiscal, com importação agendada. | A captura pode alimentar a Domínio sem digitação e sem robô. |
| **Não existe API de leitura.** Fornecedores de BI restauram os **backups do banco** num servidor próprio e leem via ODBC. | É o caminho para auditar a escrituração inteira. Precisa do aval da TR. Plano B: arquivos EFD e relatórios em Excel. |
| Há auditoria nativa paga (**Kolossus Auditor**) e workflow (**Domínio Processos**, ex-Gestta). | Fazer POC antes de construir o que já existe integrado. |

## Recomendação: ecossistema híbrido

1. **Comprar o que é commodity:** captura de XML de um parceiro homologado da API Domínio. Se a POC provar
   cobertura, também a auditoria XML × SPED de prateleira.
2. **Usar as portas oficiais:** API da Domínio para a entrada, Integra Contador (SERPRO) para a Receita Federal,
   ADN para a NFS-e e Distribuição DF-e para a SEFAZ.
3. **Construir o que é diferencial:**
   - hub de dados do escritório;
   - apuração-sombra (Simples, Presumido, ICMS);
   - cruzamento declarado × apurado × pago;
   - semáforo de importação;
   - painel de fechamento.
4. **Mudar o processo e as pessoas:**
   - núcleo de automação (dono das regras + analista de automação);
   - esteira de fechamento D+n;
   - classes de empresa A/B/C com profundidade de revisão diferente.

## Números (estimativas a validar na Fase 0)

| Cenário | Ganho de produtividade | Capacidade liberada (de 12) | Resultado líquido anual em regime pleno | Payback |
|---|---|---|---|---|
| Conservador | 19% | 2,3 FTE | R$ 12,5 mil | acima de 24 meses |
| **Base** | **28%** | **3,4 FTE** | **R$ 83 mil** | **21º mês** |
| Otimista | 37% | 4,5 FTE | R$ 157 mil | 14º mês |

**Premissas:**

- custo médio de R$ 5.500/mês por analista;
- custos do ecossistema de R$ 11,6 mil/mês (analista de automação, ferramentas, infraestrutura, APIs);
- R$ 40 mil de implantação;
- ganho em rampa ao longo de 12 meses.

Não existe benchmark independente de ganho em escritórios contábeis: os percentuais publicados são de
fornecedores. Por isso a Fase 0 mede o ponto de partida e o piloto mede o ganho real antes de aumentar custos.

**A economia só vira caixa se a capacidade liberada for convertida:**

- não repor desligamentos (rotatividade natural);
- absorver novos clientes sem contratar;
- vender serviços novos: recuperação de PIS/COFINS monofásico, revisão de regime, consultoria da Reforma.

Ficam fora da conta: menos multas e retificações, menor risco profissional e fechamento mais cedo.

## Roadmap

| Fase | Período | Foco |
|---|---|---|
| 0 · Diagnóstico | 28/09 a 23/10/2026 | Baseline, cadastro mestre, reuniões com TR e SERPRO, POCs, decisões |
| 1 · Fundação | nov a dez/2026 | Captura, hub, 16 regras (completude, CFOP/CST, Simples, IBS/CBS), painel v1 |
| 2 · Virada da CBS | jan a abr/2027 | Entrada via API com semáforo, apuração-sombra, declarado × pago, apuração assistida da CBS |
| 3 · Escala | mai a dez/2027 | IA assistiva, regras complexas (ST, PIS/COFINS retroativo), analítica, robô pontual |
| 4 · Expansão | 2028 em diante | Contábil, DP, transição ICMS/ISS → IBS (2029–2032) |

## Alertas com prazo (confirmar nas fontes oficiais)

| Data | O quê |
|---|---|
| **30/09/2026** | Fim da janela para o optante do Simples escolher IBS/CBS fora do DAS no 1º semestre de 2027. A opção pode ser cancelada até 30/11/2026. |
| 01/11/2026 | ME/EPP do Simples passam a emitir NFS-e pelo Emissor Nacional. |
| 15/12/2026 | Prazo para fixar a alíquota de referência da CBS de 2027. |
| 31/12/2026 | Programa Nacional de Conformidade Tributária (PNCT): corrigir inconsistências de IBS/CBS nos documentos e indicar o contador responsável. |

## Decisões pedidas aos sócios

1. **Quem executa:** analista de automação interno realocado, contratado, ou consultoria para a fundação.
2. **O que comprar e o que construir:** captura e auditoria de prateleira × desenvolvimento próprio.
3. **Onde roda:** servidor no escritório × nuvem.
4. **Política de pessoas:** redução por não reposição × realocação para consultoria.
5. **Orçamento da Fase 1** e critério de continuidade (go/no-go) depois do piloto.
