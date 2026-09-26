# 01 · Documentos do mês

**Objetivo:** ter todos os documentos fiscais da competência numa pasta, antes de tocar na Domínio.

## Onde buscar
Cada fonte ainda precisa ser confirmada:

- **NF-e de entrada.** [MAPEAR] Onde a captura deixa os XML hoje. Pode ser uma ferramenta de captura, uma pasta de rede
  ou download manual.
- **NF-e/NFC-e de saída.** [MAPEAR] XML enviado pelo cliente (Acessórias, e-mail ou ERP), ou notas com o CNPJ do
  escritório no autXML.
- **NFS-e prestadas e tomadas**, que são o documento principal das prestadoras de serviço.
  - Desde 01/11/2026 as ME/EPP do Simples emitem pelo Emissor Nacional, então as notas estão no Ambiente de Dados
    Nacional (ADN).
  - [MAPEAR] Como o escritório baixa hoje: portal, captura ou Domínio.
  - Resumo das NFS-e: `python ferramentas/nfse.py resumo <pasta> --cnpj <CNPJ>` (serviços por código, ISS retido,
    município de incidência, retenções).
- **Outros.** [MAPEAR] CT-e, contas de consumo, documentos sem XML.

## Passo a passo
1. Copie os arquivos para `trabalho/<AAAA-MM>/<codigo>/xml/entradas`, `.../saidas` e `.../servicos`.
2. Rode o resumo:
   ```
   python ferramentas/nfe.py resumo trabalho/<AAAA-MM>/<codigo>/xml --cnpj <CNPJ da empresa> --competencia <AAAA-MM> --saida trabalho/<AAAA-MM>/<codigo>/documentos.json
   ```
   O resumo separa as notas em entradas e saídas pelo CNPJ da empresa. Ele mostra quantidade, valor total, canceladas
   e notas fora da competência.
3. Compare com a média dos 3 meses anteriores, lendo os `documentos.json` antigos quando existirem.

## Quando parar
- Nenhuma nota de saída em empresa que costuma faturar, ou volume abaixo de 50% da média. Peça a cobrança ao
  cliente e não siga.
- XML ilegível, de outra empresa ou de outra competência.

## Evidência
`documentos.json` e uma linha no `log.md` com as quantidades e os totais.
