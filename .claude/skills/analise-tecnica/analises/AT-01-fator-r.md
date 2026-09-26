# AT-01 · Fator R e anexo (III × V)

**Pergunta:** a empresa está sendo tributada no anexo certo, dado o que ela fatura e a folha que tem? E a configuração
da Domínio vai continuar certa quando o fator r mudar?

## Regra
A base legal está conferida em `docs/referencias/fator-r.md`.
- **Atividades sujeitas** (LC 123, art. 18 §§5º-I e 5º-M) vão para o **Anexo III** quando o fator r é **igual ou
  maior que 28%**. Abaixo disso, vão para o **Anexo V**.
- **Cálculo do fator r:** folha paga nos 12 meses anteriores ÷ receita bruta dos 12 meses anteriores (§5º-K).
- **Valores zero** (Res. CGSN 140, art. 26):
  - sem folha e com receita, r = 0,01 e a atividade vai para o Anexo V;
  - com folha e sem receita, r = 0,28.
- **Atividades não sujeitas** (Anexo III direto, Anexo IV) não mudam de anexo, seja qual for a folha.
- **A partir do PA 01/2027**, a janela de 12 meses termina um mês antes. A ferramenta avisa.

## Dados a levantar
As telas marcadas com (M) vêm do suporte da Domínio e são confirmadas no mapeamento.

1. **CNAEs da empresa**, principal e secundários: `python ferramentas/cnpj.py <CNPJ>`.
   - Cada um é classificado pela tabela `config/tabelas/cnae_anexo.csv`: S sujeito, N não sujeito, D depende do
     serviço.
   - Se o CNAE não está na tabela, avise: a pessoa do fiscal classifica e a tabela é atualizada.
2. **Acumuladores de receita de serviço** (M): Arquivos > Acumuladores > Impostos > 44 > Definições.
   - Anote o Anexo / Seção / Tabela.
   - Anote se a opção "Efetuar a troca automática para os anexos III ou V…" está marcada. Marcada é `"fator_r": "S"`;
     fixa é `"N"`.
3. **Notas do período:**
   ```
   python ferramentas/nfse.py resumo <pasta> --cnpj <CNPJ>
   ```
   O resumo traz a receita por código de serviço, o CNAE da nota (só no ABRASF) e a discriminação.
4. **Folha dos 12 meses e RBT12** (M): Movimentos > Outros > Simples Nacional > Valor da Folha.
   - Compare com a Domínio Folha ou com o eSocial.
   - Folha zero só vale como fato depois de confirmada com o DP. Nesse caso, use `"folha_confirmada": true`.
5. **Anexo aplicado de fato** (M): Relatórios > Impostos > Simples Nacional, com a opção "memória de cálculo".
   - Há um bloco por atividade, com Anexo / Seção / Tabela, receita e alíquota.
   - No PGDAS-D já transmitido, o tipo de atividade confirma:
     - 10/11/12 são sujeitos ao fator r;
     - 13/14/15 são Anexo III sem fator r;
     - 16/17/18 são Anexo IV.
6. **Início de atividade** e, se a empresa apura por caixa, a receita dos 12 meses por competência
   (`rbt12_fator_r`).

## Execução
```
python ferramentas/analise_fator_r.py <dados.json>
```
A ferramenta gera:
- os fatos e o sinal de cada hipótese;
- a configuração da Domínio que causa ou vai causar erro;
- o impacto em reais: o DAS no Anexo III × Anexo V com a mesma receita;
- a folha que leva o fator r a 28%.

O formato do `dados.json` está no início do arquivo da ferramenta.

## Hipóteses a testar (sempre todas)

| # | Hipótese | Reforça | Enfraquece |
|---|---|---|---|
| H1 | **Acumulador errado:** atividade sujeita ao fator r configurada como Anexo III fixo | Código de serviço e discriminação de atividade sujeita; fator r abaixo de 28%; apuração no Anexo III | Notas emitidas para atividade não sujeita |
| H2 | **Outra atividade, não sujeita:** a empresa tem CNAE do Anexo III direto e fatura por ele | Código de serviço e discriminação batem com o CNAE não sujeito | Discriminação descreve serviço sujeito, como consultoria, desenvolvimento de software, engenharia ou publicidade |
| H3 | **CNAE desatualizado:** o serviço faturado não está entre os CNAEs do CNPJ | Não há CNAE que corresponda ao serviço | — |
| H4 | **Fator r ≥ 28%:** Anexo III correto. Se a apuração usou o V, houve pagamento a maior. | Folha ÷ receita ≥ 28% com a folha completa | Folha incompleta |
| H5 | **Folha errada na Domínio:** fator r calculado com folha zerada ou incompleta | Folha da apuração diferente da Domínio Folha ou do eSocial | Folha conferida com o DP |
| H6 | **Início de atividade:** menos de 13 meses, com regra própria | Data de abertura no CNPJ | — |

**Receita mista no mês** (notas de atividade sujeita e não sujeita): separe a receita por atividade antes de concluir.
Cada parte vai para o seu acumulador.

## Como concluir (exemplos de redação)
- **Erro provável.**
  - Exemplo: "As notas 101 a 118 de 09/2026 descrevem desenvolvimento de software, atividade sujeita ao fator r. O
    fator r é 12%, o acumulador 50 está fixo no Anexo III e a apuração usou o III. No Anexo V, o DAS seria R$ X maior no
    mês."
  - Ação: marcar a troca automática no acumulador e avaliar a retificação dos períodos afetados. Decide o sócio.
- **Oportunidade.**
  - Exemplo: "O fator r é 31% e a apuração usou o Anexo V. Foi pago R$ Y a maior no mês."
  - Ou: "A empresa só fatura treinamento (8599-6/04), que não é sujeito, e a apuração usou o Anexo V."
  - Ação: corrigir e avaliar a retificação com pedido de restituição. Decide o sócio.
- **Risco latente.**
  - Exemplo: "O acumulador 50 está fixo no Anexo III. Hoje o fator r é 31% e o DAS está certo. Se a folha dos 12
    meses ficar abaixo de R$ 100.800,00, a Domínio continua no III e o DAS sai a menor."
  - Ação: marcar a troca automática. Não muda o DAS de hoje. Decide o coordenador.
- **Situação justificada.** "As notas descrevem [serviço] do CNAE [código], que não é sujeito ao fator r. O acumulador
  no Anexo III está certo."
- **Indício, falta informação.** "A folha dos 12 meses está zerada na Domínio. Se a empresa não tem folha nem
  pró-labore, o fator r é 0,01 e o DAS no Anexo V seria R$ X maior. Quem confirma: DP."

## Saída
Parecer em `pareceres/AT-01.md`, no formato do SKILL.md, e uma linha no relatório de retorno.
