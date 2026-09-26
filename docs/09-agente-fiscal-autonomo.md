# 09 · Agente fiscal autônomo (versão 2 do plano)

**26/09/2026.** Esta versão substitui o foco do plano anterior. A equipe não lança nem audita. Um agente de IA (o
Claude) opera a Domínio Web pelas telas e fecha o mês das empresas menores do Simples, de ponta a ponta. Os documentos
00 a 08 continuam valendo como base: hub de dados, catálogo de conferências, APIs oficiais e radar legislativo.

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

O agente roda no **computador do escritório** onde a Domínio Web está instalada, numa sessão do app desktop do Claude
com *Computer use* ligado. Ele usa três "mãos":

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
| 4 | ICMS nas entradas | Calcula antecipação parcial, antecipação com ST e DIFAL, nota a nota | Divergência com a Domínio; regra da UF não validada |
| 5 | Apuração | Apura o Simples na Domínio e recalcula o DAS de forma independente | Recálculo diferente; DAS 30% fora da média |
| 6 | Guias | Gera o DAS pela Domínio via Integra Contador (transmite o PGDAS-D) e as guias estaduais | **Aprovação antes de transmitir** (níveis 1 e 2) |
| 7 | Acessórias | Coloca as guias na pasta do e-Contínuo e confere a entrega pela API | **Aprovação antes de copiar para a pasta**: equivale a enviar ao cliente |
| 8 | Retorno | Monta o relatório da empresa e o consolidado do lote | — |

## Níveis de autonomia

| Nível | Como funciona | Critério para subir |
|---|---|---|
| 1 · Acompanhado | Fazemos juntos na tela e a pessoa confirma cada etapa | Procedimento mapeado, sem pendências |
| 2 · Supervisionado | O agente faz tudo e para antes de transmitir e de enviar. Aprovação em lote pelo relatório. | 2 competências seguidas sem correção humana |
| 3 · Por exceção | Sem alerta, transmite e envia sozinho. Com alerta, espera. | Autorização escrita do sócio para a empresa |

## Como vamos construir juntos

| Quando | Sessão | Resultado |
|---|---|---|
| Semana 1 | **Importação e conferência** com 1 empresa de comércio simples: você mostra, eu faço na tela, anotamos cada passo | Etapas 1 a 3 mapeadas |
| Semana 2 | **ICMS nas entradas e apuração do Simples** | Etapas 4 e 5 mapeadas; regras da UF conferidas e validadas |
| Semana 3 | **PGDAS-D, DAS e guias estaduais** | Etapa 6 mapeada; forma de acesso definida (portal ou Integra Contador) |
| Semana 4 | **Acessórias e relatório** | Etapas 7 e 8 mapeadas |
| Competência 10/2026 (novembro) | **Piloto com 5 empresas no nível 2** | Tempo e custo reais medidos por empresa |
| Dezembro em diante | **Escala** para todas as empresas menores; nível 3 onde for liberado | Fechamento das pequenas feito pelo agente |

Em janeiro/2027 o procedimento é revisto. Os campos de IBS/CBS passam a valer para o Simples e a repartição do DAS
muda com a CBS.

## O que precisa estar pronto

1. Um **computador Windows** (ou Mac) com a Domínio Web e o plugin instalados, que possa ficar dedicado ao agente
   durante os fechamentos.
2. **App desktop do Claude** instalado e conectado, com *Computer use* ligado em Configurações → App desktop →
   Computer use, e a extensão **Claude in Chrome**.
3. **Usuário da Domínio para o agente.** Confirmar com a Thomson Reuters se pode ser um usuário dedicado e como
   funciona o MFA do login.
4. **Integra Contador** contratado e configurado na Domínio, com procuração dos clientes para o PGDAS-D.
   **e-Contínuo** do Acessórias instalado no computador; o token da API é opcional.
5. Este **repositório clonado** no computador, por exemplo em `C:\automacao-fiscal`, com o **Python 3** instalado. As
   ferramentas usam só a biblioteca padrão.
6. A lista das **5 empresas do piloto**.

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
- **Custo da IA por empresa.** Depende de quantas telas cada fechamento percorre. O piloto mede.

## Business case (empresas menores)

O modelo usa números de exemplo; substitua pelos seus.

| Premissa | Exemplo |
|---|---|
| Empresas menores no fiscal | 150 |
| Horas por empresa por mês hoje (do XML ao envio) | 3,0 h |
| Parte do trabalho que o agente assume | 70% no nível 2 · 85% no nível 3 |
| Supervisão humana por empresa | 15 min no nível 2 · 5 min no nível 3 |
| Custo por analista | R$ 5.500/mês |
| Custo da IA por empresa | R$ 15/mês (ilustrativo; medir no piloto) |
| Integra Contador por DAS | R$ 0,96 (declaração + guia + extrato na 1ª faixa) |
| Computador dedicado | R$ 400/mês |
| Supervisor do agente | 20 h/mês |

| Resultado | Nível 2 | Nível 3 |
|---|---|---|
| Horas da equipe nas empresas menores | 450 h → 172,5 h | 450 h → 80 h |
| Capacidade liberada | 1,98 FTE | 2,64 FTE |
| Economia bruta anual | R$ 130,8 mil | R$ 174,4 mil |
| Custo anual do agente (IA, Integra Contador, computador e supervisor) | R$ 43,0 mil | R$ 43,0 mil |
| Resultado líquido anual | R$ 87,9 mil | R$ 131,5 mil |

A página do plano tem a calculadora. A capacidade liberada vira resultado quando não se repõem desligamentos, quando se
absorvem clientes novos ou quando o tempo vai para consultoria.

## O que preciso de você

1. A **UF** (ou as UFs) das empresas menores. As regras de antecipação e DIFAL mudam por estado.
2. O **Integra Contador** já está configurado na Domínio para o DAS? Se não, como geram hoje: código de acesso,
   certificado ou procuração?
3. Vocês já usam o **e-Contínuo** do Acessórias para as guias?
4. Quantas **empresas menores** são e quanto tempo cada uma leva por mês, mesmo que estimado.
5. Qual **computador** pode ficar com o agente e se ele tem a Domínio Web instalada.
6. **5 empresas** para o piloto, de preferência comércio com compras de outros estados.
