# 03 · Conferência da importação

**Objetivo:** garantir que o que está na Domínio é igual ao que está nos XML, antes de apurar.

## Passo a passo
1. Na Domínio, emita os relatórios de notas de entrada e de saída da competência e salve em Excel ou PDF na pasta de
   trabalho. [MAPEAR] Quais relatórios o escritório usa, como "Relação de notas" ou livros.
2. Compare com o `documentos.json`:
   - quantidade de notas;
   - valor total;
   - notas faltando e notas sobrando;
   - notas canceladas escrituradas como normais.

   A tolerância é de R$ 0,05 por nota.
3. Confira as regras do catálogo aplicáveis ao Simples (ver `docs/02-catalogo-auditorias.md`):
   - CFOP de entrada coerente com o do fornecedor e com a finalidade (AUD-C01);
   - CSOSN coerente (AUD-C02);
   - saídas de produtos com ST ou monofásicos segregadas (AUD-C05), comparando o NCM dos itens com a tabela;
   - empresa sem movimento com XML (AUD-A09).
4. **Prestadoras de serviço:** confira nas NFS-e e na Domínio:
   - ISS retido (sim ou não) nota a nota;
   - município de incidência do ISS;
   - código de serviço;
   - canceladas.

   O resumo do `ferramentas/nfse.py` traz esses campos.
5. Registre no `log.md` o resultado de cada conferência: "ok" ou a lista de divergências.

## Quando parar
Qualquer nota faltando, sobrando ou com valor divergente. Corrigir é decisão da pessoa até a regra estar mapeada.

## Evidência
Relatórios salvos e tabela de conferência no `log.md`.
