# 03 · Esteira de fechamento e escrituração assistida

## A esteira mensal

D+n = dias úteis depois do fim do mês. Ajuste os marcos aos vencimentos de cada empresa: DAS no dia 20,
DCTFWeb/MIT no último dia útil do mês seguinte, ICMS conforme a UF.

| # | Etapa | Quando | O robô faz | A pessoa faz | Sai daqui quando |
|---|---|---|---|---|---|
| 1 | Captura | Contínua; fecha em D+3 | Baixa XML (SEFAZ, ADN, autXML), recebe documentos do portal e cobra o cliente pelo que falta (ex.: "sem nota de saída desde o dia 10") | Trata respostas do cliente | O volume capturado bate com o esperado para o cliente |
| 2 | Pré-auditoria de entrada | D+2 a D+4 | Regras de completude (grupo A), sem movimento, regime e certificados (F01, F02) | Resolve as exceções | Nenhum achado de completude que bloqueia |
| 3 | Semáforo e importação | D+3 a D+6 | Classifica cada documento em verde, amarelo ou vermelho e envia os verdes pela API. As Rotinas Automáticas importam na Domínio. | Aprova amarelos em lote e trata os vermelhos | 100% dos documentos importados |
| 4 | Auditoria da escrituração | D+6 a D+8 | Extrai a escrituração (backup ou EFD), roda os grupos B e C e reprocessa a cada correção | Corrige na Domínio ou justifica o que está certo | Zero achados críticos abertos |
| 5 | Apuração e recálculo-sombra | D+8 a D+10 | Compara a apuração da Domínio com a sombra (grupo D) | O analista apura. O revisor aprova a classe A e as divergências. | Divergência zero ou justificada |
| 6 | Declarações, guias e entrega | D+10 a D+12 | Transmite/consulta PGDAS-D e DCTFWeb (Integra Contador), confere declarado × apurado (E01) e monta o resumo do cliente | Aprova o pacote | Pacote entregue ao cliente |
| 7 | Pós-fechamento | Até o vencimento e D+30 | Confere pagamentos (E02), recibos (E03), caixa postal e situação fiscal (F03) e gera o dossiê | Trata pendências | Competência encerrada com dossiê |

## Semáforo de importação

A API da Domínio envia o XML e a *Configuração de Importação* decide acumulador e CFOP de entrada. O semáforo prevê,
**antes do envio**, se essa configuração vai acertar.

### Entradas

- **XML:** emitente, código do produto, NCM, CFOP de origem, CST/CSOSN, descrição e valores.
- **Perfil da empresa:** regime, atividade e UF.
- **Histórico** das classificações já feitas, extraído da Domínio.

### Camadas de decisão

1. **Regras determinísticas.** Família do CFOP (ST, devolução, remessa, bonificação), primeiro dígito × UF e
   CST/CSOSN × regime.
2. **Memória.** Mesmo fornecedor e mesmo produto já classificados antes: reutiliza a classificação (confiança alta).
3. **Semelhança.** Mesmo NCM no mesmo cliente: sugere (confiança média).
4. **IA.** A descrição do item indica a finalidade: revenda, insumo, uso e consumo ou ativo (confiança variável).

### Cores

| Cor | Critério | Destino |
|---|---|---|
| **Verde** | Confiança de 95% ou mais e a configuração da Domínio produz a mesma classificação | Envio pela API, sem revisão |
| **Amarelo** | Confiança entre 70% e 95%, ou o histórico diverge da configuração | Revisão rápida em lote, aprovar ou ajustar |
| **Vermelho** | Menos de 70%, fornecedor/produto novo ou CFOP atípico | Analista. Pode seguir por TXT com classificação explícita, se o leiaute permitir. |

**Metas de lançamento sem intervenção:** 60% dos documentos em verde em 6 meses e 80% em 12 meses.

**Aprendizado:**

- Toda correção do analista vira memória, com autor e data.
- Padrões que se repetem viram ajuste da Configuração de Importação na empresa-modelo, e a correção passa a valer
  para todos os clientes.

**Exemplo:**

1. Um fornecedor emite CFOP 5102 para um cliente comerciante. O item é material de limpeza (uso e consumo).
2. A configuração padrão converteria para 1102 (compra para comercialização). O certo é 1556.
3. O semáforo vê que esse fornecedor e esse produto foram escriturados como 1556 nos últimos meses e marca o documento
   em amarelo.
4. Resultado: evita o erro e, no regime normal, o crédito indevido de ICMS.

## Gestão por exceção

- **Filas por analista** no painel: achados abertos por severidade, idade e empresa.
- **Prazos:**
  - achados críticos em 1 dia útil;
  - alertas até D+10;
  - oportunidades no mês seguinte.
- **Justificativa obrigatória** para encerrar um achado sem correção ("está correto porque..."), com evidência.
- **Falso positivo recorrente:** a regra é revista. A equipe não pode se acostumar a ignorar alertas.

## Profundidade de revisão por classe de empresa

| Classe | Perfil | Revisão |
|---|---|---|
| A · complexa | Lucro Real, indústria ou mais de 500 documentos/mês | Revisão de todas as apurações por uma segunda pessoa; todos os grupos de regras |
| B · intermediária | Lucro Presumido, ST ou 100 a 500 documentos/mês | Revisão por amostragem mais todos os achados críticos |
| C · simples | Demais casos | Sem revisão manual quando não há achados: o analista confirma o pacote |

## Dossiê da competência

Por empresa e mês, o dossiê reúne:

- documentos capturados;
- achados e como foram resolvidos;
- apuração da Domínio × sombra;
- declarações e recibos;
- guias e pagamentos;
- quem aprovou cada etapa.

Serve de evidência em fiscalização, de proteção profissional e de histórico para o cliente.

## Organização do time em células

Em vez de cada analista fazer tudo da própria carteira:

- **Célula de captura e escrituração** (assistentes + robôs): etapas 1 a 3.
- **Célula de auditoria e apuração** (analistas): etapas 4 a 6.
- **Revisão e consultoria** (seniores e coordenação):
  - classe A e achados críticos;
  - oportunidades (monofásico, revisão de regime);
  - atendimento consultivo.

O cliente continua com um responsável de referência para o relacionamento, mas o trabalho corre na esteira.
Implantar aos poucos, depois do piloto.
