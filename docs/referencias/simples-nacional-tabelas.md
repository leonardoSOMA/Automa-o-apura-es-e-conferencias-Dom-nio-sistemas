# Simples Nacional: tabelas e regras usadas pelo agente

Levantamento de 26/09/2026. As páginas do planalto.gov.br não abriram direto. A conferência foi feita com cópias
literais do texto compilado da LC 123/2006 e do DOU, mais busca na web (fontes no fim).

## 2018 a 2026: tabelas em uso (`ferramentas/das_simples.py`)

As 30 linhas (5 anexos × 6 faixas) foram conferidas uma a uma: alíquota nominal, parcela a deduzir e repartição. Cada
repartição soma 100,00%. As faixas incluem o limite superior ("até 180.000,00", "de 180.000,01 a 360.000,00"...).

### Regras especiais confirmadas

- **Teto de 5% do ISS** (art. 18 §1º-B, I). Vale para qualquer faixa, mas com as tabelas atuais só é atingido na
  5ª faixa dos Anexos III (acima de 14,92537%) e IV (acima de 12,5%).
  - Anexo III: o excedente vai para IRPJ 6,02 · CSLL 5,26 · COFINS 19,28 · PIS 4,18 · CPP 65,26.
  - Anexo IV: o excedente vai para IRPJ 31,33 · CSLL 32,00 · COFINS 30,13 · PIS 6,54.
- **Arredondamento** (§1º-B, II). Se a soma dos percentuais não fechar a alíquota efetiva por um centésimo, a diferença
  vai para o tributo de maior participação na faixa. A ferramenta compara com tolerância de R$ 1,00.
- **Não há piso de 2% para o ISS no DAS.** No início da 2ª faixa do Anexo III ele fica em 1,92%. O 2% só aparece na
  retenção do primeiro mês de atividade e no limite de benefícios municipais (LC 116, art. 8º-A).
- **RBT12 zero:** usa R$ 1,00, o que dá a alíquota nominal da 1ª faixa (CGSN 140, art. 21).
- **Início de atividade** (CGSN 140, art. 22):
  - no 1º mês, a receita do mês × 12;
  - do 2º ao 12º mês, a média dos meses **anteriores** × 12.
  - No ano de início, limite e sublimite são proporcionais: R$ 400 mil e R$ 300 mil por mês.
- **Segregação** (art. 18 §§4º-A, 12 e 14): o percentual excluído some e não é redistribuído.
  - ICMS-ST retido ou antecipação com encerramento: tira o ICMS.
  - Monofásico: tira PIS e COFINS.
  - Exportação: tira COFINS, PIS, IPI, ICMS e ISS.
  - ISS retido: tira o ISS.
  - ISS devido a outro município: continua no DAS.
- **Exportação:** o PGDAS-D separa o RBT12 do mercado interno e do externo (art. 3º §15).
- **Sublimite de R$ 3,6 mi** (mantido para 2026 em todas as UFs):
  - **RBT12 na faixa 6 e empresa não impedida.** Os federais usam a faixa 6. ICMS e ISS entram no DAS pela alíquota
    efetiva da 5ª faixa, com o teto de 5% do ISS.
  - **Receita do ano passa de R$ 3,6 mi no mês.** Sobre o excedente do mês, ICMS e ISS usam a alíquota efetiva da
    5ª faixa calculada sobre R$ 3,6 mi.
  - **Impedimento.** Começa no mês seguinte ao que a receita do ano passar de R$ 4,32 mi; caso contrário, em janeiro.
    Impedida, a empresa paga ICMS e ISS fora do DAS.
  - A ferramenta calcula só os federais na faixa 6 e avisa para conferir o resto manualmente.

## 2027 e 2028: tabelas com CBS e IBS (a carregar e validar antes de fevereiro/2027)

Fontes: LC 214/2025 (art. 519, Anexos XVIII a XXII), alterada pela LC 227/2026, e Res. CGSN 190/2026 (DOU
10/08/2026, vigência 01/01/2027). **Ainda não estão na ferramenta.** Conferir com o texto oficial antes de usar.

Alíquota nominal e parcela a deduzir das faixas 1 a 5 são as mesmas de 2026. A CBS substitui PIS e COFINS e aparece
uma pequena parcela de IBS. Repartição em % (IRPJ; CSLL; CBS; CPP; IPI; ICMS; ISS; IBS):

```
I   f1-f2  5,50; 3,50; 15,33; 41,50; -;     34,00; -;     0,17
I   f3-f5  5,50; 3,50; 15,33; 42,00; -;     33,50; -;     0,17
I   f6     nominal 18,90% · PD 378.000 · 13,58; 10,06; 34,02; 42,34
II  f1-f5  5,50; 3,50; 13,85; 37,50; 7,50;  32,00; -;     0,15
II  f6     nominal 29,90% · PD 720.000 · 8,53; 7,53; 25,22; 23,59; 35,13
III f1     4,00; 3,50; 15,43; 43,40; -; -; 33,50; 0,17
III f2     4,00; 3,50; 16,91; 43,40; -; -; 32,00; 0,19
III f3-f4  4,00; 3,50; 16,41; 43,40; -; -; 32,50; 0,19
III f5     4,00; 3,50; 15,43; 43,40; -; -; 33,50; 0,17
III f6     nominal 32,90% · PD 648.000 · 35,09; 15,04; 19,29; 30,58
IV  f1     18,80; 15,20; 21,26; -; -; -; 44,50; 0,24   (CPP fora do DAS)
IV  f2     19,80; 15,20; 24,73; -; -; -; 40,00; 0,27
IV  f3     20,80; 15,20; 23,74; -; -; -; 40,00; 0,26
IV  f4     17,80; 19,20; 22,75; -; -; -; 40,00; 0,25
IV  f5     18,80; 19,20; 21,76; -; -; -; 40,00; 0,24
IV  f6     nominal 32,90% · PD 828.000 · 53,71; 21,59; 24,70
V   f1     25,00; 15,00; 16,96; 28,85; -; -; 14,00; 0,19
V   f2     23,00; 15,00; 16,96; 27,85; -; -; 17,00; 0,19
V   f3     24,00; 15,00; 17,95; 23,85; -; -; 19,00; 0,20
V   f4     21,00; 15,00; 18,94; 23,85; -; -; 21,00; 0,21
V   f5     23,00; 12,50; 16,96; 23,85; -; -; 23,50; 0,19
V   f6     nominal 30,40% · PD 540.000 · 35,10; 15,54; 19,78; 29,58
```

**Teto do ISS em 2027 e 2028, repartição do excedente:**
- Anexo III f5: IRPJ 6,02 · CSLL 5,26 · CBS 23,20 · CPP 65,26 · IBS 0,26.
- Anexo IV f5: IRPJ 31,33 · CSLL 32,00 · CBS 36,27 · IBS 0,40.

**O que mais muda em 2027:**
- O RBT12 passa a ser os 12 meses encerrados no mês anterior ao anterior (a apuração 01/2027 usa 12/2025 a 11/2026).
- Acaba o regime de caixa.
- A receita acima do sublimite ou do limite passa a usar as alíquotas efetivas normais.
- A indústria passa ao Anexo I, exceto produtos ainda sujeitos a IPI, que ficam no Anexo II.
- Na exportação, saem IBS, CBS, IPI, ICMS e ISS.
- **Simples híbrido:** quem recolhe IBS/CBS pelo regime regular exclui as parcelas de CBS/IBS do DAS (CGSN 140, art.
  22-A). A janela da opção foi de 01 a 30/09/2026 (CGSN 186/2026).
- Início de atividade: meses 1 e 2 pela 1ª faixa; meses 3 a 13 pela média × 12.
- DAS arredondado para cima a partir de meio centavo, com mínimo de R$ 0,01 (art. 45-A).
- De 2029 a 2032, ICMS e ISS ficam com 90/80/70/60% da sua parcela e o resto vai para o IBS. O teto do ISS cai para
  4,5/4/3,5/3%. Em 2033 só resta o IBS.

**Pontos a conferir no texto oficial:**
- Na nota de ICMS da faixa 6 do Anexo II, a CGSN 190 publicou números do Anexo III (21% / 125.640 / 33,5%). O
  esperado é 14,70% / 85.500 / 32%.
- A faixa 6 do Anexo I a partir de 2029 aparece como 18,90%, mas a LC 214 diz 19,00%.

## Fontes

- LC 123/2006 compilada: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm
- LC 214/2025 e LC 227/2026: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm · https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp227.htm
- Res. CGSN 140/2018 (anexos na Receita): https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=92278
- Res. CGSN 190/2026: https://www.legisweb.com.br/legislacao/?id=499102
- Res. CGSN 186/2026: https://www.in.gov.br/web/dou/-/resolucao-cgsn-n-186-de-9-de-abril-de-2026-700230741
- Sublimite 2026 (Fenacon): https://fenacon.org.br/noticias/simples-nacional-sublimite-de-icms-e-iss-e-mantido-em-r-36-milhoes-para-2026/
- ISS abaixo de 2% no Simples (CNM/PGFN): https://cnm.org.br/comunicacao/noticias/cnm-questiona-pgfn-sobre-aliquota-de-iss-menor-que-2-permitida-pelo-simples-nacional
