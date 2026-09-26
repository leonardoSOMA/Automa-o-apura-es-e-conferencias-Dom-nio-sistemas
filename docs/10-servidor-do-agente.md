# 10 · Computador do agente: onde roda e como montar

**26/09/2026.** Os preços são de lista e **não incluem impostos**. Confira-os na contratação.

## Recomendação para o piloto

**Uma máquina física dedicada, com Windows 11 Pro, no escritório.** Quem supervisiona é o sócio, com a própria conta
do Claude.

| Por que ela | Detalhe |
|---|---|
| **É o que o Claude e a Domínio suportam** | Windows 11 nativo, sem as dúvidas de licença e de compatibilidade da nuvem |
| **Não tem o problema da tela desconectada** | O acesso remoto é feito compartilhando a tela da própria máquina, e a sessão continua aberta |
| **Custa menos** | O escritório não tem Microsoft 365. Na nuvem seriam ~R$ 504 por mês; aqui fica a energia. |
| **Virtualização de hardware** | O Cowork funciona, se um dia for preciso |

**O que se perde em relação à nuvem:**
- ficar sem energia ou sem internet para o agente, que depois retoma de onde parou;
- não ter SLA de provedor.

A defesa é o nobreak, o backup da pasta de trabalho e o repositório no Git, que guarda os procedimentos. Se a energia
ou a internet do escritório falharem com frequência, ou se o volume pedir mais de uma máquina, a alternativa é o
Windows 365 (abaixo).

## O que o Claude exige da máquina

Conferido na documentação da Anthropic e em relatos de usuários (fontes no fim).

| Requisito | Consequência |
|---|---|
| **Windows 10 ou 11, x64.** O Windows Server não é citado, e há relatos de falha no Server 2022. | Windows 11 Pro na máquina física |
| **Computer use só nos planos Pro e Max.** Está em beta desde abril/2026 e não existe nos planos Team e Enterprise. | Confira o plano da conta do supervisor em Configurações. Não compartilhe o login. |
| **Sessão aberta, desbloqueada e ativa**, com o app aberto e a máquina ligada | Sem bloqueio de tela, sem proteção de tela, sem suspensão |
| **No Windows, o Claude assume a tela inteira.** Não há modo em segundo plano. | A máquina é **só do agente**. Ninguém trabalha nela, e robôs de tela ficam em outra máquina. |
| **O acesso aos apps é aprovado a cada sessão.** A aprovação chega no celular e não dá para deixar pré-aprovada. | O nível 2 funciona. No nível 3, alguém ainda libera o início do lote. |
| **O Cowork exige virtualização** | Ligue a virtualização na BIOS. O agente roda na aba **Code** do app (Claude Code), que não precisa dela. |
| **O app reinicia para se atualizar** em até 72 h | Atualize fora dos dias de fechamento |
| **A Anthropic recomenda não usar Computer use em sites de banco e de governo** | Já está no desenho: DAS pela Domínio com Integra Contador, NFS-e por API e Acessórias pelo e-Contínuo |

## Montagem da máquina física (Sessão 1)

1. **Hardware:**
   - 4 núcleos ou mais, 16 GB de RAM, SSD de 256 GB ou mais;
   - rede por cabo;
   - **nobreak**.
2. **Windows 11 Pro:**
   - BitLocker ligado, porque o disco terá dados de clientes e certificados;
   - senha forte, máquina em lugar fechado;
   - Windows Defender e firewall ativos, sem portas abertas para a internet.
3. **Sempre ligada:**
   - plano de energia sem suspensão nem hibernação;
   - na BIOS, "ligar ao voltar a energia";
   - atualizações do Windows fora dos dias de fechamento (horário ativo e adiamento).
4. **Tela sempre ativa:**
   - monitor ligado ou um **emulador de HDMI**, para manter 1920 × 1080 mesmo sem monitor;
   - sem bloqueio nem proteção de tela.
5. **Volta sozinha depois de reiniciar:** login automático com o Autologon (Microsoft Sysinternals), que guarda a senha
   criptografada. Depois de uma atualização, a sessão volta aberta.
6. **Acesso remoto sem travar a tela:**
   - use um programa que compartilhe a tela da própria máquina: Área de Trabalho Remota do Chrome ou AnyDesk;
   - **não use a Área de Trabalho Remota do Windows (RDP).** Ao desconectar, ela bloqueia a sessão, e o agente passa a
     ver a tela de bloqueio;
   - se precisar do RDP, rode antes de sair: `for /f "skip=1 tokens=3" %s in ('query user %USERNAME%') do tscon %s /dest:console`,
     como administrador (num `.bat`, use `%%s`).
7. **Programas:**
   - plugin da Domínio Web;
   - Google Chrome com a extensão Claude in Chrome;
   - app desktop do Claude (instalador `.msix`), com *Computer use* ligado em Configurações → App desktop → Computer
     use;
   - Python 3 e Git;
   - este repositório em `C:\automacao-fiscal`.
8. **Conta do Claude:**
   - a do sócio que supervisiona, no plano Pro ou Max;
   - desligue o uso das conversas para treinamento de modelos, nas configurações de privacidade, porque os dados são de
     clientes.
9. **Certificados:** só os A1 necessários, marcados como não exportáveis. As duas prestadoras do piloto já têm A1.
10. **Envio ao Acessórias:** pela API do e-Contínuo (`ferramentas/acessorias.py`) ou pela pasta do robô.
11. **Backup:** a pasta `trabalho/` sincronizada com o armazenamento em nuvem do escritório. Ela tem dados de clientes e
    nunca vai para o Git.

## Validar no primeiro mês

1. **Plugin da Domínio Web:** instala e abre, com login e MFA do usuário do agente.
2. **Acesso remoto:** depois de desconectar, o agente continua vendo e clicando.
3. **Reinício:** depois de reiniciar, a sessão volta sozinha e o agente retoma.
4. **Operação:**
   - o app do Claude, na aba Code e aberto na pasta do repositório, opera a Domínio;
   - as aprovações chegam no celular.
5. **Uso do plano:** meça o consumo num fechamento inteiro. O piloto diz se o Max 5x basta.

## Alternativa na nuvem: Windows 365 Enterprise

Se a máquina física não servir, a melhor opção na nuvem é o **Windows 365 Enterprise, plano Premium (4 vCPU, 16 GB,
128 GB), na região Brazil South: R$ 377,90 por usuário por mês**.
- **Pré-requisito:** Windows E3, Intune e Entra ID P1 para o usuário. O escritório não tem Microsoft 365, então o
  caminho é o **Microsoft 365 Business Premium**, cerca de R$ 126 por usuário por mês no plano anual, segundo revendas
  (conferir).
- **Total:** ~R$ 504 por mês.
- **Não hiberna** (o plano Business hiberna depois de 1 hora ocioso).
- **Acesso** pelo app Windows, com login Microsoft e MFA.
- **Ponto a testar:** o agente continuar vendo a tela com a conexão fechada.

| Opção | Sistema | R$/mês | Avaliação |
|---|---|---|---|
| **Máquina física dedicada no escritório** | Windows 11 Pro | energia (~R$ 20 a 80, estimativa) | **Recomendada para o piloto** |
| Windows 365 Enterprise 4/16/128 + Business Premium | Windows 11 | ~504 | Alternativa na nuvem |
| Azure VM D4s_v5, Brazil South, como host pessoal do Azure Virtual Desktop | Windows 11 | ~1.330 (estimativa) + Microsoft 365 | Só se as duas acima falharem |
| Windows 365 Business 4/16/128 | Windows 11 | 320,60 | **Evitar:** hiberna depois de 1 h ocioso |
| AWS t3.xlarge / m7i-flex.xlarge (São Paulo) | Windows Server | 1.401 / 1.923 | **Evitar:** caro, Windows Server, sem Windows 11 em hardware compartilhado |
| Google e2-standard-4 (São Paulo) | Windows Server | 1.606 | **Evitar:** mesmos motivos |
| Oracle E5.Flex 2 OCPU/16 GB (São Paulo) | Windows Server | 1.112 | Só se o Windows Server for testado e aprovado |
| Locaweb, Magalu Cloud, Vultr | Windows Server | varia | Servem para scripts e outros robôs, não para o agente |

Sobre os preços:
- Windows 365 e Oracle estão nas tabelas dos próprios fabricantes, em reais.
- AWS e Google foram convertidos a R$ 5,20 por dólar e cobram IOF.
- O Azure é estimativa.
- Evite instâncias "burstable" (t3, B-series) sob carga 24 horas.

## Custos no business case

| Item | R$/mês | Observação |
|---|---|---|
| Máquina física (energia e desgaste) | ~100 | Estimativa conservadora. Se a máquina já existe, não há compra. |
| Plano Claude Max 5x | ~540 | US$ 100 a R$ 5,20, com IOF. O Max 20x custa o dobro. O piloto mede qual basta. |
| Integra Contador | 0,96 por DAS | Já contratado |

Com 63 prestadoras, 2 h por empresa hoje e supervisor de 20 h por mês:

| | Nível 2 | Nível 3 |
|---|---|---|
| Custo anual do agente | R$ 17,8 mil | R$ 17,8 mil |
| Capacidade liberada | 0,5 FTE | 0,7 FTE |
| Resultado líquido anual, antes das análises | R$ 16,3 mil | R$ 30,2 mil |

Na nuvem (Windows 365 + Business Premium), o custo sobe R$ 4,8 mil por ano. A calculadora da página tem esses campos.

## Outras automações na mesma máquina

- **Scripts sem tela** (Python, APIs, downloads de XML) podem rodar na mesma máquina.
- **Robôs que usam a tela** (RPA) não: no Windows, o Claude usa a tela inteira. Coloque-os em outra máquina, que pode
  ser Windows Server, ou em horários separados dos fechamentos.

## Fontes (consultadas em 26/09/2026)

- Computer use no app desktop (planos, Windows, beta): https://code.claude.com/docs/en/desktop e
  https://support.claude.com/en/articles/14128542
- Requisitos do app no Windows: https://support.claude.com/en/articles/10065433
- Cowork em máquinas virtuais: https://support.claude.com/en/articles/12622703
- Políticas do app (atualização automática): https://support.claude.com/en/articles/12622667
- Preços do Windows 365 Enterprise no Brasil: https://www.microsoft.com/pt-br/windows-365/enterprise/compare-plans-pricing
- Licenciamento do Windows em nuvem: https://www.microsoft.com/licensing/terms/productoffering/WindowsDesktopOperatingSystem/MCA
- Microsoft 365 Business Premium no Brasil (revendas, a conferir):
  https://www.office365brasil.com.br/365blog/sem-categoria/novos-precos-do-microsoft-365-business-no-brasil-guia-atualizado-por-plano-2026/
  e https://blog.ftconsult.com.br/reajuste-microsoft-365-julho-2026/
- Preços AWS (Price List API, sa-east-1, 25/09/2026), Google Cloud (páginas de preço de Compute Engine) e Oracle
  (cloud-price-list.json, 23/09/2026).
- Plugin GO-Global (clientes suportados): https://releases.graphon.com · Domínio Web (requisitos): central de soluções,
  código 4351.
- Planos do Claude: https://claude.com/pricing
