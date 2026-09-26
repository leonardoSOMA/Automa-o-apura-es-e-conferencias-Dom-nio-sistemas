# Ecossistema de Automação Fiscal · Domínio Web

Planejamento (e, a partir da Fase 1, o código) do ecossistema que vai automatizar capturas, auditorias
(cruzamentos), escrituração assistida, apurações e fechamento do departamento fiscal, em volta da
**Domínio Web (Thomson Reuters)**.

> **Status: Fase 0, planejamento e diagnóstico (setembro/2026).** Nada foi implantado ainda.
> Os números são estimativas iniciais e serão substituídos pelo baseline medido na Fase 0.

## Objetivos

| Objetivo | Meta em 12 meses (cenário base, a validar) |
|---|---|
| Reduzir o esforço do fiscal (hoje 12 pessoas) | −28% de horas por empresa ≈ 3,4 FTE de capacidade liberada |
| Auditar todas as empresas, todo mês | 100% de cobertura automática, com o analista atuando só nas exceções |
| Fechar mais cedo | 90% das empresas fechadas até D+10 úteis |
| Chegar à virada da CBS (jan/2027) preparado | Captura, hub de dados e auditoria de IBS/CBS rodando antes de janeiro |

## Comece por aqui

1. [Página do plano](https://claude.ai/artifact/5xaa7eMNJtrRRHkoMFM7fU): versão visual e interativa, com
   calculadora do business case e catálogo filtrável. O link é privado e só abre para quem tiver acesso.
2. [`docs/00-sumario-executivo.md`](docs/00-sumario-executivo.md): uma página para os sócios.
3. [`docs/08-fase0-plano-30-dias.md`](docs/08-fase0-plano-30-dias.md): o que fazer a partir de segunda-feira.
4. [`fase0/Kit_Fase0_Diagnostico.xlsx`](fase0/Kit_Fase0_Diagnostico.xlsx): planilha da Fase 0. Tem cadastro mestre,
   levantamento de tempo, baseline, business case, catálogo de auditorias, plano de 30 dias e roteiro de reuniões.

## Documentos

| Documento | Conteúdo |
|---|---|
| [00 · Sumário executivo](docs/00-sumario-executivo.md) | Problema, tese, recomendação, números, alertas e decisões |
| [01 · Arquitetura](docs/01-arquitetura.md) | Princípios, camadas, as 3 portas da Domínio Web, APIs oficiais, comprar × construir |
| [02 · Catálogo de auditorias](docs/02-catalogo-auditorias.md) | 46 cruzamentos priorizados em 4 fases, com ficha-modelo de regra |
| [03 · Esteira de fechamento](docs/03-esteira-de-fechamento.md) | Fechamento D+n, semáforo de importação e gestão por exceção |
| [04 · Roadmap](docs/04-roadmap.md) | Fases com datas, entregáveis e critérios de continuidade |
| [05 · Business case](docs/05-business-case.md) | Premissas, cenários, payback e como converter capacidade em resultado |
| [06 · Pessoas, governança e riscos](docs/06-pessoas-governanca-riscos.md) | Núcleo de automação, gestão de mudança, segurança/LGPD, KPIs e riscos |
| [07 · Reforma tributária e radar](docs/07-reforma-tributaria-e-radar.md) | Linha do tempo 2026–2033, prazos e fontes consultadas |
| [08 · Fase 0: plano de 30 dias](docs/08-fase0-plano-30-dias.md) | Semana a semana, decisões e roteiros para TR, SERPRO e fornecedores |

## Estrutura do repositório

```
docs/                 planejamento (este material)
catalogo/             catálogo de regras de auditoria (CSV), futuro registro de regras do motor
fase0/                kit de diagnóstico
ferramentas/          geradores do catálogo (CSV) e do kit (xlsx), a partir de uma fonte única
# planejado a partir da Fase 1
conectores/           Distribuição DF-e, ADN (NFS-e), Integra Contador, API Domínio, extração do banco
hub/                  modelo de dados (PostgreSQL) e cargas
regras/               uma regra de auditoria por arquivo, com casos de teste
apuracao_sombra/      recálculo do Simples, Presumido, ICMS e retenções
painel/               painel de fechamento e KPIs
```

## Princípios

1. A Domínio continua sendo o livro oficial. O ecossistema trabalha em volta dela e não a substitui.
2. Dados antes de robôs: capturar e centralizar primeiro; robô de tela só onde não há porta oficial.
3. Portas oficiais primeiro: API da Domínio, Integra Contador (SERPRO), ADN (NFS-e) e Distribuição DF-e (SEFAZ).
4. Regras como dados: tabelas e parâmetros com vigência, porque a Reforma muda regras todo ano até 2033.
5. Gestão por exceção: o que passa limpo segue, e o analista vê só as divergências.
6. Humano no circuito: a IA sugere, a regra determinística valida e o contador aprova.
7. Rastreabilidade: cada achado guarda regra, versão, evidência e quem resolveu.

## Aviso

A legislação citada foi pesquisada em 26/09/2026 (fontes em [`docs/07`](docs/07-reforma-tributaria-e-radar.md)).
Confirme na fonte oficial antes de agir. O ecossistema apoia, e não substitui, o julgamento e a responsabilidade
técnica do contador.
