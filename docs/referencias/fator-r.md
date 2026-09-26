# Fator R: referência do agente

Levantamento de 26/09/2026. Como cada fonte foi lida:
- **LC 123/2006:** cópia literal do texto do Planalto, porque o site do Planalto não abriu.
- **Res. CGSN 140/2018 e 190/2026, páginas de suporte da Domínio e manual do PGDAS-D:** lidos só por trechos de busca.
  Por isso aparecem com **(M)**, de confiança média.
- **Códigos de atividade do PGDAS-D:** vêm da tabela de domínio do Integra Contador (SERPRO).

## 1. A regra (LC 123/2006, art. 18)

- **§5º-J.** As atividades do §5º-I "serão tributadas na forma do Anexo III (...) caso a razão entre a folha de salários
  e a receita bruta da pessoa jurídica seja igual ou superior a 28%".
- **§5º-M.** Com a razão "inferior a 28%", vão para o Anexo V as atividades:
  - dos incisos XVI, XVIII, XIX, XX e XXI do §5º-B;
  - de todo o §5º-D.
- **§5º-K.** Entram "os montantes pagos e auferidos nos doze meses anteriores ao período de apuração".
- **§24.** A folha é "o montante pago, nos doze meses anteriores ao período de apuração, a título de remunerações a
  pessoas físicas decorrentes do trabalho, acrescido do montante efetivamente recolhido a título de contribuição
  patronal previdenciária e FGTS, incluídas as retiradas de pró-labore".
- **§25.** Só contam as remunerações informadas à Previdência (antes na GFIP, hoje no eSocial e na DCTFWeb).
- **§26.** Não contam aluguéis nem distribuição de lucros.

### Quem é sujeito ao fator r

| Origem | Atividades |
|---|---|
| §5º-I (Anexo V; III com fator r ≥ 28%) | medicina veterinária; comissaria, despachantes, tradução e interpretação; engenharia, medição, cartografia, topografia, geologia, geodésia, testes, suporte e análises técnicas e tecnológicas, pesquisa, design, desenho e agronomia; representação comercial e intermediação; perícia, leilão e avaliação; auditoria, economia, consultoria, gestão, organização, controle e administração; jornalismo e publicidade; agenciamento, exceto de mão de obra; outras atividades intelectuais, técnicas, científicas, desportivas, artísticas ou culturais que não sejam dos Anexos III ou IV |
| §5º-B, incisos XVI e XVIII a XXI (Anexo III; V com fator r < 28%) | fisioterapia; arquitetura e urbanismo; medicina, inclusive laboratorial, e enfermagem; odontologia e prótese dentária; psicologia, psicanálise, terapia ocupacional, acupuntura, podologia, fonoaudiologia, clínicas de nutrição e de vacinação e bancos de leite |
| §5º-D inteiro (Anexo III; V com fator r < 28%) | administração e locação de imóveis de terceiros; academias de dança, capoeira, ioga, artes marciais e atividades físicas; elaboração e licenciamento de software; páginas eletrônicas; montagem de estandes; laboratórios de análises clínicas e patologia clínica; diagnóstico por imagem; próteses |

**Não são sujeitos:**
- o resto do §5º-B, que fica sempre no Anexo III: ensino, agências de viagem, instalação e manutenção, contabilidade,
  produções culturais e outros;
- **corretagem de seguros** (§5º-B, XVII), que não está na lista do §5º-M;
- o §5º-C (Anexo IV): construção, paisagismo, decoração de interiores, vigilância, limpeza e conservação, advocacia;
- serviços sem previsão expressa nos Anexos IV ou V, que ficam no Anexo III (§5º-F).

### O que entra na folha (M)
- **Entra:** salários, 13º, férias, pró-labore, pagamentos a autônomos, FGTS e contribuição patronal efetivamente
  recolhidos.
- **Não entra:** aluguel, lucros distribuídos, bolsa de estágio, notas de MEI ou de outras empresas.
- **Sem consenso:** a CPP que está dentro do DAS. O escritório decide o critério e registra. O agente usa a folha
  informada na Domínio e aponta quando ela diverge da Domínio Folha ou do eSocial.

## 2. O cálculo (Res. CGSN 140/2018, arts. 25 e 26) (M)

- r = folha paga nos 12 meses ÷ receita bruta dos 12 meses. É recalculado todo mês.
- A receita do fator r é por **competência**, mesmo na empresa que apura por caixa. A ferramenta aceita
  `rbt12_fator_r` para esse caso.
- **Início de atividade (menos de 13 meses):** a folha é proporcionalizada como a RBT12 (art. 22).
  - No 1º mês, vale o valor do mês × 12.
  - Do 2º ao 12º mês, vale a média dos meses anteriores × 12.
- **Valores zero (art. 26):**
  - com folha e sem receita, **r = 0,28**;
  - sem folha e com receita, **r = 0,01**, e a atividade sujeita vai para o Anexo V.

  Uma empresa de serviço sujeito, sem pró-labore e sem empregados, fica no Anexo V. É um erro comum quando o acumulador
  está fixo no III.

### A partir do PA 01/2027 (LC 214/2025 e Res. CGSN 190/2026) (M)
- **Janela de 12 meses.** Passa a ser a dos "12 meses antecedentes ao mês anterior" ao período de apuração. Exemplo: o PA
  05/2027 usa de 04/2026 a 03/2027.
- **Primeiros 2 meses de atividade:** r = 0,28.
- **Regime de caixa:** acaba.
- **Limite de 28%:** continua.

A ferramenta avisa quando a competência é de 2027 em diante. As tabelas de 2027 ainda não estão carregadas; ver
`simples-nacional-tabelas.md`.

## 3. CNAE × anexo

- **Não existe tabela oficial.**
  - Os Anexos VI e VII da Res. CGSN 140 dizem só quem pode optar: CNAE impeditivo ou ambíguo.
  - O anexo depende do **serviço efetivamente faturado**, e o PGDAS-D não pede CNAE.
- As tabelas comerciais divergem nos casos de fronteira, e as cópias abertas encontradas têm erros.
- A tabela do escritório é `config/tabelas/cnae_anexo.csv`. Colunas:
  - `anexo`;
  - `fator_r`: S sujeito, N não sujeito, D depende do serviço;
  - `confianca`: alta quando vem do texto da lei, média quando vem de solução de consulta ou há divergência;
  - `observacao`;
  - `fonte`.
- Uma pessoa do fiscal deve validar a tabela antes da primeira varredura. CNAE que falta vira alerta "sem
  classificação" e deixa a análise em "Indício".
- Casos de fronteira já marcados:
  - 6209-1/00 e 6311-9/00: fator r, mas reparo de hardware é III;
  - 7112-0/00 e 7119-7/99: fator r, mas obra é IV;
  - 7410-2/02, design de interiores: design vai pelo fator r, decoração é IV;
  - 6622-3/00: corretagem de seguros é III, planos de saúde e previdência vão pelo fator r;
  - 8211-3/00 e 8219-9/99: III, com divergência;
  - 7319-0/02, promoção de vendas: III pela SC Cosit 13/2022.

## 4. Na Domínio (M, a confirmar no mapeamento das telas)

As soluções do suporte citadas abaixo estão em `https://suporte.dominioatendimento.com/central/faces/solucao.html?codigo=<nº>`.

| O quê | Onde |
|---|---|
| Parâmetros da empresa | Controle > Parâmetros: imposto 44, ME/EPP, aba do Simples Nacional |
| Anexo do acumulador | Arquivos > Acumuladores > Impostos > 44 > **Definições**: Anexo / Seção / Tabela |
| Troca automática | Na mesma tela: "Efetuar a troca automática para os anexos III ou V quando o fator r for igual/superior ou inferior a 28%". Desmarcada, a apuração avisa (5506). Sem fator r, usa-se uma combinação diferente das do fator r (4630); com fator r, ver 4434. |
| Folha do fator r | Movimentos > Outros > Simples Nacional > **Valor da Folha**, por competência, com os quadros "Valor da Folha" e "INSS/CPP" (4439) |
| Importação da folha | Da Domínio Folha ou do extrato do PGDAS-D (4439). A rotina automática fica em Arquivos > Rotinas Automáticas (11020). |
| Sem folha informada | A apuração avisa "Não existem valores informados…" (3027) |
| Conferência do fator r | Solução 9676 |
| Memória de cálculo | Relatórios > Impostos > Simples Nacional, opção "memória de cálculo" (4415): um bloco por atividade com Anexo / Seção / Tabela, receita e alíquota |
| Receita por acumulador | Relatórios > Acompanhamentos > Resumo por Acumulador (1866) |

## 5. No PGDAS-D

Tipos de atividade de serviço declarados por estabelecimento. Os três códigos de cada linha mudam só pelo ISS: devido a
outro município, devido ao próprio município e retido.

| Códigos | Tipo |
|---|---|
| 10, 11, 12 | Sujeitos ao fator "r" |
| 13, 14, 15 | Não sujeitos ao fator "r" e tributados pelo Anexo III |
| 16, 17, 18 | Anexo IV |
| 9 | Escritório contábil com ISS fixo |
| 29, 30, 31 | Exportação de serviços: sujeitos ao fator r, não sujeitos e Anexo IV |

- **Folha obrigatória.** Com os códigos 10, 11, 12 ou 29, sem a folha a transmissão é recusada ("Existe atividade com
  folha de salário obrigatória").
  - No Integra Contador, a folha vai em `folhasSalario` {pa, valor}, com os 12 meses anteriores.
  - O histórico fica guardado, e em geral só o mês anterior é pedido.
- **O PGDAS-D calcula o r** e aplica o III ou o V sozinho. O extrato mostra "Folha de Salários Anteriores" e "Fator r".
- **O erro aparece no código declarado.**
  - Receita de serviço sujeito declarada em 13, 14, 15 ou 30 equivale a um acumulador fixo no Anexo III.
  - Com fator r abaixo de 28%, o DAS saiu a menor.

## 6. O que o agente procura (AT-01)

| Situação | Conclusão |
|---|---|
| Serviço sujeito (código de serviço e discriminação) declarado como não sujeito, ou acumulador fixo no III, com fator r < 28% | Erro provável: DAS a menor |
| Acumulador fixo no V, ou folha faltando na Domínio, com fator r real ≥ 28% | Oportunidade: DAS a maior |
| Atividade não sujeita apurada no Anexo V | Oportunidade: DAS a maior |
| Configuração errada que hoje não muda o DAS: acumulador fixo no III com fator r ≥ 28%, fixo no V com fator r < 28%, ou troca automática em empresa sem atividade sujeita | Risco latente: corrigir antes que o fator r mude |
| Notas de CNAE não sujeito que a empresa tem (8599-6/04, 7319-0/02, corretagem de seguros), ou regra de início de atividade | Situação justificada |

A ferramenta é `ferramentas/analise_fator_r.py` e o roteiro é
`.claude/skills/analise-tecnica/analises/AT-01-fator-r.md`.

## Fontes

- LC 123/2006, art. 18 (cópia do texto do Planalto): https://github.com/juliopatti/AMLDO/blob/main/data/split_docs/Lcp123/TITULO_0/capitulos/CAPITULO_IV/artigos/artigo_18.txt
- LC 123/2006 (Planalto): https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm
- Res. CGSN 140/2018 compilada: http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=92278&visao=compilado
- Anexo VII da Res. CGSN 140: http://normas.receita.fazenda.gov.br/sijut2consulta/anexoOutros.action?idArquivoBinario=54769
- Receita Federal sobre a Res. CGSN 190/2026: https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/agosto/cgsn-atualiza-regras-do-simples-nacional-para-adequacao-a-reforma-tributaria-do-consumo
- Econet, mudanças de 2027: https://blog.econeteditora.com.br/simples-nacional-o-que-muda-no-rbt12-e-no-fs12-a-partir-de-2027/
- Manual do PGDAS-D: https://www8.receita.fazenda.gov.br/simplesnacional/arquivos/manual/manual_pgdas-d_2018_v4.pdf
- Tabela de domínio do PGDAS-D no Integra Contador (cópia): https://github.com/MarlonSantosDev/serpro_integra_contador_api/blob/HEAD/bk.cursor/rules/pgdasd/pgdasd.mdc
- SC Cosit 13/2022 (promoção de vendas): https://www.ibet.com.br/solucao-de-consulta-cosit-no-13-de-28-de-marco-de-2022-assunto-simples-nacional-promocao-de-vendas-marketing-direto-anexo-iii-no-simples-nacional-as-receitas-de-promocao-de-vendas-cnae-7319-0/
- Ferramentas de consulta usadas para comparação (não oficiais): https://www.contabeis.com.br/ferramentas/simples-nacional/fator-r e https://www.contabilizei.com.br/contabilidade-online/cnae/
