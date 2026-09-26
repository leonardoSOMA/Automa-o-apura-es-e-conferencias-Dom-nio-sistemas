# 09 · Agente fiscal autônomo (versão 2 do plano)

**26/09/2026.** Esta versão substitui o foco do plano anterior. A equipe não lança nem audita. Um agente de IA (o
Claude) opera a Domínio Web pelas telas e fecha o mês das empresas menores do Simples, de ponta a ponta. Os documentos
00 a 08 continuam valendo como base: hub de dados, catálogo de conferências, APIs oficiais e radar legislativo.

## Perfil confirmado (26/09/2026)

- **Carteira:** 356 empresas no Acessórias. No Simples, 63 sem inscrição estadual (as prestadoras, fase 1) e 161 com
  inscrição estadual (comércio e indústria, fase 2). Todas em MG, a maioria em Três Corações.
- **Piloto:** 5 empresas escolhidas, com o cadastro em `config/empresas_autorizadas.csv` (fora do Git). Três têm IE
  (uma ainda sem a IE cadastrada no Acessórias) e duas são prestadoras, que já têm certificado A1.
- **Integra Contador** já configurado na Domínio: o DAS sai pela própria Domínio.
- **e-Contínuo** do Acessórias já em uso: o envio ao cliente é salvar o PDF na pasta.
- **O agente roda numa máquina física dedicada com Windows 11 Pro no escritório, ligada 24 h.** O sócio supervisiona com a
  própria conta do Claude. O escritório não tem Microsoft 365, e o Windows 365 fica como alternativa na nuvem (ver
  [10 · Computador do agente](10-servidor-do-agente.md)).
- **Pedido novo:** uma **IA analítica** que investiga erros técnicos. O exemplo dado foi o Fator R: CNAE sujeito,
  acumulador configurado sem fator r, e é preciso decidir se é erro ou se a empresa fatura por outra atividade, não
  sujeita.

## A visão, em uma frase

O agente faz o fechamento completo de cada empresa pequena:

1. importa as notas;
2. confere;
3. calcula antecipação de ICMS e DIFAL;
4. apura o Simples;
5. gera o DAS e as guias estaduais;
6. salva os PDFs;
7. envia pelo Acessórias;
8. devolve um relatório.

A equipe aprova e resolve o que o agente não souber.

## Como o agente trabalha

O agente roda num **computador Windows 11 dedicado**: no piloto, uma máquina física no escritório, com a Domínio Web
instalada. Ele trabalha numa sessão do app desktop do Claude (aba Code), com *Computer use* ligado. Ele usa três
"mãos":

| Onde | Como o agente age | Exemplos |
|---|---|---|
| **Domínio Web** (programa aberto pelo plugin) | Pela tela: vê, clica e digita como uma pessoa | Importar XML, emitir relatórios, apurar o Simples |
| **Páginas web** | Pelo navegador (Claude in Chrome), que lê a página e é mais rápido e preciso que clicar na imagem | Login da Domínio Web, Acessórias, SEFAZ |
| **Ferramentas e pastas** | Scripts deste repositório, a pasta do robô e-Contínuo e a API do Acessórias | `das_simples.py`, `icms_entradas.py`, `nfe.py`, `acessorias.py` |

**Por que dá certo agora.** Um robô tradicional clica em coordenadas e quebra quando a tela muda. A Domínio Web é
transmitida como imagem, e para esses robôs isso é um problema. O agente de IA **enxerga e entende a tela**: lê menus,
campos e mensagens, se adapta a pequenas mudanças e percebe quando algo está errado. Ele é mais lento do que uma API,
por isso usa API quando ela existir: a de entrada de XML da Domínio e o Integra Contador para o PGDAS-D.

## O que a Domínio e o Acessórias já fazem

A pesquisa na central de soluções da Domínio e na documentação do Acessórias mostrou três atalhos. Todos serão
confirmados nas sessões.

- **DAS pela própria Domínio, via Integra Contador.** Fica em Relatórios > Guias > Federais > DAS, e também nas Rotinas
  Automáticas.
  - A Domínio transmite o PGDAS-D e emite o DAS pelo SERPRO, em lote, por cerca de R$ 1 por DAS.
  - O escritório contrata o Integra Contador e cada cliente dá procuração eletrônica com o serviço PGDAS-D.
  - O portal do PGDAS-D fica de fora: tem captcha e bloqueia robôs das 8h às 18h.
- **Acessórias pelo robô e-Contínuo.** O agente salva o PDF numa pasta. O robô lê a guia, identifica empresa, obrigação
  e competência, envia ao cliente e registra a entrega. Existe também uma API para enviar e para conferir as entregas.
- **Antecipação e DIFAL na Domínio.** A Domínio calcula quando está configurada:
  - impostos 27 (ICMS Antecipado), 8 (DIFALI) e 31 (ICMS ST/AT);
  - configuração em Controle > Parâmetros e Arquivos > Impostos.

  A calculadora do agente confere esses valores.

## O fluxo de uma empresa

O procedimento completo está em [`.claude/skills/fechamento-simples`](../.claude/skills/fechamento-simples/SKILL.md).

| # | Etapa | O agente faz | Para e pergunta quando |
|---|---|---|---|
| 1 | Documentos | Junta os XML do mês e resume quantidade e valores | Volume muito abaixo do normal |
| 2 | Importação | Importa os XML na Escrita Fiscal pela tela | Nota sem acumulador conhecido |
| 3 | Conferência | Compara o relatório da Domínio com os XML e roda as conferências do catálogo | Nota faltando, sobrando ou divergente |
| 4 | ICMS nas entradas | Só contribuintes do ICMS, como o comércio: antecipação parcial, com ST e DIFAL, nota a nota | Divergência com a Domínio; regra da UF não validada |
| 5 | Apuração | Apura o Simples na Domínio e recalcula o DAS de forma independente | Recálculo diferente; DAS 30% fora da média |
| 6 | Revisão técnica | IA analítica: Fator R, ISS retido, município de incidência, retenções, limites | "Erro provável" acima de R$ 50 bloqueia a transmissão |
| 7 | Guias | Gera o DAS pela Domínio via Integra Contador (transmite o PGDAS-D) e as guias estaduais | **Aprovação antes de transmitir** (níveis 1 e 2) |
| 8 | Acessórias | Coloca as guias na pasta do e-Contínuo e confere a entrega pela API | **Aprovação antes de copiar para a pasta**: equivale a enviar ao cliente |
| 9 | Retorno | Monta o relatório da empresa e o consolidado do lote | — |

## IA analítica

É o mesmo agente trabalhando como revisor técnico, com um procedimento próprio: a skill
[`analise-tecnica`](../.claude/skills/analise-tecnica/SKILL.md). Não é outra IA. O método é o diagnóstico diferencial:

1. **Fatos:** CNAEs, acumuladores, notas, folha e apuração.
2. **Regra:** dispositivo e vigência.
3. **Hipóteses:** todas as explicações possíveis.
4. **Teste:** cada hipótese contra evidência.
5. **Conclusão:** erro provável, indício, situação justificada, oportunidade ou risco latente (configuração errada
   que ainda não mudou o imposto).
6. **Impacto em reais:** pelo recálculo do DAS.
7. **Ação e quem decide.**

A **AT-01 · Fator R** já tem ferramenta (`ferramentas/analise_fator_r.py`), tabela CNAE × anexo com 75 CNAEs e
base legal (`config/tabelas/cnae_anexo.csv`, `docs/referencias/fator-r.md`) e 16 cenários testados. Um deles é o caso
descrito: empresa com atividade sujeita e outra não sujeita, notas emitidas pela não sujeita. Nesse cenário a conclusão
é "situação justificada", e não "erro". Outros cenários testados:
- empresa sem folha nem pró-labore, que tem fator r de 0,01 e vai para o Anexo V;
- acumulador fixo no Anexo III com fator r acima de 28% (risco latente);
- atividade não sujeita apurada no Anexo V (pagamento a maior).

Catálogo completo:

| Código | Análise |
|---|---|
| AT-01 | Fator R e anexo (III × V): CNAE × acumulador × notas × folha |
| AT-02 | ISS retido segregado no PGDAS-D (evita pagar ISS duas vezes) |
| AT-03 | ISS devido a outro município |
| AT-04 | CNAE × serviço faturado |
| AT-05 | Retenções federais indevidas em notas de optante |
| AT-06 | Anexo IV: CPP fora do DAS e retenção de INSS |
| AT-07 | Planejamento do fator r: folha que leva ao Anexo III e economia |
| AT-08 | Limite, sublimite e crescimento |
| AT-09 | Comércio: monofásicos e ST |
| AT-10 | Comércio: antecipação e DIFAL |

**Primeira entrega prática sugerida:** a varredura de Fator R nas 70 prestadoras, com os achados ordenados por impacto
em reais.

## Níveis de autonomia

| Nível | Como funciona | Critério para subir |
|---|---|---|
| 1 · Acompanhado | Fazemos juntos na tela e a pessoa confirma cada etapa | Procedimento mapeado, sem pendências |
| 2 · Supervisionado | O agente faz tudo e para antes de transmitir e de enviar. Aprovação em lote pelo relatório. | 2 competências seguidas sem correção humana |
| 3 · Por exceção | Sem alerta, transmite e envia sozinho. Com alerta, espera. | Autorização escrita do sócio para a empresa |

## Como vamos construir juntos

| Quando | Sessão | Resultado |
|---|---|---|
| Semana 1 | **Máquina do agente e primeira prestadora:** montar a máquina, testar o acesso remoto sem travar a tela e fazer juntos a importação e a conferência das NFS-e | Etapas 1 a 3 mapeadas |
| Semana 2 | **Apuração com fator r e revisão técnica:** onde a Domínio mostra anexo, acumuladores e folha; AT-01 numa empresa real | Etapas 5 e 6 mapeadas |
| Semana 3 | **DAS pelo Integra Contador e e-Contínuo:** fechar o ciclo de uma empresa | Etapas 7 a 9 mapeadas |
| Semana 4 | **As empresas com IE:** NF-e, antecipação, ST e DIFAL com as regras de MG validadas | Etapa 4 mapeada |
| A partir da semana 2 | **Varredura de Fator R nas 63 prestadoras** | Lista de erros e oportunidades por impacto |
| Competência 10/2026 (novembro) | **Piloto: as 5 empresas escolhidas, no nível 2** | Tempo e custo reais por empresa |
| Dezembro em diante | **Escala para as 63 prestadoras** | Nível 3 onde for liberado |

Em janeiro/2027 o procedimento é revisto: DAS com CBS/IBS e o RBT12 com o novo período.

## O que precisa estar pronto

1. A **máquina física dedicada com Windows 11 Pro**, com a Domínio Web e o plugin instalados. A montagem passo a
   passo está em [10 · Computador do agente](10-servidor-do-agente.md).
   - A máquina é só do agente. A sessão fica aberta e desbloqueada, com resolução de tela fixa.
   - O acesso remoto compartilha a tela da própria máquina (Área de Trabalho Remota do Chrome ou AnyDesk). O RDP do
     Windows bloqueia a sessão ao desconectar.
   - Windows Server não serve para o agente.
2. **App desktop do Claude** com *Computer use* ligado em Configurações → App desktop → Computer use, e a extensão
   **Claude in Chrome**.
   - A conta do Claude tem de ser **Pro ou Max, de uma pessoa**: o Computer use não existe nos planos Team e
     Enterprise.
   - A conta é a do sócio que supervisiona e aprova pelo celular.
3. **Usuário da Domínio para o agente.** Confirmar com a Thomson Reuters se pode ser um usuário dedicado e como
   funciona o MFA do login.
4. **Integra Contador** contratado e configurado na Domínio, com procuração dos clientes para o PGDAS-D.
   **e-Contínuo** do Acessórias instalado no computador; o token da API é opcional.
5. Este **repositório clonado** no computador, por exemplo em `C:\automacao-fiscal`, com o **Python 3** instalado. As
   ferramentas usam só a biblioteca padrão.
6. A lista das **5 empresas do piloto**: recebida, com o cadastro em `config/empresas_autorizadas.csv`, fora do Git.

## Segurança

- **O agente nunca paga guias.** Quem paga é o cliente.
- **Transmitir e enviar:**
  - só com aprovação nos níveis 1 e 2;
  - no nível 3, só sem alertas.
- **Captcha e MFA:** o agente chama uma pessoa e não tenta contornar.
- **Cadastros e configurações da Domínio:** o agente não altera sem aprovação.
- **Evidência:** prints, PDFs e log de cada fechamento ficam na pasta de trabalho.
- **Dados de clientes ficam fora do Git.** Veja o `.gitignore`.

## Limites que precisam ser medidos no piloto

- **Velocidade.** Operar pela tela é mais lento que um analista experiente por empresa. O agente compensa rodando sem
  parar, inclusive fora do expediente.
- **Erros de operação.** Um clique errado é possível. Por isso cada etapa termina com uma conferência (quantidade,
  valores, recálculo).
- **Política da Thomson Reuters e login com MFA.** Precisa de resposta antes da escala.
- **Plano do Claude.** O consumo depende de quantas telas cada fechamento percorre. O piloto mede se o Max 5x basta.
- **Aprovação de acesso aos apps.** Hoje ela é pedida a cada sessão, pelo celular. No nível 3, alguém ainda libera o
  início do lote.

## Business case (63 prestadoras)

Premissas de exemplo, a medir no piloto:

| Premissa | Exemplo |
|---|---|
| Horas por empresa por mês hoje | 2 h |
| Parte assumida pelo agente | 70% no nível 2 · 85% no nível 3 |
| Supervisão por empresa | 15 min no nível 2 · 5 min no nível 3 |
| Plano Claude Max 5x | ~R$ 540/mês (US$ 100 com IOF) |
| Integra Contador | R$ 0,96 por DAS |
| Máquina física (energia e desgaste) | ~R$ 100/mês |
| Supervisor | 20 h/mês |

| Resultado | Nível 2 | Nível 3 |
|---|---|---|
| Horas da equipe | 126 h → 53,6 h | 126 h → 24,2 h |
| Capacidade liberada | 0,5 FTE | 0,7 FTE |
| Economia bruta anual | R$ 34,2 mil | R$ 48,0 mil |
| Custo anual do agente | R$ 17,8 mil | R$ 17,8 mil |
| Resultado líquido anual, antes das análises | R$ 16,3 mil | R$ 30,2 mil |

**Leitura honesta:**
- Para 63 prestadoras pequenas, o ganho em horas é modesto.
- O valor maior tende a vir da IA analítica, que encontra Fator R errado, ISS retido pago duas vezes e retenções
  indevidas. Isso vira economia ou recuperação para o cliente e consultoria para o escritório.
- A calculadora da página tem um campo para essa receita.

## O que preciso de você

1. A **lista de empresas da Domínio** (código × CNPJ), ou a confirmação de que os IDs do Acessórias são os códigos
   da Domínio.
2. A **Cerâmica** do piloto é indústria ou comércio?
3. A folha das prestadoras está na **Domínio Folha**? O Fator R depende dela.
4. **Quanto tempo**, mesmo estimado, cada prestadora leva por mês.
5. O **plano da conta do Claude** do sócio: precisa ser Pro ou Max.
