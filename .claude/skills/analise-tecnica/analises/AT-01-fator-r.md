# AT-01 · Fator R e anexo (III × V)

**Pergunta:** a empresa está sendo tributada no anexo certo, dado o que ela fatura e a folha que tem?

## Regra
A base legal está conferida em `docs/referencias/fator-r.md`.
- Atividades do Anexo V sujeitas ao fator r vão para o **Anexo III** quando o fator r for **igual ou maior que 28%**.
- O fator r é a folha de salários dos 12 meses anteriores dividida pela receita bruta dos 12 meses anteriores.
- Atividades que não são sujeitas ao fator r (Anexo III direto, Anexo IV) não mudam de anexo, seja qual for a folha.

## Dados a levantar
1. **CNAEs da empresa**, principal e secundários: `python ferramentas/cnpj.py <CNPJ>`. Cada um é classificado pela
   tabela `config/tabelas/cnae_anexo.csv`.
2. **Configuração da Domínio:** anexo e tipo de atividade de cada acumulador de receita de serviços.
   [MAPEAR] Tela ou relatório que mostra isso.
3. **Notas do período:**
   ```
   python ferramentas/nfse.py resumo <pasta> --cnpj <CNPJ>
   ```
   O resumo traz a receita por código de serviço, o CNAE informado na nota (quando houver) e a discriminação.
4. **Folha dos 12 meses anteriores e RBT12.** [MAPEAR] Relatório da Domínio Folha, e o RBT12 da apuração.
5. **Anexo aplicado de fato:** relatório de apuração do Simples (Relatórios > Impostos > Simples Nacional).

## Execução
```
python ferramentas/analise_fator_r.py <dados.json>
```
Gera os fatos, os sinais de cada hipótese e o impacto em reais: DAS no Anexo III × Anexo V com a mesma receita.

## Hipóteses a testar (sempre todas)

| # | Hipótese | Reforça | Enfraquece |
|---|---|---|---|
| H1 | **Acumulador errado:** atividade sujeita ao fator r configurada como Anexo III fixo | Código de serviço e discriminação de atividade sujeita; fator r abaixo de 28%; apuração no Anexo III | Notas emitidas para atividade não sujeita |
| H2 | **Outra atividade, não sujeita:** a empresa tem CNAE do Anexo III direto e fatura por ele | Código de serviço e discriminação batem com o CNAE não sujeito | Discriminação descreve serviço sujeito, como consultoria, desenvolvimento de software, engenharia ou publicidade |
| H3 | **CNAE desatualizado:** o serviço faturado não está entre os CNAEs do CNPJ | Não há CNAE que corresponda ao serviço | — |
| H4 | **Fator r ≥ 28%:** Anexo III correto. Se a apuração usou o V, houve pagamento a maior. | Folha ÷ RBT12 ≥ 28% com a folha completa | Folha incompleta |
| H5 | **Folha errada na Domínio:** fator r calculado com folha zerada ou incompleta | Folha da apuração diferente da Domínio Folha ou do eSocial | — |
| H6 | **Início de atividade:** menos de 13 meses, com regra própria | Data de abertura no CNPJ | — |

## Como concluir (exemplos de redação)
- **Erro provável.** "As notas 101 a 118 de 09/2026 descrevem desenvolvimento de software, atividade sujeita ao fator
  r. O fator r é 12% e a apuração usou o Anexo III. No Anexo V, o DAS seria R$ X maior no mês." Ação: corrigir o
  acumulador e avaliar a retificação dos períodos afetados. Decide o sócio.
- **Oportunidade.** "O fator r é 31% e a apuração usou o Anexo V. Foi pago R$ Y a maior no mês." Ação: corrigir e
  avaliar a retificação com pedido de restituição. Decide o sócio.
- **Situação justificada.** "As notas descrevem [serviço] do CNAE [código], que não é sujeito ao fator r. O acumulador
  no Anexo III está correto."
- **Indício, falta informação.** "A folha dos 12 meses não está na Domínio. Sem ela não é possível calcular o fator r.
  Quem tem: DP."

## Saída
Parecer em `pareceres/AT-01.md`, no formato do SKILL.md, e uma linha no relatório de retorno.
