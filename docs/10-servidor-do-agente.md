# 10 · Servidor do agente: onde contratar e como montar

**26/09/2026.** Os preços são de lista e **não incluem impostos**. Confira-os na contratação.

## Recomendação

**Windows 365 Enterprise, plano Premium (4 vCPU, 16 GB de RAM, 128 GB), na região Brazil South (São Paulo):
R$ 377,90 por usuário por mês.**

O Windows 365 é um "Cloud PC": um Windows 11 completo na nuvem da Microsoft, ligado o tempo todo e cobrado em reais.

| Por que ele | Detalhe |
|---|---|
| É **Windows 11** | É o sistema suportado pelo app do Claude e pelo plugin da Domínio Web (GO-Global). O Windows Server não aparece nas páginas de requisitos de nenhum dos dois. |
| É **legal e barato** | Windows 11 em nuvem compartilhada só é permitido na Microsoft, com licença por usuário. Na AWS e no Google, só em hardware dedicado. |
| **Fica ligado** | O plano Enterprise não hiberna. O Business hiberna depois de 1 hora ocioso e não serve. |
| **Acesso seguro** | Entra-se pelo app Windows, com login Microsoft e MFA. Não fica porta de área de trabalho remota aberta na internet. |
| **Dados no Brasil** | A região Brazil South fica em São Paulo, perto da Domínio e dos portais, o que ajuda na LGPD. |

**Pré-requisito.** A pessoa dona do Cloud PC precisa de Windows E3, Intune e Entra ID P1. O caminho mais simples é o
**Microsoft 365 Business Premium**, cerca de R$ 126 por usuário por mês no plano anual, segundo revendas (conferir).
Se o escritório já tem Business Premium, E3 ou E5, não há custo extra.

**Custo do servidor:** R$ 377,90, mais R$ 126 se precisar do Business Premium, o que dá **cerca de R$ 504 por mês**,
mais impostos.

## O que o Claude exige da máquina

Conferido na documentação da Anthropic e em relatos de usuários (fontes no fim).

| Requisito | Consequência |
|---|---|
| **Windows 10 ou 11, x64.** O Windows Server não é citado, e há relatos de falha no Server 2022. | Nada de VPS com Windows Server para o agente. |
| **Computer use só nos planos Pro e Max.** Está em beta desde abril/2026 e não existe nos planos Team e Enterprise. | A conta do Claude no servidor é **Pro ou Max, de uma pessoa**. Não compartilhe o login. |
| **Sessão aberta, desbloqueada e ativa**, com o app aberto e a máquina ligada | Sem bloqueio de tela nem proteção de tela, e com a desconexão testada (ver abaixo) |
| **No Windows, o Claude assume a tela inteira.** Não há modo em segundo plano. | O agente não divide a sessão com robôs de tela. Scripts sem tela podem rodar junto. |
| **O acesso aos apps é aprovado a cada sessão.** A aprovação chega no celular e não dá para deixar pré-aprovada. | O nível 2 funciona. No nível 3, alguém ainda libera o início do lote. |
| **O Cowork exige virtualização aninhada** | O agente roda na aba **Code** do app (Claude Code), que não precisa dela. |
| **O app reinicia para se atualizar** em até 72 h | Atualize fora dos dias de fechamento; há política para controlar isso. |
| **A Anthropic recomenda não usar Computer use em sites de banco e de governo** | Já está no desenho: DAS pela Domínio com Integra Contador, NFS-e por API e Acessórias pelo e-Contínuo. |

## Validar no primeiro mês, antes de levar as 63 prestadoras

1. **Plugin da Domínio Web.** Instala e abre no Cloud PC, com login e MFA do usuário do agente.
2. **Sessão desconectada.** Quando a conexão remota fecha, o Windows para de desenhar a tela, e o Computer use vê tela
   preta. Teste o `tscon` (passo 8 da montagem) e confirme que o agente continua vendo e clicando com ninguém
   conectado.
3. **Limites de ociosidade e desconexão.** No Intune, deixe os dois em "Nunca".
4. **Operação.** O app do Claude, na aba Code e aberto na pasta do repositório, opera a Domínio com Computer use. As
   aprovações chegam no celular.
5. **Uso do plano.** Meça o consumo do Max num fechamento inteiro. O piloto diz se o Max 5x basta.

**Se o teste 2 falhar:**
- manter a conexão aberta e minimizada num computador do escritório que fique ligado, com a chave de registro
  `RemoteDesktop_SuppressWhenMinimized = 2` no cliente de área de trabalho remota;
- ou ir para o plano B.

## Plano B e o que evitar

| Opção | Sistema | R$/mês | Quando usar |
|---|---|---|---|
| **Windows 365 Enterprise 4/16/128** (recomendada) | Windows 11 | 377,90 + Business Premium | Primeira escolha |
| Azure VM D4s_v5, Brazil South, como host pessoal do Azure Virtual Desktop | Windows 11 | ~1.330 (estimativa) | Se a sessão desconectada falhar no Windows 365. Ali o `tscon` é comprovado. Confira o preço na calculadora do Azure. |
| Mini PC com Windows 11 Pro no escritório, com nobreak | Windows 11 | só a compra | Sem problema de tela desconectada, mas depende da energia e da internet do escritório |
| Windows 365 Business 4/16/128 | Windows 11 | 320,60 | **Evitar:** hiberna depois de 1 h ocioso |
| AWS t3.xlarge / m7i-flex.xlarge (São Paulo) | Windows Server | 1.401 / 1.923 | **Evitar:** caro, Windows Server, sem Windows 11 em hardware compartilhado |
| Google e2-standard-4 (São Paulo) | Windows Server | 1.606 | **Evitar:** mesmos motivos |
| Oracle E5.Flex 2 OCPU/16 GB (São Paulo) | Windows Server | 1.112 | Só se o Windows Server for testado e aprovado |
| Locaweb, Magalu Cloud, Vultr | Windows Server | varia | Servem para scripts e outros robôs, não para o agente |

Sobre os preços:
- Windows 365 e Oracle estão nas tabelas dos próprios fabricantes, em reais.
- AWS e Google foram convertidos a R$ 5,20 por dólar e cobram IOF.
- O Azure é estimativa, porque a API de preços não abriu daqui.
- Evite instâncias "burstable" (t3, B-series) sob carga 24 horas.

## Montagem (Sessão 1)

1. **Licenças.** O Cloud PC fica no nome da pessoa que supervisiona o agente. É ela que aprova pelo celular, e a conta
   Pro ou Max do Claude deve ser dela também. Atribua o Business Premium, se precisar, e o Windows 365 Enterprise
   Premium.
2. **Provisionamento no Intune:**
   - região Brazil South;
   - imagem Windows 11 Enterprise;
   - administrador local durante a montagem;
   - limites de sessão ociosa e desconectada em "Nunca".
3. **Programas:**
   - plugin da Domínio Web;
   - Google Chrome com a extensão Claude in Chrome;
   - app desktop do Claude (instalador `.msix`), com *Computer use* ligado em Configurações → App desktop → Computer
     use;
   - Python 3 e Git;
   - este repositório em `C:\automacao-fiscal`.
4. **Envio ao Acessórias** pela API do e-Contínuo (`ferramentas/acessorias.py`), sem instalar o robô, ou com a pasta
   do e-Contínuo, se preferirem.
5. **Certificados.**
   - Só os A1 necessários, marcados como não exportáveis.
   - Certificado A3 em token não funciona na nuvem.
6. **Tela.** Resolução fixa (1920 × 1080), sem bloqueio de tela, sem proteção de tela e sem suspensão.
7. **Privacidade da conta do Claude.** Desligue o uso das conversas para treinamento de modelos, nas configurações de
   privacidade. É uma conta de consumidor, e os dados são de clientes.
8. **Desconectar sem apagar a tela.** Crie um atalho, executado como administrador, que roda:
   ```
   for /f "skip=1 tokens=3" %s in ('query user %USERNAME%') do tscon %s /dest:console
   ```
   Num arquivo `.bat`, use `%%s`. Teste no primeiro mês.
9. **Backup.**
   - Use os pontos de restauração do Windows 365.
   - Copie a pasta `trabalho/` para o OneDrive ou SharePoint do escritório. Ela tem dados de clientes e nunca vai para
     o Git.

## Custos no business case

| Item | R$/mês | Observação |
|---|---|---|
| Cloud PC Windows 365 Enterprise Premium | 377,90 | Tabela Microsoft Brasil, sem impostos |
| Microsoft 365 Business Premium | ~126 | Só se o escritório ainda não tiver. Preço de revenda, a conferir. |
| Plano Claude Max 5x | ~540 | US$ 100 a R$ 5,20, com IOF. O Max 20x custa o dobro. O piloto mede qual basta. |
| Integra Contador | 0,96 por DAS | Já contratado |

Com 63 prestadoras, 2 h por empresa hoje e supervisor de 20 h por mês:

| | Nível 2 | Nível 3 |
|---|---|---|
| Custo anual do agente | R$ 22,7 mil | R$ 22,7 mil |
| Capacidade liberada | 0,5 FTE | 0,7 FTE |
| Resultado líquido anual, antes das análises | R$ 11,5 mil | R$ 25,3 mil |

A calculadora da página tem esses mesmos campos.

## Outras automações no mesmo servidor

- **Scripts sem tela** (Python, APIs, downloads de XML) podem rodar no mesmo Cloud PC.
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
