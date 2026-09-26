---
name: fechamento-simples
description: Fecha o mês de uma empresa pequena do Simples Nacional (prestadora de serviço ou comércio) operando a Domínio Web pela tela. Importa as notas (NFS-e, NF-e), confere, calcula antecipação de ICMS e DIFAL quando houver, apura o Simples, faz a revisão técnica com a IA analítica, gera o DAS e as guias, salva os PDFs, envia pelo Acessórias e devolve o relatório de retorno. Use quando pedirem para fechar, apurar, gerar o DAS ou enviar as guias de uma empresa do Simples, por exemplo "feche 09/2026 da empresa 101" ou "rode o fechamento das empresas do piloto".
---

# Fechamento mensal de empresa do Simples Nacional

> **Procedimento em construção.** Os trechos marcados com **[MAPEAR]** dependem das telas e dos hábitos do
> escritório. Eles são preenchidos nas sessões em que fazemos o processo juntos. Enquanto uma etapa tiver
> [MAPEAR], ela roda no nível 1 (acompanhado): mostre o que vai fazer e espere a confirmação da pessoa.

Leia antes o [`CLAUDE.md`](../../../CLAUDE.md) do repositório. As regras de lá valem acima de qualquer coisa escrita aqui.

## Antes de começar

1. Confirme a empresa (código na Domínio e CNPJ) e a competência. Só siga se a empresa estiver em
   `config/empresas_autorizadas.csv`, e anote o nível de autonomia dela (1, 2 ou 3). A empresa é identificada pelo
   **CNPJ**. Se `codigo_dominio` estiver vazio, localize a empresa na Domínio pelo CNPJ e peça à pessoa para gravar o
   código no arquivo. O `id_acessorias` é o ID da empresa no Acessórias.
2. Leia a ficha da empresa em `empresas/<codigo>.md`, se existir: UF, anexo(s), ST, monofásicos, particularidades
   e contato no Acessórias.
3. Crie a pasta de trabalho `trabalho/<AAAA-MM>/<codigo>/` e abra nela o `log.md`. Registre cada etapa com hora,
   o que foi feito e o resultado.
4. Confira as ferramentas:
   - a Domínio Web aberta no programa do plugin, e não só na página de login;
   - o navegador conectado (Claude in Chrome);
   - `python` disponível no terminal;
   - a pasta do e-Contínuo acessível;
   - a variável `ACESSORIAS_TOKEN` definida, se for usar a API.

## Etapas

| # | Etapa | Procedimento | Onde | Parada obrigatória |
|---|---|---|---|---|
| 1 | Documentos do mês | [01-documentos.md](procedimentos/01-documentos.md) | pastas + `ferramentas/nfe.py` | volume muito abaixo do normal |
| 2 | Importação na Domínio | [02-importacao.md](procedimentos/02-importacao.md) | tela da Domínio | nota sem acumulador conhecido |
| 3 | Conferência da importação | [03-conferencia.md](procedimentos/03-conferencia.md) | relatório da Domínio + XML | qualquer nota faltando, sobrando ou divergente |
| 4 | ICMS nas entradas (só contribuintes do ICMS) | [04-icms-entradas.md](procedimentos/04-icms-entradas.md) | `ferramentas/icms_entradas.py` + tela | divergência com a Domínio; UF sem configuração validada |
| 5 | Apuração do Simples | [05-apuracao-simples.md](procedimentos/05-apuracao-simples.md) | tela + `ferramentas/das_simples.py` | recálculo diferente da Domínio |
| 6 | Revisão técnica (IA analítica) | [06-revisao-tecnica.md](procedimentos/06-revisao-tecnica.md) | skill `analise-tecnica` + ferramentas | "erro provável" acima de R$ 50 bloqueia a transmissão |
| 7 | DAS e guias estaduais | [07-guias.md](procedimentos/07-guias.md) | tela da Domínio (Relatórios > Guias), DAS via Integra Contador | **transmitir só com aprovação** (níveis 1 e 2) |
| 8 | Salvar e enviar pelo Acessórias | [08-acessorias.md](procedimentos/08-acessorias.md) | pasta do e-Contínuo ou API do Acessórias | **copiar para a pasta só com aprovação**: equivale a enviar ao cliente |
| 9 | Relatório de retorno | [09-relatorio.md](procedimentos/09-relatorio.md) | `trabalho/.../relatorio.md` | — |

## Como pedir aprovação

Pare num ponto só, com tudo pronto, e mostre um resumo curto:

- empresa e competência;
- valores do DAS e das guias estaduais;
- divergências e alertas (ou "nenhum");
- o que vai fazer ao aprovar.

Exemplo: "Empresa 101, 09/2026. DAS R$ 3.595,00, recálculo igual. Antecipação parcial R$ 412,80. Nenhum alerta.
Posso transmitir o PGDAS-D e enviar as guias pelo Acessórias?"

Em lote, liste uma linha por empresa e peça uma única aprovação para as que não têm alerta.

## Quando parar e chamar uma pessoa

- Divergência acima da tolerância: R$ 0,05 por nota; R$ 1,00 no DAS e nas guias.
- Nota que não sabe classificar, ou fornecedor ou produto novo sem regra.
- Tela, mensagem ou erro que não está descrito no procedimento.
- Captcha, pedido de MFA ou de certificado que não abre.
- DAS com variação acima de 30% em relação à média dos 3 meses anteriores, ou receita zerada em empresa que costuma
  faturar.

Ao parar:

1. Registre no `log.md` o que viu, com print.
2. Diga em uma frase o que precisa.
3. Não tente contornar.

## Ao terminar

- O relatório `trabalho/<AAAA-MM>/<codigo>/relatorio.md` segue o [modelo](procedimentos/modelo-relatorio.md).
- A pasta de trabalho contém os XML usados, os PDFs gerados e os prints das telas-chave.
- Se algo novo foi aprendido (tela diferente, mensagem nova, exceção da empresa), proponha a mudança no
  procedimento ou na ficha da empresa. Não altere sozinho.
