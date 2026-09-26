# Ferramentas

## Ferramentas do agente

Só usam a biblioteca padrão do Python.

| Ferramenta | Para quê | Exemplo |
|---|---|---|
| `nfe.py` | Ler XML de NF-e/NFC-e e resumir o mês: entradas, saídas, canceladas, duplicadas | `python ferramentas/nfe.py resumo <pasta> --cnpj <CNPJ> --competencia 2026-09` |
| `nfse.py` | Ler NFS-e (Nacional e ABRASF) e resumir por código de serviço, ISS retido, município e retenções | `python ferramentas/nfse.py resumo <pasta> --cnpj <CNPJ> --competencia 2026-09 --saida nfse.json` |
| `cnpj.py` | CNAEs, Simples e situação do CNPJ (BrasilAPI), classificados pela tabela `config/tabelas/cnae_anexo.csv` | `python ferramentas/cnpj.py <CNPJ> --saida cnpj.json` |
| `analise_fator_r.py` | AT-01: Fator R e anexo. Hipóteses, conclusão preliminar, impacto III × V e planejamento. | `python ferramentas/analise_fator_r.py dados.json --saida pareceres/AT-01` |
| `analise_iss.py` | AT-02 (ISS retido segregado), AT-03 (município de incidência) e AT-05 (retenções em notas de optante) | `python ferramentas/analise_iss.py dados.json --saida pareceres/ISS` |
| `varredura.py` | Roda a AT-01 em todas as empresas de uma pasta e ordena os achados por impacto | `python ferramentas/varredura.py trabalho/2026-09 --saida trabalho/varreduras/2026-10-05` |
| `das_simples.py` | Recalcular o DAS (Anexos I a V, segregação de ST, monofásico, ISS retido, fator r) | `python ferramentas/das_simples.py --rbt12 600000 --anexo I --receita normal=40000 --receita st=10000` |
| `icms_entradas.py` | Antecipação parcial, antecipação com ST e DIFAL nas compras de outros estados, pelas regras de `config/uf/<UF>.json` | `python ferramentas/icms_entradas.py <pasta> --uf BA --cnpj <CNPJ> --saida trabalho/.../icms` |
| `acessorias.py` | Enviar guias ao robô e-Contínuo e consultar entregas pela API do Acessórias | `python ferramentas/acessorias.py enviar DAS.pdf` (simula; `--confirmo-envio` envia) |

As regras de ICMS por UF precisam ser preenchidas e **validadas por um contador** antes do uso. Enquanto isso, a
calculadora se recusa a rodar sem `--permitir-nao-validada`. As tabelas do DAS valem até 12/2026. Em 2027 a repartição
muda com a CBS/IBS e as tabelas precisam ser atualizadas.

## Geradores do plano (versão 1)

Geradores dos artefatos da Fase 0. O catálogo de auditorias tem uma fonte única, `catalogo.py`. Altere as regras lá e
gere de novo o CSV e a planilha, para que tudo continue batendo.

```bash
pip install openpyxl
python ferramentas/catalogo.py catalogo/auditorias.csv /tmp/catalogo.json /tmp/catalogo_tabela.md
python ferramentas/kit_fase0.py /tmp/catalogo.json fase0/Kit_Fase0_Diagnostico.xlsx
```

- `catalogo.py` gera o CSV (separador `;`, abre direto no Excel), o JSON e a tabela Markdown usada em
  `docs/02-catalogo-auditorias.md`.
- `kit_fase0.py` gera a planilha. As fórmulas são calculadas quando o arquivo é aberto no Excel ou no LibreOffice.
