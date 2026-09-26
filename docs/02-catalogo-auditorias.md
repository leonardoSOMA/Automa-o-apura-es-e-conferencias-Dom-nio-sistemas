# 02 · Catálogo de auditorias (cruzamentos)

O catálogo é a lista do que o motor de regras verifica todo mês. São **46 regras** em 7 grupos, priorizadas em
4 fases. A mesma lista está em [`catalogo/auditorias.csv`](../catalogo/auditorias.csv) e na aba *Catálogo de
Auditorias* do [kit da Fase 0](../fase0/Kit_Fase0_Diagnostico.xlsx), onde dá para filtrar e acompanhar o status.

## Como ler

- **Risco:** impacto se o erro passar sem ser visto (autuação, crédito perdido, pagamento a maior, retrabalho).
- **Esforço:** complexidade para construir a regra (dados necessários, tabelas por UF, lógica).
- **Fase:** quando entra em produção (ver [04 · Roadmap](04-roadmap.md)).
- **Ação:**
  - *Bloqueia*: a competência não fecha com o achado aberto;
  - *Alerta*: vai para a fila do analista;
  - *Oportunidade*: gera lista de recuperação ou planejamento.
- **Prioridade** (na planilha): risco × 2 + (4 − esforço), de 3 a 9. Quanto maior, antes.

## Resumo

| Grupo | Fase 1 | Fase 2 | Fase 3 | Fase 4 | Total |
|---|---|---|---|---|---|
| A. Completude documental | 6 | 2 | 1 | – | 9 |
| B. Integridade de valores | 2 | 1 | 1 | – | 4 |
| C. Classificação fiscal | 4 | 2 | 5 | – | 11 |
| D. Apuração (recálculo-sombra) | 2 | 6 | 2 | – | 10 |
| E. Declarado × apurado × pago | – | 4 | 1 | – | 5 |
| F. Cadastro e situação fiscal | 2 | 1 | 1 | – | 4 |
| G. Analítica e indícios de risco | – | – | 2 | 1 | 3 |
| **Total** | **16** | **16** | **13** | **1** | **46** |

### Fase 1: as 16 regras da fundação (nov a dez/2026)

- **AUD-A01** NF-e de entrada não escrituradas (Todos; ação: bloqueia)
- **AUD-A02** Notas de saída não escrituradas (Todos; ação: bloqueia)
- **AUD-A03** Canceladas, denegadas e inutilizadas (Todos; ação: bloqueia)
- **AUD-A05** Lançamento em duplicidade (Todos; ação: bloqueia)
- **AUD-A06** NFS-e prestadas e tomadas não escrituradas (Todos; ação: bloqueia)
- **AUD-A09** "Sem movimento" com documentos (Todos; ação: bloqueia)
- **AUD-B01** Totais do documento divergentes (Todos; ação: bloqueia)
- **AUD-B02** Competência e datas (Todos; ação: alerta)
- **AUD-C01** CFOP de entrada incoerente (Todos; ação: bloqueia)
- **AUD-C02** CFOP × CST/CSOSN incoerentes (Todos; ação: bloqueia)
- **AUD-C05** Monofásicos de PIS/COFINS (SN, LP, LR; ação: oportunidade)
- **AUD-C11** Reforma: grupos IBS/CBS nos documentos (Todos; ação: alerta)
- **AUD-D01** Simples Nacional: recálculo do DAS (SN; ação: bloqueia)
- **AUD-D02** Simples Nacional: limite e sublimite (SN; ação: alerta)
- **AUD-F01** Regime tributário e CNAE (Todos; ação: bloqueia)
- **AUD-F02** Certificados e procurações a vencer (Todos; ação: alerta)

Critério da escolha: risco alto, esforço baixo ou médio, dados já disponíveis na captura ou na escrituração, e
urgência legal (IBS/CBS nos documentos antes do fim do PNCT, em 31/12/2026). A **AUD-C05** (monofásicos) entra cedo
porque aponta PIS/COFINS pago a maior por clientes do Simples nos últimos 5 anos. É uma recuperação que pode ajudar a
pagar o projeto.

## Regras por grupo

### A. Completude documental

| Código | Regra | O que verifica | Fontes cruzadas | Regimes | Risco | Esforço | Fase | Ação |
|---|---|---|---|---|---|---|---|---|
| AUD-A01 | NF-e de entrada não escrituradas | Toda NF-e emitida contra o CNPJ do cliente (Distribuição DF-e / manifestação) está escriturada na competência; lista faltantes. | XML (SEFAZ) × escrituração Domínio | Todos | Alto | Baixo | 1 | Bloqueia |
| AUD-A02 | Notas de saída não escrituradas | NF-e/NFC-e autorizadas do cliente × escrituração: faltantes, extras e total por dia/série. | XML emitidos (autXML/ERP/captura) × escrituração | Todos | Alto | Baixo | 1 | Bloqueia |
| AUD-A03 | Canceladas, denegadas e inutilizadas | Nota cancelada escriturada como normal, cancelamento posterior ao lançamento e inutilizações sem registro de situação. | Eventos SEFAZ × escrituração | Todos | Alto | Baixo | 1 | Bloqueia |
| AUD-A04 | Quebra de sequência numérica | Saltos na numeração das notas emitidas (por modelo/série) sem inutilização correspondente. | XML emitidos × eventos de inutilização | Todos | Médio | Baixo | 2 | Alerta |
| AUD-A05 | Lançamento em duplicidade | Mesma chave de acesso (ou emitente + número + série) escriturada mais de uma vez. | Escrituração Domínio | Todos | Alto | Baixo | 1 | Bloqueia |
| AUD-A06 | NFS-e prestadas e tomadas não escrituradas | NFS-e do Ambiente Nacional (API do ADN por NSU, com certificado) e de prefeituras que não compartilham × escrituração de serviços, com retenções. _Ref.: LC 214/2025, art. 62; Res. CGSN 191/2026._ | ADN / prefeituras × escrituração | Todos | Alto | Médio | 1 | Bloqueia |
| AUD-A07 | CT-e tomados não escriturados | CT-e em que o cliente é tomador × escrituração; vínculo CT-e ↔ NF-e (frete FOB) e crédito do frete. | XML CT-e × escrituração | Todos | Médio | Médio | 2 | Alerta |
| AUD-A08 | Notas não reconhecidas pelo cliente | NF-e contra o CNPJ sem manifestação ou de fornecedor atípico: possível nota fria ou operação não realizada. | Distribuição DF-e × manifestação × histórico de fornecedores | Todos | Médio | Médio | 3 | Alerta |
| AUD-A09 | "Sem movimento" com documentos | Empresa marcada sem movimento ou com apuração zerada, mas com XML emitido/recebido na competência. | Cadastro mestre × XML × apuração | Todos | Alto | Baixo | 1 | Bloqueia |

### B. Integridade de valores

| Código | Regra | O que verifica | Fontes cruzadas | Regimes | Risco | Esforço | Fase | Ação |
|---|---|---|---|---|---|---|---|---|
| AUD-B01 | Totais do documento divergentes | Valor contábil, BC e ICMS, BC e ICMS-ST, IPI, PIS, COFINS e FCP: XML × escrituração, por chave, com tolerância. | XML × escrituração (relatório/EFD C100-C190) | Todos | Alto | Baixo | 1 | Bloqueia |
| AUD-B02 | Competência e datas | Data de entrada/saída fora da competência; notas extemporâneas lançadas sem controle. | XML × escrituração | Todos | Médio | Baixo | 1 | Alerta |
| AUD-B03 | Participante divergente | CNPJ, IE e UF do participante no cadastro da Domínio × XML (afeta CFOP interno/interestadual e DIFAL). | XML × cadastro de participantes | Todos | Médio | Baixo | 2 | Alerta |
| AUD-B04 | Itens divergentes nas entradas | Quantidade, valor, NCM e CFOP por item: XML × registro de itens (EFD C170). | XML × EFD ICMS/IPI (C170) | LP, LR | Médio | Médio | 3 | Alerta |

### C. Classificação fiscal

| Código | Regra | O que verifica | Fontes cruzadas | Regimes | Risco | Esforço | Fase | Ação |
|---|---|---|---|---|---|---|---|---|
| AUD-C01 | CFOP de entrada incoerente | CFOP escriturado × CFOP do emitente e finalidade (ex.: 5405→1403/1407; 6102→2102/2556/2551; 5910→1910; 5202→1202) e 1º dígito × UF. _Ref.: Convênio s/nº 1970 (CFOP)._ | XML × escrituração × tabela de conversão | Todos | Alto | Médio | 1 | Bloqueia |
| AUD-C02 | CFOP × CST/CSOSN incoerentes | Ex.: 5405 com CST 00; CST 40/41 com ICMS destacado; CST 60 sem CFOP de ST; CSOSN em empresa do regime normal e CST em optante do Simples. | XML × escrituração × cadastro mestre | Todos | Alto | Baixo | 1 | Bloqueia |
| AUD-C03 | Crédito de ICMS indevido ou não aproveitado | Crédito em uso e consumo, ativo fora do CIAP (1/48), fornecedor do Simples sem pCredSN, entradas com ST/isentas; e créditos permitidos não aproveitados. _Ref.: LC 87/1996, arts. 20 e 33; LC 123/2006, art. 23._ | XML × escrituração × finalidade do item | LP, LR | Alto | Médio | 2 | Bloqueia |
| AUD-C04 | Créditos de PIS/COFINS não cumulativos | CST 50–56 nas entradas × natureza do item (insumo, revenda, ativo); monofásicos e alíquota zero sem crédito; coerência com EFD-Contribuições. _Ref.: Leis 10.637/2002 e 10.833/2003 (até 12/2026; revisão retroativa 5 anos)._ | XML × escrituração × EFD-Contribuições | LR | Alto | Alto | 3 | Alerta |
| AUD-C05 | Monofásicos de PIS/COFINS | NCM na lista de tributação concentrada × receita segregada no PGDAS-D (Simples) ou CST 04 nas saídas (LP/LR). Pagamento em duplicidade vira recuperação. _Ref.: Leis 10.147/2000, 10.485/2002, 13.097/2015; LC 123/2006, art. 18 §4º-A._ | XML (NCM) × tabela de monofásicos × PGDAS-D/escrituração | SN, LP, LR | Alto | Médio | 1 | Oportunidade |
| AUD-C06 | ICMS-ST: produto sujeito × tratamento | NCM/CEST sujeito à ST na UF × CST/CSOSN e segregação de receita com ST no Simples; ST não retida em compra interestadual. _Ref.: Convênios/protocolos ICMS e legislação da UF._ | XML × tabela ST por UF × escrituração/PGDAS-D | Todos | Alto | Alto | 3 | Alerta |
| AUD-C07 | DIFAL | Compras interestaduais para uso/consumo/ativo e vendas a não contribuinte de outra UF: DIFAL calculado e recolhido. _Ref.: EC 87/2015; LC 190/2022._ | XML × escrituração × guias | Todos | Alto | Médio | 2 | Alerta |
| AUD-C08 | Alíquota de IPI × TIPI | Indústrias e equiparadas: alíquota por NCM × TIPI vigente; crédito de IPI nas entradas. _Ref.: Decreto 11.158/2022 (TIPI) e alterações._ | XML × TIPI × escrituração | LP, LR | Médio | Médio | 3 | Alerta |
| AUD-C09 | NCM inválido ou incompatível | NCM inexistente/expirado ou incompatível com a descrição do produto (triagem assistida por IA, decisão humana). | XML × tabela NCM × IA | Todos | Médio | Médio | 3 | Alerta |
| AUD-C10 | Antecipação de ICMS (conforme UF) | Entradas interestaduais sujeitas à antecipação parcial/total × guia recolhida. _Ref.: Legislação da UF._ | XML × regra da UF × guias | Todos | Médio | Alto | 3 | Alerta |
| AUD-C11 | Reforma: grupos IBS/CBS nos documentos | CST IBS/CBS, cClassTrib, bases e alíquotas nos XML emitidos (obrigatório: NF-e/CT-e desde 03/08/2026, NFS-e desde 01/10/2026, Simples em 01/01/2027). A SEFAZ ainda não rejeita a falta do grupo: só a auditoria pega. _Ref.: LC 214/2025; Ato Conjunto RFB/CGIBS 4/2026; NT 2025.002-RTC._ | XML × tabelas da RTC × escrituração | Todos | Alto | Médio | 1 | Alerta |

### D. Apuração (recálculo-sombra)

| Código | Regra | O que verifica | Fontes cruzadas | Regimes | Risco | Esforço | Fase | Ação |
|---|---|---|---|---|---|---|---|---|
| AUD-D01 | Simples Nacional: recálculo do DAS | Recalcula RBT12, anexo, faixa, alíquota efetiva e repartição, com segregações (ST, monofásico, exportação, ISS retido) × Domínio × PGDAS-D. _Ref.: LC 123/2006; Res. CGSN 140/2018._ | Receitas × tabelas LC 123 × Domínio × PGDAS-D | SN | Alto | Médio | 1 | Bloqueia |
| AUD-D02 | Simples Nacional: limite e sublimite | Receita acumulada e RBT12 × sublimite (R$ 3,6 mi) e limite (R$ 4,8 mi); alerta preventivo a partir de 80%. _Ref.: LC 123/2006, arts. 3º e 13-A._ | Receitas 12 meses | SN | Alto | Baixo | 1 | Alerta |
| AUD-D03 | Simples Nacional: Fator R | Folha de 12 meses (salários, pró-labore, FGTS, CPP) ÷ RBT12 ≥ 28% define Anexo III × V; confere o anexo aplicado. _Ref.: LC 123/2006, art. 18 (fator r)._ | Domínio Folha × receitas × apuração | SN | Alto | Médio | 2 | Bloqueia |
| AUD-D04 | Lucro Presumido: IRPJ e CSLL | Base de presunção por atividade, acréscimo de 10% nos percentuais sobre a receita acima de R$ 5 mi/ano (R$ 1,25 mi/trimestre; IRPJ desde 01/2026, CSLL desde 04/2026), adicional de IRPJ e retenções compensadas. _Ref.: Lei 9.249/1995, arts. 15 e 20; LC 224/2025; IN RFB 2.305/2025 e 2.306/2026._ | Receitas por atividade × apuração Domínio × DCTFWeb/MIT | LP | Alto | Médio | 2 | Bloqueia |
| AUD-D05 | PIS/COFINS: débitos e créditos | Recalcula débitos (cumulativo 0,65%/3%; não cumulativo 1,65%/7,6%), exclusões e créditos × apuração × EFD-Contribuições, incluindo a redução de benefícios da LC 224/2025 (até 12/2026; depois, revisão retroativa). _Ref.: Leis 9.718/1998, 10.637/2002 e 10.833/2003; LC 224/2025._ | Escrituração × EFD-Contribuições | LP, LR | Alto | Médio | 3 | Alerta |
| AUD-D06 | ICMS regime normal: apuração | Recalcula débitos e créditos pelos documentos (C190) × apuração da Domínio (E110) × declaração estadual; saldo credor transportado. | EFD ICMS/IPI × apuração × GIA/declaração da UF | LP, LR | Alto | Médio | 2 | Bloqueia |
| AUD-D07 | ISS próprio e retido | ISS dos serviços prestados × alíquota e local de incidência; ISS retido por tomadores deduzido; ISS retido em serviços tomados recolhido. _Ref.: LC 116/2003, arts. 3º e 6º._ | NFS-e × escrituração × guias municipais | Todos | Médio | Médio | 2 | Alerta |
| AUD-D08 | Retenções federais e INSS | Serviços tomados e prestados com IRRF, CSRF (4,65%) e INSS (11%) × EFD-Reinf (R-2010/R-2020/R-4020) × DCTFWeb. _Ref.: Lei 10.833/2003, art. 30; Lei 8.212/1991, art. 31._ | NFS-e × escrituração × EFD-Reinf × DCTFWeb | Todos | Alto | Médio | 2 | Bloqueia |
| AUD-D09 | Carga tributária fora do padrão | Carga efetiva do mês (tributos ÷ receita) × média de 12 meses e faixa esperada do segmento. | Apurações × receitas (histórico) | Todos | Médio | Baixo | 3 | Alerta |
| AUD-D10 | Lucros e dividendos acima de R$ 50 mil/mês | Pagamentos de lucros à mesma pessoa física acima de R$ 50 mil no mês: IRRF de 10% retido × EFD-Reinf (R-4010) × DCTFWeb. Interface com contábil/DP. _Ref.: Lei 15.270/2025; NT EFD-Reinf 02/2026._ | Distribuições (contábil) × EFD-Reinf × DCTFWeb | Todos | Alto | Baixo | 2 | Alerta |

### E. Declarado × apurado × pago

| Código | Regra | O que verifica | Fontes cruzadas | Regimes | Risco | Esforço | Fase | Ação |
|---|---|---|---|---|---|---|---|---|
| AUD-E01 | Apuração × declaração transmitida | Valores da Domínio × PGDAS-D, DCTFWeb/MIT, EFD-Contribuições, EFD ICMS/IPI e declarações estaduais/municipais. | Domínio × Integra Contador × recibos | Todos | Alto | Médio | 2 | Bloqueia |
| AUD-E02 | Guia emitida × guia paga | DAS, DARF e guias estaduais/municipais emitidas × pagamentos localizados; aviso ao cliente antes do vencimento. | Guias × consulta de pagamentos (e-CAC) × conta corrente da UF | Todos | Alto | Médio | 2 | Alerta |
| AUD-E03 | Obrigações entregues no prazo | Matriz de obrigações de cada empresa × recibos de entrega; alerta 5 dias antes do vencimento. | Cadastro mestre × recibos | Todos | Alto | Baixo | 2 | Alerta |
| AUD-E04 | Parcelamentos em dia | Parcelas emitidas e pagas (Simples, federais e estaduais); risco de rescisão. | Integra Contador (parcelamentos) × pagamentos | Todos | Médio | Médio | 3 | Alerta |
| AUD-E05 | CBS: apuração assistida × escrituração | A partir de 2027, débitos e créditos da apuração assistida da Plataforma CBS (APIs da Receita) × escrituração da Domínio × hub. _Ref.: LC 214/2025._ | APIs da apuração da CBS × Domínio × hub | LP, LR | Alto | Médio | 2 | Bloqueia |

### F. Cadastro e situação fiscal

| Código | Regra | O que verifica | Fontes cruzadas | Regimes | Risco | Esforço | Fase | Ação |
|---|---|---|---|---|---|---|---|---|
| AUD-F01 | Regime tributário e CNAE | Regime cadastrado na Domínio × situação na Receita (optante do Simples/SIMEI) e opção semestral pelo IBS/CBS fora do DAS (a partir de 2027); CNAEs × atividades escrituradas e anexo usado. | Cadastro Domínio × consulta Receita | Todos | Alto | Baixo | 1 | Bloqueia |
| AUD-F02 | Certificados e procurações a vencer | Validade dos certificados A1 (clientes e escritório), procurações eletrônicas e acessos estaduais: alertas em 30, 15 e 5 dias. | Cofre de certificados × cadastro mestre | Todos | Alto | Baixo | 1 | Alerta |
| AUD-F03 | Situação fiscal e caixa postal | Pendências no relatório de situação fiscal, mensagens da Caixa Postal do e-CAC e DTE-SN, domicílios eletrônicos estaduais, termos de exclusão do Simples. | Integra Contador × portais da UF | Todos | Alto | Médio | 2 | Alerta |
| AUD-F04 | IE e situação de fornecedores | IE do cliente ativa e fornecedores relevantes inaptos/baixados (crédito glosável). | Cadastro × consulta de contribuintes (CCC/SINTEGRA) | LP, LR | Médio | Médio | 3 | Alerta |

### G. Analítica e indícios de risco

| Código | Regra | O que verifica | Fontes cruzadas | Regimes | Risco | Esforço | Fase | Ação |
|---|---|---|---|---|---|---|---|---|
| AUD-G01 | Variação atípica de receitas e compras | Variação do mês × média de 12 meses fora da faixa; queda brusca de faturamento; compras sem vendas no mês. | Histórico do hub de dados | Todos | Médio | Baixo | 3 | Alerta |
| AUD-G02 | Compras incompatíveis com receitas | Entradas maiores que saídas de forma recorrente no comércio (indício de omissão de receita ou estoque inflado). | Histórico do hub de dados | Todos | Médio | Baixo | 3 | Alerta |
| AUD-G03 | Fiscal × contábil | Faturamento do fiscal × receitas contábeis; tributos apurados × contas de tributos a recolher (quando expandir para o contábil). | Escrita Fiscal × Contabilidade | Todos | Médio | Médio | 4 | Alerta |

## Ficha-modelo de regra

Cada regra, ao ser construída, ganha uma ficha em `regras/<código>.md` com os campos abaixo, além do código e dos
casos de teste:

| Campo | Conteúdo |
|---|---|
| Código e nome | Ex.: AUD-C01 · CFOP de entrada incoerente |
| Objetivo | Qual erro a regra evita e qual o impacto |
| Base legal | Dispositivos e vigência |
| Fontes | Tabelas do hub e campos usados |
| Lógica | Passo a passo em português antes do código |
| Tolerância | Ex.: diferença até R$ 0,05 por documento |
| Severidade e ação | Bloqueia, alerta ou oportunidade; quem resolve |
| Exemplos | Pelo menos 1 caso que deve disparar e 1 que não deve, com dados reais anonimizados |
| Dono | Quem responde pelo conteúdo fiscal da regra |
| Vigência e versão | Datas de início/fim e histórico de mudanças |

## Ciclo de vida de uma regra

1. **Backlog.**
2. **Em especificação:** o dono fiscal preenche a ficha.
3. **Em desenvolvimento.**
4. **Modo sombra:** roda por 1 competência sem avisar ninguém e mede os falsos positivos.
5. **Em produção.**
6. **Revisão trimestral:** falsos positivos, mudanças de lei.

O status de cada regra é acompanhado na planilha.

## Usar o catálogo para avaliar ferramentas

Na POC de uma ferramenta de auditoria (Kolossus Auditor, e-Auditoria ou outra), marque cada regra como **coberta**,
**parcial** ou **não coberta**, usando as mesmas empresas-piloto. Depois construa só o que faltar. Isso evita pagar
duas vezes pela mesma função e evita construir o que já existe pronto e integrado à Domínio.
