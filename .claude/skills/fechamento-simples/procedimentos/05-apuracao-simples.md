# 05 · Apuração do Simples Nacional

**Objetivo:** apurar o Simples na Domínio e conferir o valor com um recálculo independente.

## Passo a passo
1. Na Domínio, rode a apuração da competência (imposto **44 · Simples Nacional**). [MAPEAR] Tela e opções usadas.
2. Emita o relatório de cálculo em **Relatórios > Impostos > Simples Nacional** e salve na pasta de trabalho. Confira:
   - receita do mês por tipo: revenda normal, com ST, monofásico, serviços, exportação, ISS retido;
   - RBT12, anexo e faixa.
3. Recalcule com a ferramenta:
   ```
   python ferramentas/das_simples.py --rbt12 <RBT12> --anexo I --receita normal=<valor> --receita st=<valor> --receita monofasico=<valor>
   ```
   Use as mesmas receitas segregadas da Domínio. A ferramenta mostra a alíquota efetiva, o valor por tributo e o DAS.
4. Compare o DAS da Domínio com o recálculo. A tolerância é de R$ 1,00.
5. Verifique os alertas:
   - RBT12 acima de 80% do sublimite (R$ 3,6 mi) ou do limite (R$ 4,8 mi);
   - fator R perto de 28% nos serviços;
   - DAS com variação acima de 30% em relação à média de 3 meses.

## Quando parar
Recálculo diferente da Domínio, qualquer alerta acima ou receita segregada que não bate com os itens das notas.

## Evidência
Relatório da apuração e saída do `das_simples.py` salvos na pasta de trabalho.
