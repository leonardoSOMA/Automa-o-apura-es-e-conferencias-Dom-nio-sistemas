# 08 · Fase 0: plano de 30 dias

A planilha [`fase0/Kit_Fase0_Diagnostico.xlsx`](../fase0/Kit_Fase0_Diagnostico.xlsx) traz esta lista com responsáveis,
prazos calculados a partir da data de início e coluna de status. Os prazos abaixo supõem início em 28/09/2026.

## Semana 1 (28/09 a 02/10)

| # | Ação | Responsável | Entregável |
|---|---|---|---|
| 1 | **URGENTE, até 30/09:** revisar os clientes do Simples com vendas relevantes a empresas e decidir a opção pelo IBS/CBS fora do DAS no 1º semestre de 2027. A opção pode ser cancelada até 30/11/2026. Confirme no Portal do Simples Nacional. | Sócio + coordenador | Clientes analisados e opções feitas |
| 2 | Nomear o núcleo: patrocinador, dono das regras e candidato a analista de automação | Sócio | Núcleo nomeado |
| 3 | Comunicar a equipe: objetivos, como o tempo será medido e o compromisso com as pessoas | Sócio | Reunião realizada |
| 4 | Preencher a aba *Equipe* e começar o *Levantamento de Tempo* (10 dias úteis) | Coordenador fiscal | Registros diários |
| 5 | Agendar a reunião com o gerente de contas da Thomson Reuters | Sócio | Reunião agendada |

## Semana 2 (05 a 09/10)

| # | Ação | Responsável | Entregável |
|---|---|---|---|
| 6 | Preencher o *Cadastro Mestre* de 100% das empresas | Analistas (cada um a sua carteira) | Cadastro completo |
| 7 | Inventariar certificados A1/A3, procurações do e-CAC e acessos estaduais/municipais | Coordenador fiscal | Pendências listadas |
| 8 | Mapear o processo atual de 3 empresas-tipo (Simples comércio, Presumido serviços, regime normal de ICMS) | Coordenador + 1 analista | Fluxo atual desenhado |
| 9 | Começar a campanha autXML: clientes incluem o CNPJ do escritório nas NF-e que emitem | Coordenador + atendimento | Comunicado enviado |
| 10 | Reunião com a TR, com as respostas registradas no roteiro | Sócio | Roteiro respondido |

## Semana 3 (13 a 16/10; 12/10 é feriado)

| # | Ação | Responsável | Entregável |
|---|---|---|---|
| 11 | Pedir a chave da API da Domínio (api.dominio@tr.com), enviar o XML de 1 empresa e testar a extração: EFD, Gerador de Relatórios e, se liberado, backup do banco | Analista de automação | Envio e extração testados |
| 12 | Contratar e testar o Integra Contador com 2 empresas-piloto | Analista de automação | Consulta do PGDAS-D e da caixa postal funcionando |
| 13 | POCs de captura (2 parceiros homologados) e de auditoria (Kolossus Auditor e 1 alternativa), usando o catálogo como checklist | Coordenador fiscal | Comparativo preenchido |
| 14 | Escolher 15 a 20 empresas-piloto (classes A, B e C) | Coordenador fiscal | Lista do piloto |

## Semana 4 (19 a 23/10)

| # | Ação | Responsável | Entregável |
|---|---|---|---|
| 15 | Consolidar o baseline e atualizar o *Business Case* com números reais | Sócio + coordenador | Baseline aprovado |
| 16 | Decidir execução, o que comprar e o que construir, infraestrutura e orçamento | Sócio | Decisões registradas |
| 17 | Preparar o ambiente: servidor/VM, banco, cofre de certificados, acesso ao repositório | Analista de automação | Ambiente pronto |
| 18 | Aprovar o backlog da Fase 1 (16 regras) e o calendário do piloto | Sócio + coordenador | Kick-off da Fase 1 |

## Decisões a registrar no fim da Fase 0

| Decisão | Opções | Recomendação inicial |
|---|---|---|
| Quem executa | Interno realocado × contratado × consultoria | Interno com perfil técnico + consultoria na fundação |
| Captura de XML | Parceiro homologado × construir | Parceiro homologado da API Domínio que exporte para o hub |
| Auditoria de prateleira | Kolossus Auditor × alternativa × só construir | Decidir pela cobertura do catálogo na POC |
| Extração da Domínio | Backup restaurado × EFD/relatórios | Backup, se a TR autorizar; EFD/relatórios como plano B |
| Infraestrutura | Servidor local × nuvem | Nuvem (VM Windows + banco gerenciado), com backups |
| Painel | Power BI × Looker Studio × Metabase | O que combinar com Microsoft 365 ou Google Workspace |
| Pessoas | Não reposição × realocação | Não reposição + realocação para revisão e consultoria |

## Roteiro das reuniões (resumo)

O roteiro completo, com espaço para as respostas, está na aba *Roteiro de Reuniões* do kit.

**Thomson Reuters**

- Custo e limites da API de entrada.
- Leitura de dados: existe API? A restauração do backup é permitida? Precisa de licença do SQL Anywhere?
- Leiaute TXT com acumulador por nota.
- Exportação de EFD e relatórios em lote.
- Política para robôs e MFA.
- Kolossus Auditor e Domínio Processos no pacote contratado.
- Cronograma de CBS/IBS.
- Aviso prévio de mudanças de tela.

**SERPRO**

- Serviços do Integra Contador para o nosso caso.
- Tabela de preços por faixa.
- Procurações por código de serviço.

**Fornecedores de captura**

- Homologação na API Domínio.
- Cobertura (inclusive NFS-e fora do ADN e notas emitidas via autXML).
- Certificados A1/A3 e limites da SEFAZ.
- Exportação para o hub.
- Preço e LGPD.

## O que ainda preciso saber para detalhar a Fase 1

1. Quantas empresas o fiscal atende e a divisão por regime (Simples, Presumido, Real, MEI) e por atividade.
2. Em quais UFs estão os clientes. Isso define ST, DIFAL, antecipação e declarações estaduais.
3. Quais módulos e pacote da Domínio estão contratados (One/Pro/Max, Processos, Portal do Cliente) e se a importação
   de XML já é usada.
4. Volume médio de notas por mês e quantos clientes têm certificado A1 × A3.
5. Se alguém da equipe tem perfil técnico (Power Query, SQL, Python).
6. Ferramentas já contratadas (captura, tarefas, BI) e se o escritório usa Microsoft 365 ou Google Workspace.
