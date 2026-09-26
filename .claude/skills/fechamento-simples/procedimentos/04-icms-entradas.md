# 04 · ICMS nas entradas: antecipação e DIFAL

**Objetivo:** calcular o ICMS devido na entrada das compras de outros estados: antecipação parcial, antecipação com
ST e DIFAL de uso e consumo ou ativo. Depois, conferir com a Domínio.

## Passo a passo
1. Rode a calculadora sobre os XML de entrada:
   ```
   python ferramentas/icms_entradas.py trabalho/<AAAA-MM>/<codigo>/xml/entradas --uf <UF da empresa> --cnpj <CNPJ> --saida trabalho/<AAAA-MM>/<codigo>/icms_entradas
   ```
   Ela usa `config/uf/<UF>.json`. Se o arquivo não existir ou não estiver validado, a calculadora avisa. Nesse caso,
   pare: a legislação da UF precisa ser conferida antes.
2. Leia os avisos da saída:
   - **Finalidade presumida.** A calculadora não sabe se o item é revenda ou uso e consumo. Use o CFOP de entrada
     escriturado na Domínio; se não souber, pergunte.
   - **Alíquota interestadual inferida.** Não havia ICMS destacado na nota.
3. Compare com o que a Domínio calculou, nota a nota. A tolerância é de R$ 1,00 por guia. A Domínio só calcula se
   estiver configurada:
   - impostos: **27 · ICMS Antecipado** (antecipação parcial), **8 · DIFALI** (DIFAL nas compras) e **31 · ICMS ST/AT**
     (antecipação total, documentada para SP);
   - onde se configura: Controle > Parâmetros, na vigência, e Arquivos > Impostos (cálculo por nota ou por produto);
   - os acumuladores de entrada precisam ter esses impostos.

   [MAPEAR] Qual relatório mostra os valores para comparar. Se a Domínio não estiver configurada, o valor da
   calculadora vai para a guia estadual e a configuração entra como sugestão no relatório.
4. Anote no `log.md` os totais: antecipação parcial, antecipação com ST, DIFAL e FCP.

## Quando parar
- Divergência entre a calculadora e a Domínio.
- Item com finalidade incerta que muda o imposto, ou UF sem configuração validada.

## Evidência
`icms_entradas.csv` e `icms_entradas.json` na pasta de trabalho.
