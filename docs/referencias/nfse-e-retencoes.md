# NFS-e e retenções para optantes do Simples: referência do agente

Levantamento de 26/09/2026. Os XSD e o Anexo I da NFS-e Nacional foram lidos de cópias literais do pacote oficial. A
LC 123 foi lida de espelho do Planalto. O restante vem de busca, marcado com (M) quando a confiança é média.

## NFS-e Nacional (XSD 1.01, NT 007/2026)

Namespace `http://www.sped.fazenda.gov.br/nfse`. Legenda dos caminhos:
- `I` = `NFSe/infNFSe`
- `D` = `I/DPS/infDPS`

| Campo | Caminho |
|---|---|
| Número | `I/nNFSe` |
| Chave | `I/@Id` = "NFS" + 50 dígitos |
| Competência | `D/dCompet`, usada para o período do PGDAS-D |
| Prestador | `D/prest/CNPJ` (`I/emit` pode ser o tomador quando `tpEmit` = 2) |
| Simples | `D/prest/regTrib/opSimpNac`: 1 não optante, 2 MEI, 3 ME/EPP. `regApTribSN`: 1 tudo no SN, 2 ISS fora, 3 federais e ISS fora |
| Serviço | `D/serv/cServ/{cTribNac (6), cTribMun, cNBS, xDescServ}`. Os 4 primeiros dígitos do cTribNac são o subitem da LC 116. |
| Valor | `D/valores/vServPrest/vServ` |
| ISS | `I/valores/{vBC, pAliqAplic, vISSQN, vTotalRet, vLiq}` |
| Retenção de ISS | `tpRetISSQN`: 1 não retido, 2 tomador, 3 intermediário |
| Tributação do ISS | `tribISSQN`: 1 tributável, 2 imunidade, 3 exportação, 4 não incidência |
| Incidência | `I/cLocIncid` (ausente quando `tribISSQN` ≠ 1); local da prestação em `D/serv/locPrest/cLocPrestacao` |
| Retenções federais | `D/valores/trib/tribFed/{vRetCP, vRetIRRF, vRetCSLL}` |

- **Retenção de PIS, COFINS e CSLL:** desde a NT 007, o `vRetCSLL` traz a soma dos três. `vPis` e `vCofins` são débito
  próprio do prestador, não retenção.
- **CNAE:** não existe campo de CNAE na NFS-e Nacional.
- **Cancelamento:** chega em evento separado (`infPedReg/chNFSe` com `e101101`). A substituição usa `e105102`. Existem
  também `e105104` (deferido por análise fiscal) e `e305101` (de ofício).

## ABRASF 2.x

Namespace `http://www.abrasf.org.br/nfse.xsd`. Os campos principais:
- **Serviço:** `ItemListaServico` ("01.01"), `CodigoCnae` (inteiro de 7 dígitos, sem o zero à esquerda),
  `CodigoTributacaoMunicipio`, `CodigoNbs` (só na 2.04), `Discriminacao`, `MunicipioIncidencia`.
- **Valores:** `ValorServicos`, `ValorIss` e `Aliquota`.
  - A alíquota é percentual na 2.04 e fração na 1.0; nas 2.01/2.02 é ambígua, por isso a ferramenta normaliza.
- **Retenções:** `IssRetido` (1 sim, 2 não), `ValorIr`, `ValorCsll`, `ValorPis`, `ValorCofins`, `ValorInss`.
- **Exigibilidade:** `ExigibilidadeISS` (1 exigível, 2 não incidência, 3 isenção, 4 exportação, 5 imunidade, 6/7
  suspensa).
- **Simples:** `OptanteSimplesNacional` (1/2).
- **Cancelamento:** `CompNfse/NfseCancelamento`.
- Os leiautes municipais variam, e a ferramenta busca os campos pelo nome da tag.

## Regras para prestadoras do Simples

- **ISS retido** (LC 123, art. 21 §4º):
  - só cabe nos casos do art. 3º da LC 116;
  - a alíquota é a efetiva do ISS do mês anterior, informada na nota;
  - no primeiro mês de atividade, 2%;
  - sem informação na nota, 5%;
  - o ISS retido é definitivo (inciso VII).

  A receita precisa ser segregada no PGDAS-D como "com retenção/substituição tributária de ISS" (art. 18 §4º-A, II).
  Sem segregação, o ISS é pago duas vezes (AT-02).
- **ISS devido a outro município** (art. 18 §4º-A, V): é recolhido no Simples, com a opção "sem retenção, com ISS
  devido a outro(s) município(s)" e o município indicado (AT-03).
- **IRRF:** dispensado para optante (IN RFB 765/2007), salvo em aplicações financeiras.
- **PIS/COFINS/CSLL retidos (4,65%):** não se aplicam a pagamentos a optante (Lei 10.833/2003, art. 32).
- **INSS de 11%:** só para empresas do Anexo IV em cessão de mão de obra ou empreitada (IN RFB 2.110/2022, arts. 166 e
  167; dispensas consolidadas na IN RFB 2.289/2025) (M).
- **Na NFS-e Nacional**, `opSimpNac` = 3 com `vRetIRRF` ou `vRetCSLL` maior que zero indica retenção indevida (AT-05).
- **Anexo IV** (construção, vigilância, limpeza e conservação, advocacia): a CPP é paga fora do DAS, via eSocial,
  DCTFWeb e DARF (LC 123, art. 13, VI, e art. 18 §5º-C).
- **Vedações:** CNAE impeditivo ou ambíguo (Res. CGSN 140/2018, Anexos VI e VII) e cessão de mão de obra fora do Anexo
  IV (LC 123, art. 17, XII).

## Correlação serviço × CNAE

- **cTribNac → subitem da LC 116:** determinístico, pelos 4 primeiros dígitos.
- **CNAE ↔ LC 116:** não há tabela nacional oficial. Alguns municípios publicam a sua, como Salvador e Montes Claros.
- **NBS:** o Anexo VIII da NFS-e correlaciona LC 116 × NBS × cClassTrib. O NBS classifica o serviço, não a atividade,
  e só ajuda como indício.
- Por isso, na NFS-e Nacional, a atividade faturada é identificada pelo subitem e pela discriminação. A IA analítica
  faz essa leitura e o parecer registra a evidência.

## Fontes

- Documentação técnica da NFS-e Nacional: https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/documentacao-atual
- XSD e Anexo I em cópia: https://github.com/claudio-mas/nfse_nacional
- ABRASF 2.04: https://abrasf.org.br/biblioteca/arquivos-publicos/nfs-e/versao-2-04
- NT 007/2026 (TOTVS): https://www.totvs.com/blog/fiscal-clientes/nfs-e-nacional-nota-tecnica-no-007-2026-esclarece-pis-cofins-retencoes-e-atualiza-codigos-de-operacao/
- LC 123/2006: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm
- Manual do PGDAS-D: https://www8.receita.fazenda.gov.br/simplesnacional/arquivos/manual/manual_pgdas-d_2018_v4.pdf
- IN RFB 765/2007: http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=15713
- Lei 10.833/2003: https://www.planalto.gov.br/ccivil_03/leis/2003/l10.833compilado.htm
- CPP do Anexo IV (Receita): https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cobrancas-e-intimacoes/contribuicao-previdenciaria-anexo-iv-do-simples-nacional
- Anexo VIII (NBS × LC 116): https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/rtc/anexoviii-correlacaoitemnbsindopcclasstrib_ibscbs_v1-00-00.xlsx/view
