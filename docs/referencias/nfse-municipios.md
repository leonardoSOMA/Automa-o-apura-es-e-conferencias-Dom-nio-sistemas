# NFS-e nos municípios da carteira: de onde vêm as notas

Levantamento de 26/09/2026. Os sites das prefeituras e dos fornecedores não abriram daqui. As informações vêm de:
- trechos de busca;
- da tabela de municípios e provedores do projeto ACBr (atualizada em 23/09/2026);
- do XSD oficial da NFS-e;
- de clientes abertos da API nacional.

Por isso cada linha tem um grau de confiança, e o agente **testa cada rota no primeiro uso**.

## Por município

| | Três Corações | São Thomé das Letras | Varginha |
|---|---|---|---|
| Código IBGE | 3169307 | 3165206 | 3170701 |
| Sistema hoje | Próprio: **E&L "el-nfse"**. Web service SOAP no estilo ABRASF 1.0, com login e senha. | **Emissor Nacional** | **Betha e-Nota Cloud**, que já aceita o leiaute nacional |
| Desde | E&L pelo menos desde 2023. O MEI está no Emissor Nacional desde 2023. | ~01/01/2026 | Betha desde 11/2023; leiaute nacional entre 12/2025 e 01/2026 |
| Notas no ADN | **Não confirmado** | Sim | **Sim.** Há XML de 01/2026 com `ambGer=1` e `tpEmis=2`. |
| Rota do agente | Testar o ADN. Se as notas não estiverem lá: web service da E&L (só notas **prestadas**; não há consulta de tomadas) ou o portal | ADN | ADN |
| Confiança | Média no sistema, baixa no ADN | Média | Média-alta |

Portais: Três Corações em `pmtc.trescoracoes.mg.gov.br/el-nfse`, São Thomé em `nfse.gov.br/EmissorNacional`, Varginha em
`contribuinte.nota-eletronica.betha.cloud`.

## Datas que mudam a rota

| Data | O que muda | Base |
|---|---|---|
| 01/09/2023 | MEI emite pelo Emissor Nacional em todo o país | Obrigação nacional do MEI |
| 01/01/2026 | Municípios com sistema próprio precisam mandar as notas ao ADN | LC 214/2025, art. 62 |
| **01/11/2026** | **ME/EPP do Simples emitem pelo Emissor Nacional**, na web ou por API. Os sistemas municipais valem até 31/10/2026. | Res. CGSN 191/2026, que revogou a 189 |
| 01/01/2027 | Campos de IBS/CBS obrigatórios na NFS-e para o Simples | Ato Conjunto RFB/CGIBS nº 4/2026 |

- **Alíquotas-teste de 2026:** o Simples fica fora (LC 214/2025, art. 348, III, "c").
- **Consequência para o piloto:** a competência 10/2026, fechada em novembro, ainda tem notas de outubro emitidas no
  E&L de Três Corações. A partir das notas de novembro, as prestadoras do Simples dos três municípios estão todas no
  ADN, tanto as notas prestadas quanto as tomadas de quem compartilha.

## API do Ambiente de Dados Nacional (ADN)

- **Consulta:**
  - `GET https://adn.nfse.gov.br/contribuintes/DFe/{NSU}?cnpjConsulta={CNPJ}&lote=true`, com TLS mútuo e
    certificado ICP-Brasil.
  - Devolve lotes de até 50 documentos: NFS-e e eventos (cancelamento `e101101`, substituição `e105102`).
  - Traz as notas em que o CNPJ é prestador, tomador ou intermediário.
  - Erro `E2220`: não há mais documentos. HTTP 429: excesso de consultas, espere e tente de novo.
- **Certificado.**
  - Tem de ser o **da própria empresa**: A1, para rodar sem ninguém. O token A3 não funciona.
  - O `cnpjConsulta` precisa ter a mesma raiz do certificado, então um certificado serve para matriz e filiais.
  - **Não existe acesso por procuração nem com o certificado do escritório.**
- **Controle:** guarde o último NSU de cada CNPJ e consulte todo dia a partir dele.
- **Situação do município:** `GET https://adn.nfse.gov.br/parametrizacao/{cMun}/convenio` devolve
  `aderenteAmbienteNacional` e `situacaoEmissaoPadraoContribuintesRFB`. Conferir todo mês nos três códigos e avisar se
  mudar.
- **Regimes especiais e retenções do município:**
  - `/parametrizacao/{cMun}/{cServ}/{competencia}/regimes_especiais`;
  - `/parametrizacao/{cMun}/{cServ}/{competencia}/retencoes`.

  O regime especial 6 é "Sociedade de Profissionais".

## ISS

- **Alíquota:** entre 2% e 5% em Três Corações e Varginha, pela tabela nacional de alíquotas. São Thomé das Letras não
  aparece na base consultada. As leis municipais não foram conferidas.
- **Retenção pelo tomador:**
  - a lista nacional está na LC 116/2003, art. 6º, §2º;
  - listas municipais não foram conferidas;
  - para prestador do Simples, a retenção usa a alíquota efetiva do Simples (LC 123, art. 21, §4º).
- **ISS fixo dentro do Simples:**
  - escritório contábil (LC 123, art. 18, §22-A; atividade 9 no PGDAS-D), se a lei municipal prever;
  - valores fixos de ME (§18), também se a lei municipal prever.

  Não conferido nos três municípios.

## Domínio

- **Entrada oficial de XML:** a API Onvio BR Accounting (`POST https://api.onvio.com.br/dominio/invoice/v3/batches`,
  OAuth2 e chave de integração por empresa). A Domínio importa por "Importação API" ou pelas rotinas automáticas.
- **Leiaute da NFS-e Nacional: não confirmado.** Testar com um XML ou perguntar a api.dominio@tr.com antes de escalar.

## O que fazer

1. **Coletor do ADN:** um por cliente, com certificado A1 e controle de NSU, rodando todo dia. Guarda XML e eventos
   em `trabalho/`.
2. **Três Corações até 31/10/2026:** rodar o coletor numa prestadora e procurar notas com município 3169307 e
   `ambGer=1`. Se não vierem, usar o web service da E&L para as prestadas e tratar as tomadas como exceção.
3. **Certificado A1 de todas as prestadoras:** sem ele não há download automático.
4. **Testar a importação na Domínio** de um XML da NFS-e Nacional.

## Fontes

- Tabela de municípios e provedores do ACBr (commits de 21/11/2023 a 23/09/2026):
  https://github.com/MirrorProjetoACBr/ACBr/blob/master/Fontes/ACBrDFe/ACBrNFSeX/ACBrNFSeXServicos.ini
- XSD da NFS-e Nacional v1.01: https://github.com/claudio-mas/nfse_nacional
- WSDL da E&L: https://github.com/akretion/nfselib/blob/master/WSDL/Producao/PManhuacuMG-EL.wsdl
- Clientes do ADN: https://github.com/rafael-negrao/nfse-nacional-service e https://github.com/luizecs94/nfse_downloader
- Res. CGSN 191/2026: https://www.legisweb.com.br/legislacao/?id=499104 · Res. CGSN 189/2026:
  https://www.legisweb.com.br/legislacao/?id=494855
- Ato Conjunto RFB/CGIBS nº 4/2026: https://www.legisweb.com.br/legislacao/?id=498712
- LC 214/2025, art. 348: https://jurishand.com/lei-complementar-214-de-16-janeiro-2025/artigo-348/inciso-3/alinea-c
- Varginha (trechos): https://focusnfe.com.br/guides/nfse/municipios-integrados/varginha-mg/ e
  https://notagateway.com.br/blog/varginha-mg-inicia-migracao-da-nfs-e-e-iss-para-sistema-nacional-e-altera-canais-de-atendimento/
- Três Corações (trechos): https://nfe.io/docs/prefeituras-integradas/minas-gerais/tres-coracoes-mg-3169307/
- Integração com a Domínio (código aberto): https://github.com/tiagoistuque/IntegracaoDominioThomsomReuters
