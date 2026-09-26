# 02 · Importação das notas na Domínio

**Objetivo:** escriturar na Escrita Fiscal todos os documentos da etapa 1, com o acumulador certo.

## Passo a passo
Tudo nesta etapa é feito **na tela da Domínio**, com computer use.

1. Na Domínio Web, selecione a empresa pelo código e a competência. [MAPEAR] Tela de troca de empresa.
2. Abra a importação de XML da Escrita Fiscal. [MAPEAR] Caminho exato do menu.
3. Aponte a pasta dos XML. Dentro da Domínio Web o disco local aparece como `M:`. [MAPEAR] Confirmar o caminho.
4. Importe primeiro as saídas, depois as entradas e por último os serviços. [MAPEAR] Ordem e opções usadas no
   escritório.
5. Trate as mensagens da importação:
   - **Acumulador não relacionado ao CFOP.** Procure em `config/acumuladores.csv` [a montar juntos]. Se não estiver
     lá, pare e pergunte, porque é uma regra nova.
   - **Produto ou participante novo.** [MAPEAR] Como o escritório cadastra.
   - **Nota já importada.** Não importe de novo e registre no log.
6. Tire um print da tela final com a quantidade importada.

## Alternativa sem tela: Rotinas Automáticas
A própria Domínio importa XML sozinha pelas **Rotinas Automáticas**:
- a configuração fica em Arquivos > Rotinas Automáticas, aba Importação;
- o agendamento fica em Movimentos > Rotinas Automáticas;
- a origem pode ser uma pasta ou a API Onvio BR Accounting;
- o computador precisa estar ligado e o módulo aberto na hora da rotina.

Com a rotina ativa, o papel do agente nesta etapa é **conferir** se a importação aconteceu. [Confirmar na sessão:
estes caminhos vêm da central de soluções da Domínio.]

## Quando parar
- Erro de sistema, tela diferente da descrita ou importação parcial.
- Qualquer mudança em cadastro ou configuração de acumulador. Só com aprovação.

## Evidência
Print da conclusão e quantidade importada registrada no `log.md`.
