# Ferramentas

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
