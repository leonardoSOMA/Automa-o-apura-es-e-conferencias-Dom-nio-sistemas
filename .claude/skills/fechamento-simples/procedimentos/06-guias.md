# 06 · DAS e guias estaduais

**Objetivo:** transmitir o PGDAS-D, gerar o DAS e emitir as guias estaduais de antecipação e DIFAL.

> **Aprovação obrigatória antes de transmitir** nos níveis 1 e 2. Transmitir declaração é um ato legal em nome do
> cliente. **Nunca pagar guias.**

## DAS pela Domínio
O agente gera o DAS **pela própria Domínio**, em **Relatórios > Guias > Federais > DAS**: informe a competência e
escolha a *Forma de gerar*.

- **Preferida: API Integra Contador.** A Domínio transmite o PGDAS-D e emite o DAS pelo SERPRO, inclusive em lote e
  nas Rotinas Automáticas (aba Guias, opção "DAS - API Integra Contador").
  - O escritório contrata o Integra Contador e informa a Consumer Key/Secret na Domínio.
  - Cada cliente precisa dar procuração eletrônica com o serviço PGDAS-D.
  - O custo é da ordem de R$ 1 por DAS.
- **Evitar: código de acesso ou certificado pelo portal.** Nesses modos a Domínio abre o site do PGDAS-D, que tem
  captcha e bloqueia uso automatizado das 8h às 18h. Se não houver outro jeito, rode depois das 18h. Se o captcha
  aparecer, chame uma pessoa.

Antes de gerar, confira se as receitas segregadas e o valor batem com a etapa 5. [Confirmar na sessão: caminhos e
opções vêm da central de soluções da Domínio.]

## Guias estaduais
Na Domínio, em **Relatórios > Guias > Estaduais**: DAE, DARE ou GNRE, conforme a UF. [MAPEAR] Guia e código de
receita da sua UF. Se a Domínio não emitir, use o portal da SEFAZ. Os valores vêm da etapa 4.

## Arquivos
Salve em `trabalho/<AAAA-MM>/<codigo>/guias/`:
- `DAS_<codigo>_<AAAA-MM>.pdf` e o recibo do PGDAS-D;
- `ICMS-ANTECIPACAO_<codigo>_<AAAA-MM>.pdf` e `ICMS-DIFAL_<codigo>_<AAAA-MM>.pdf`, quando houver.

## Quando parar
- Valor do portal diferente do recálculo.
- Captcha, MFA ou certificado que não abre.
- Pendência que impede a transmissão.
