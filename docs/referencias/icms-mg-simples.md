# ICMS de MG nas compras interestaduais do Simples: referência do agente

Levantamento de 26/09/2026. Os sites da SEF/MG, do Confaz e de legislação não abriram daqui, e **nenhum texto oficial
foi lido na íntegra**. Tudo vem de trechos de busca de páginas da SEF/MG, de calendários fiscais de 2026 e de notícias.
Por isso:
- a configuração `config/uf/MG.json` é um **rascunho**;
- a calculadora se recusa a usá-la até um contador validar (lista no fim).

## 1. Antecipação do Simples (compra de outro estado para comercializar)

**Continua valendo em 2026 (M).**
- **Base legal:**
  - RICMS/2023 (Decreto 48.589/2023, em vigor desde 01/07/2023);
  - fato gerador: art. 3º, VII;
  - base de cálculo: art. 4º, XII, com o inciso VI e o § 7º;
  - LC 123/2006, art. 13, § 1º, XIII, "g", 2.
- **Alcance:** mercadoria para comercializar, industrializar ou usar na prestação de serviço. Insumo de indústria
  **entra**, o que importa se a cerâmica fabricar. Não encontrei redução para o Simples nem exclusão por faturamento.
- **Não se aplica:**
  - a mercadoria sujeita a ST, porque vale a ST;
  - ao uso e consumo ou ativo, porque vale o DIFAL;
  - a operação interna isenta;
  - a empresa acima do sublimite.
- **Base dupla desde 01/01/2016** (Orientação DOLT/SUTRI 002/2016; nota técnica "Malha SN Antecipação") (A). Exemplo da
  SEF, que também é teste da calculadora:
  - 1.000 − 120 = 880;
  - 880 ÷ 0,82 = 1.073,17;
  - × 18% = 193,17;
  - − 120 = **R$ 73,17**.
- **Crédito:** alíquota interestadual × valor da operação, **mesmo quando o fornecedor do Simples não destaca ICMS**
  (IN SUTRI 001/2016, art. 2º, III) (A). A alíquota é 12% para MG, ou 4% para importados.
- **O que entra na base (M):**
  - IPI fica **fora**, porque é revenda entre contribuintes;
  - frete, seguro e outras despesas cobrados na NF-e **entram**;
  - frete FOB em CT-e separado: regra não confirmada.
- **Competência:** a data de emissão da NF-e (IN SUTRI 001/2021) (M).
- **STF Tema 517 (RE 970.821):** julgado constitucional o diferencial cobrado do Simples, com trânsito em julgado em
  10/06/2022. A ADI 6030 reafirmou (A).
  - Risco aberto: a base dupla contra a vedação de "agregação de valor" da LC 123. Não encontrei decisão (B).

## 2. ST quando o fornecedor não reteve

- **Onde estão a lista e as MVAs:** RICMS/2023, **Anexo VII, Parte 2**, por capítulo (Capítulo 10 = materiais de
  construção). Alterado pelos Decretos 49.233/2026 e **49.281/2026** (DOE 29/08/2026) (A para o local).
- **MVA ajustada** = [(1 + MVA) × (1 − alíquota interestadual) ÷ (1 − alíquota interna)] − 1 (A). A calculadora já
  aplica.
- **Bicicletas e peças (8712, 8714, pneus 4011.50 e câmaras 4013.20):**
  - na ST em MG pelo **Protocolo 203/2009** (MG, RJ, SC, PR);
  - o **Prot. 29/2009 (MG–SP) foi revogado pelo Prot. 110/2026 a partir de 01/10/2026**;
  - item e MVA **não confirmados** (M-B).
- **Cerâmica (6907, 6910):**
  - Capítulo 10;
  - o Prot. 32/2009 (MG–SP) e o Decreto 49.281/2026 tiraram SP do **item 64.0**;
  - item e MVA **não confirmados** (M-B).
- **SP sai da ST em vários segmentos em 01/10/2026** (Protocolos 90 a 123/2026; Despacho Confaz 43/2026) (M). A partir
  de outubro, compras de SP tendem a chegar **sem ST retida**. Se a mercadoria continuar na ST em MG, o comprador
  recolhe na entrada. **Isso afeta a loja de bicicletas já na competência 10/2026.**
- **Na calculadora:**
  - enquanto as MVAs não forem preenchidas, os NCMs acima estão em `ncm_a_confirmar`;
  - a calculadora avisa e calcula esses itens sem ST, o que pode dar valor a menor.

## 3. DIFAL (uso e consumo, ativo)

- **Base dupla com IPI:** tira o ICMS interestadual do valor, divide pela alíquota interna e paga a diferença positiva
  (LC 123, art. 13, § 1º, XIII, "h"; RICMS/2023, art. 4º, VI e § 7º). Sem isenção para o Simples (M).
- **FEM (+2 pontos):** só para a lista do art. 12-A da Lei 6.763/1975, com bebidas, fumo, armas, perfumes e
  cosméticos, ração pet, celulares e câmeras. **Bicicletas e cerâmicas não estão na lista** (M-B).

## 4. Alíquota interna

18% geral. Não encontrei alíquota ou base reduzida para os NCMs do piloto (M).

## 5. Na Domínio

Existe a solução **8368, "MG – Como calcular imposto 27-ICMS Antecipado por Nota?"**, o que indica o imposto 27 por NF-e
(M/B). O código do DIFAL e a configuração serão mapeados na Sessão 4.

## 6. Vencimentos e guia

| Guia | Vencimento | Base |
|---|---|---|
| Antecipação do Simples | **dia 20 do 2º mês** após a emissão da NF-e (NF-e de 09/2026 vence em 20/11/2026) | Decreto 48.423/2022; RICMS/2023, art. 112, § 7º, III (A) |
| ST e DIFAL declarados na DeSTDA | dia 2 do 2º mês, ou o próximo dia útil | RICMS/2023, art. 112, § 7º, II, "c" (M) |

- A DeSTDA vence até o dia 28 do mês seguinte.
- A guia é o **DAE, emitido no SIARE**. Códigos de receita não confirmados. Não achei emissão em lote nem API (B).

## Lista de conferência do contador (antes de preencher `validado_em`)

1. **Texto atual do RICMS/2023**, consolidado até o Decreto 49.245/2026:
   - art. 3º, VII;
   - art. 4º, VI, XII e § 7º;
   - art. 112, § 7º.

   Confirmar a base dupla e o crédito: ICMS destacado ou alíquota interestadual × valor.
2. **MVAs do Anexo VII, Parte 2** para 8712, 8714, 4011.50, 4013.20, 8512.10, 6907 e 6910, com capítulo, item e estados
   que retêm. Preencher `mva_por_ncm`.
3. **ST depois de 01/10/2026:** se bicicletas, peças e cerâmica seguem na ST em MG, e se SC, RJ e PR seguem retendo.
4. **ST paga pelo comprador do Simples na entrada:** prazo e ICMS próprio a deduzir quando o fornecedor é do Simples.
5. **IPI e frete** na base da antecipação: IPI fora; frete na NF-e dentro; e o CT-e separado?
6. **18% e o FEM** para os NCMs do piloto.
7. **Códigos de receita** do DAE e a DeSTDA em 2026.
8. **A cerâmica é indústria ou comércio?** Há benefício no DIFAL de ativo industrial?
9. **Sublimite:** cada empresa está abaixo?
10. **Um mês real** conferido contra a fórmula da SEF e contra o imposto 27 da Domínio.
11. **PGDAS-D da loja de bicicletas:** receita de mercadoria com ST segregada, para não pagar o ICMS duas vezes.

## Fontes (lidas por trechos de busca)

- RICMS/2023 consolidado: https://www.fazenda.mg.gov.br/empresas/legislacao_tributaria/ricms_2023_seco/regulamento2023seco.pdf
- Decreto 48.589/2023: https://www.fazenda.mg.gov.br/empresas/legislacao_tributaria/decretos/2023/d48589_2023.html
- Anexo VII (ST): https://www.fazenda.mg.gov.br/empresas/legislacao_tributaria/ricms_2023_seco/anexovii2023_2.html
- Cálculo da ST (SEF): https://www.fazenda.mg.gov.br/empresas/substituicao_tributaria/stminasgerais.html
- IN SUTRI 001/2016: https://www.fazenda.mg.gov.br/empresas/legislacao_tributaria/instrucoes_normativas/2016/insutri001_2016.html
- IN SUTRI 001/2021: https://www.fazenda.mg.gov.br/empresas/legislacao_tributaria/instrucoes_normativas/2021/insutri001_2021.html
- Orientação DOLT/SUTRI 002/2016: https://www.fazenda.mg.gov.br/empresas/legislacao_tributaria/orientacao/orientacao_002_2016.pdf
- Nota técnica Malha SN Antecipação: https://www.fazenda.mg.gov.br/empresas/autorregularizacao/Nota-Tecnica-Simples-Nacional-Antecipacao-ICMS.pdf
- Decreto 48.423/2022 (Fecomércio MG): https://fecomerciomg.org.br/noticias/governo-de-minas-estende-prazo-de-recolhimento-do-icms-para-empresas-optantes-pelo-simples-nacional/
- STF Tema 517: https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=517
- Protocolo ICMS 203/2009: https://www.confaz.fazenda.gov.br/legislacao/protocolos/2009/pt203_09
- Protocolos de setembro/2026: https://www.contabeis.com.br/noticias/79437/confaz-publica-34-protocolos-com-mudancas-no-icms-st-veja-o-que-muda/
- Decreto 49.281/2026: https://mgcontecnica.com.br/2026/08/31/estado-de-minas-gerais-altera-aplicacao-da-substituicao-tributaria-nas-operacoes-de-diversos-segmentos/
- Domínio, solução 8368: https://suporte.dominioatendimento.com/central/faces/solucao.html?codigo=8368
