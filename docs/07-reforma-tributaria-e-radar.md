# 07 · Reforma tributária e radar legislativo

> A pesquisa foi feita em 26/09/2026 em fontes oficiais e na imprensa especializada (lista no fim). Algumas páginas
> oficiais não puderam ser abertas diretamente, e parte das informações vem de resumos que coincidem entre duas ou mais
> fontes. **Confirme o texto legal antes de agir.**

## Linha do tempo (EC 132/2023 e LC 214/2025)

| Quando | O que acontece | Impacto no ecossistema |
|---|---|---|
| 2026 | Ano-teste. CBS de 0,9% e IBS de 0,1% são informados nos documentos, com caráter informativo. O recolhimento é dispensado para quem cumpre as obrigações acessórias. Simples e MEI ficam fora do teste. | Capturar e auditar os grupos IBS/CBS (AUD-C11) |
| 03/08/2026 | Grupos IBS/CBS obrigatórios em NF-e, NFC-e, CT-e, CT-e OS, MDF-e e NF3e (Ato Conjunto RFB/CGIBS 4/2026) | A SEFAZ não rejeita a falta do grupo (rejeição suspensa, sem data). Só a auditoria detecta. |
| 01/10/2026 | IBS/CBS obrigatório na NFS-e, sem rejeição até 31/12/2026 | Mesma regra para serviços |
| 01/11/2026 | ME/EPP do Simples passam a emitir NFS-e pelo Emissor Nacional (Res. CGSN 191/2026) | A captura de NFS-e dos clientes do Simples pelo ADN fica quase completa |
| 31/12/2026 | Programa Nacional de Conformidade Tributária (PNCT): corrigir inconsistências e indicar o contador responsável (Ato Conjunto RFB/CGIBS 5/2026) | Painel com a evolução de documentos corretos por cliente |
| 01/01/2027 | Mudanças: veja a lista abaixo da tabela. | PIS/COFINS só para 2026 e revisões retroativas. Regras de CBS com vigência. Apuração assistida × escrituração (AUD-E05). |
| 2029 a 2032 | ICMS e ISS caem para 9/10, 8/10, 7/10 e 6/10 das alíquotas, e o IBS sobe | Dupla apuração e tabelas com vigência. Sem automação, mais trabalho por empresa. |
| 2033 | ICMS e ISS extintos | — |

**O que muda em 01/01/2027:**

- A CBS passa a ser cobrada pela alíquota de referência, reduzida em 0,1 ponto em 2027 e 2028.
- O IBS fica em 0,1% (0,05% estadual e 0,05% municipal).
- PIS/COFINS são extintos.
- O IPI é zerado, exceto para produtos incentivados da Zona Franca de Manaus.
- Começa o Imposto Seletivo.
- Os campos IBS/CBS passam a ser obrigatórios para o Simples.
- A alíquota de referência da CBS depende do TCU (até 30/10) e de resolução do Senado (até 15/12/2026).

A **apuração assistida** da CBS roda em teste na Plataforma CBS durante 2026. A Receita anunciou APIs de débitos,
créditos, pagamentos e DARF a partir de outubro/2026. O efeito financeiro começa em 2027.

## Simples Nacional: IBS/CBS fora do DAS

**A regra**

- O optante pode recolher IBS/CBS pelo regime regular, fora do DAS. Assim os clientes pessoa jurídica aproveitam o
  crédito integral.
- **Janela para o 1º semestre de 2027:** de 01 a 30/09/2026, no Portal do Simples Nacional (Res. CGSN 186/2026).
  - A opção vale por semestre e não pode ser desfeita dentro dele.
  - Pode ser cancelada até 30/11/2026. Esse prazo pode ser prorrogado por causa da alíquota da CBS.
- A Res. CGSN 190/2026 exclui da receita bruta do Simples o IBS/CBS pago fora do DAS, a partir de 01/01/2027.
- **Próxima janela (2º semestre de 2027):** noticiada para março/2027. Uma fonte cita abril. Confirmar.

**Uso no ecossistema**

- Antes de cada janela, simular por cliente a partir do hub: vendas a pessoa jurídica, margens e créditos.
- Registrar a opção no cadastro mestre, que é conferido pela AUD-F01.

## Outras mudanças de 2026 que entram nas regras

| Norma | O que muda | Regra |
|---|---|---|
| LC 224/2025, IN RFB 2.305/2025 e IN RFB 2.306/2026 | Veja a lista abaixo da tabela. | AUD-D04, AUD-D05 |
| Lei 15.270/2025 | IRRF de 10% quando a mesma empresa paga mais de R$ 50 mil de lucros no mês à mesma pessoa física. Isenção de IRPF até R$ 5 mil/mês e IRPF mínimo para altas rendas. A aplicação ao Simples é discutida na Justiça. | AUD-D10 |
| NT EFD-Reinf 02/2026 | Lucros e dividendos informados no R-4010 (natureza 12001) | AUD-D10 |
| IN RFB 2.237/2024 e IN RFB 2.248/2025 | A DCTFWeb com MIT substitui a DCTF desde 2025. Prazo: último dia útil do mês seguinte. | AUD-E01, AUD-E03 |

**O que muda com a LC 224/2025:**

- **Lucro Presumido:** os percentuais de presunção sobem 10% sobre a receita que passar de R$ 5 mi/ano
  (R$ 1,25 mi por trimestre).
  - IRPJ desde 01/01/2026.
  - CSLL desde 01/04/2026.
  - Há liminares que suspendem o aumento para alguns contribuintes.
- **Benefícios federais:** redução linear. Por exemplo, operações com alíquota zero de PIS/COFINS passam a ter
  alíquota reduzida.
- **JCP:** o IRRF sobe para 17,5%.

## Radar mensal

- **Dono:** coordenador fiscal (dono das regras), 1 hora por mês.
- **Fontes:** Receita Federal, CGIBS, Portal NF-e (notas técnicas), Portal NFS-e, CGSN, SEFAZ das UFs dos clientes e
  informativos da Domínio.
- **Saída:**
  1. Lista de mudanças.
  2. Backlog de regras: novas, alteradas ou com vigência encerrada.
  3. Registro no repositório.

## Fontes consultadas (26/09/2026)

**Reforma e documentos fiscais**
- Receita Federal: flexibilização dos campos IBS/CBS nos documentos (jul/2026). https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/julho/receita-federal-e-cgibs-flexibilizarao-obrigatoriedade-de-informacoes-em-documentos-fiscais
- Contábeis: rejeição 1115 adiada. https://www.contabeis.com.br/noticias/79337/nf-e-rejeicao-1115-de-ibs-e-cbs-adiada-mas-obrigacao-permanece
- Machado Meyer: cronograma dos documentos eletrônicos com IBS/CBS. https://www.machadomeyer.com.br/pt/inteligencia-juridica/publicacoes-ij/tributario-ij/rfb-e-cgibs-definem-cronograma-oficial-de-obrigatoriedade-dos-documentos-fiscais-eletronicos-com-ibs-e-cbs
- Receita Federal: PNCT (ago/2026). https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/agosto/receita-federal-e-cgibs-regulamentam-programa-nacional-de-conformidade-tributaria-para-apoiar-adaptacao-a-reforma-tributaria-no-ano-de-2026
- Ministério da Fazenda: APIs de apuração da CBS (set/2026). https://www.gov.br/fazenda/pt-br/assuntos/noticias/2026/setembro/receita-federal-publica-nova-documentacao-tecnica-das-apis-de-apuracao-de-cbs
- Portal NF-e: notas técnicas. https://www.nfe.fazenda.gov.br/portal/listaConteudo.aspx?tipoConteudo=04BIflQt1aY%3D

**Simples Nacional**
- Receita Federal: prazos de opção (Res. CGSN 186/2026). https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/abril/cgsn-define-prazos-de-opcao-pelo-simples-nacional-e-pelo-regime-regular-do-ibs-e-da-cbs-para-2027
- Receita Federal: Res. CGSN 190/2026. https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/agosto/cgsn-atualiza-regras-do-simples-nacional-para-adequacao-a-reforma-tributaria-do-consumo
- Receita Federal: NFS-e nacional para ME/EPP a partir de 01/11/2026. https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/agosto/simples-nacional-nfs-e-nacional-sera-obrigatoria-para-me-e-epp-a-partir-de-1o-de-novembro-de-2026

**Lucro Presumido, dividendos e declarações**
- Contábeis: IN 2.306/2026 e o Lucro Presumido. https://www.contabeis.com.br/artigos/76669/in-2-306-altera-calculo-no-lucro-presumido/
- Demarest: LC 224/2025. https://www.demarest.com.br/en/lei-complementar-no-224-2025-reducao-de-beneficios-fiscais-e-tributacao-de-jcp-fintechs-e-bets/
- Lei 15.270/2025. https://www2.camara.leg.br/legin/fed/lei/2025/lei-15270-26-novembro-2025-798354-publicacaooriginal-177117-pl.html
- Receita Federal: MIT na DCTFWeb. https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2024/dezembro/publicada-instrucao-normativa-que-institui-o-modulo-de-inclusao-de-tributos-2013-mit-na-dctfweb-e-substitui-a-dctf

**APIs e integrações**
- ADN, manual das APIs para contribuintes. https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/documentacao-atual/manual-contribuintes-apis-adn-sistema-nacional-nfse.pdf
- SERPRO, Integra Contador. https://apicenter.estaleiro.serpro.gov.br/documentacao/api-integra-contador/
- Thomson Reuters, Onvio BR Accounting API. https://developerportal.thomsonreuters.com/onvio-br-accounting-api
- Domínio, Kolossus Auditor. https://www.dominiosistemas.com.br/solucoes/kolossus-auditor/
