# 06 · Pessoas, governança e riscos

## Núcleo de automação fiscal

| Papel | Quem | Dedicação | Responsabilidades |
|---|---|---|---|
| Patrocinador | Sócio | 2 h/semana | Prioridades, orçamento, go/no-go, comunicação com a equipe |
| Dono das regras | Coordenador fiscal sênior | 30% a 50% nas Fases 0 a 2 | Conteúdo fiscal de cada regra (ficha), aprovação de mudanças, condução do piloto |
| Analista de automação/dados | Novo ou realocado. Perfil: Excel avançado/SQL/Python e noção fiscal. | 100% | Conectores, hub, regras em código, painel. Desenvolve com apoio do Claude Code. |
| Usuários-chave | 2 analistas do piloto | 20% | Testar, medir e treinar os colegas |
| Parceiro externo (opcional) | Consultoria ou desenvolvedor | Fases 1 e 2 | Acelerar a fundação e transferir conhecimento |

Procure primeiro dentro de casa: a aba *Equipe* do kit registra o perfil técnico e o interesse de cada pessoa.

## Gestão de mudança

- **Comunicar antes de medir.** O levantamento de tempo não é avaliação individual. Ele mostra onde o processo trava.
- **Compromisso explícito com as pessoas:**
  - a redução vem por não reposição e por crescimento;
  - quem quiser pode migrar para automação, revisão ou consultoria.
- **Treinamento:** ler o painel, tratar e justificar achados, sugerir regras novas.
- **Metas compartilhadas:** horas por empresa e qualidade, e não quantidade de notas lançadas.
- **Reconhecimento:** a regra sugerida por um analista leva o nome dele na ficha.

## Governança das regras

- **Ciclo de vida:**
  1. Backlog.
  2. Especificação (ficha).
  3. Desenvolvimento.
  4. Casos de teste reais.
  5. Modo sombra por 1 competência.
  6. Produção.
  7. Revisão trimestral.
- **Segregação:** quem escreve a regra não aprova sozinho. O dono fiscal aprova o conteúdo e o analista de automação
  aprova a parte técnica.
- **Versionamento:** tudo neste repositório. Cada mudança registra motivo e vigência.
- **Radar legislativo mensal:** alimenta o backlog (ver [07](07-reforma-tributaria-e-radar.md)).
- **Saúde da regra:** falso positivo acima de 20% por 2 meses leva a revisar ou desligar a regra.

## Segurança e LGPD

- **Certificados A1:**
  - ficam em cofre (Azure Key Vault, AWS Secrets Manager ou cofre local criptografado);
  - só o servidor de robôs acessa;
  - senha nunca vai por e-mail nem fica em pasta;
  - o uso é registrado em log;
  - o vencimento gera alerta (AUD-F02).
- **Certificados A3 não servem para robôs.** O ADN exige o certificado do próprio cliente. Planeje migrar para A1 onde
  a captura precisar, ou use autXML e procuração quando der.
- **Procurações eletrônicas do e-CAC** para o CNPJ do escritório, por código de serviço (Integra Contador).
- **Acessos:**
  - por perfil no hub e no painel;
  - *usuário externo* somente leitura na Domínio;
  - MFA em tudo.
- **LGPD:**
  - base legal: execução de contrato e obrigação legal;
  - minimização: NFC-e e NFS-e trazem CPF de consumidores;
  - retenção: 5 anos mais os prazos de discussão;
  - acordo de tratamento de dados com cada fornecedor;
  - backups criptografados e plano de resposta a incidentes.
- **IA:** só com contrato corporativo que não use os dados para treinamento. Mascarar CPF e nome de pessoa física
  quando não forem necessários.

## KPIs do projeto

| KPI | Como medir | Baseline | Meta em 6 meses | Meta em 12 meses |
|---|---|---|---|---|
| Horas por empresa/mês, por classe | Levantamento de tempo, depois registro de tarefas | Fase 0 | −10% | −28% |
| Empresas por analista | Cadastro mestre | Fase 0 | +11% | +39% |
| Documentos em verde (lançados sem intervenção) | Hub | — | 60% | 80% |
| Empresas fechadas até D+10 | Painel | Fase 0 | 70% | 90% |
| Cobertura de auditoria automática | Hub | 0% | 100% das empresas | 100% com as regras da Fase 3 |
| Falsos positivos por regra | Hub | — | abaixo de 20% | abaixo de 15% |
| Erros depois da entrega (retificações, multas e juros pagos pelo escritório) | Registro de ocorrências | Fase 0 | −50% | −80% |
| Receita de serviços novos | Financeiro | 0 | a definir | a definir |

## Riscos

| # | Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|---|
| 1 | A TR não libera a leitura do banco via backup | Média | Médio | Plano B desde a Fase 0 (EFD + Gerador de Relatórios); priorizar regras que funcionam com EFD; negociar |
| 2 | Robô de tela quebra com atualização da Domínio Web | Alta, se usado | Médio | Só como último recurso, com monitoramento e roteiro manual de contingência |
| 3 | Regra errada replicada em muitas empresas | Média | Alto | Modo sombra, casos de teste, aprovação dupla, piloto antes de escalar |
| 4 | Vazamento de certificados ou de dados | Baixa | Muito alto | Cofre, acesso mínimo, logs, MFA, seguro cibernético, conformidade com a LGPD |
| 5 | Resistência da equipe | Média | Alto | Comunicação, compromisso com as pessoas, requalificação, metas compartilhadas |
| 6 | Dependência de uma única pessoa | Alta | Alto | Documentação e código neste repositório, 2 pessoas treinadas, parceiro externo |
| 7 | Mudanças da Reforma (alíquota da CBS só em dezembro; regras novas até 2033) | Alta | Médio | Regras como dados com vigência, radar mensal, foco em CBS/IBS na Fase 2 |
| 8 | Cadastros ruins na Domínio | Alta | Médio | Saneamento na Fase 0 (cadastro mestre) e regra AUD-F01 |
| 9 | Bloqueio por consumo indevido na SEFAZ ou municípios fora do ADN | Média | Médio | Fornecedor especializado, controle de NSU, lista de municípios fora do ADN |
| 10 | Custos de ferramentas se acumulam | Média | Médio | Orçamento por fase; cancelar o que não mostrar ganho no go/no-go |
| 11 | Pico de trabalho em janeiro/2027 (virada da CBS) atrasa o projeto | Alta | Médio | Fundação pronta em dezembro; nada de mudança grande de processo em janeiro |
