# -*- coding: utf-8 -*-
"""Varredura da carteira: roda as análises técnicas em todas as empresas e ordena os achados por impacto em reais.

Uso:
    python ferramentas/varredura.py <pasta> [--saida trabalho/varreduras/AAAA-MM-DD]

A pasta contém um arquivo de dados por empresa, montado pelo agente no formato de entrada da análise:
    <pasta>/<codigo>/fator_r.json   (formato do analise_fator_r.py; caminhos relativos à própria pasta da empresa)

Saída:
    achados.md    tabela com uma linha por empresa, ordenada pelo impacto em reais (maior primeiro)
    achados.json  resultado completo
    pareceres/<codigo>-AT-01.md   rascunho de parecer de cada empresa
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analise_fator_r  # noqa: E402
from das_simples import _brl  # noqa: E402

ORDEM = {"Erro provável": 0, "Oportunidade": 1, "Indício, falta informação": 2, "Risco latente": 3,
         "Situação justificada": 4}


def varrer(pasta: Path, tabela: dict | None = None) -> list:
    achados = []
    for arq in sorted(Path(pasta).glob("*/fator_r.json")):
        try:
            dados = json.loads(arq.read_text(encoding="utf-8"))
            r = analise_fator_r.analisar(dados, tabela, base=arq.parent)
        except (ValueError, KeyError, OSError) as erro:
            achados.append({"empresa": {"codigo": arq.parent.name}, "analise": "AT-01", "erro": str(erro)})
            continue
        achados.append(r)

    def chave(r):
        imp = (r.get("impacto") or {}).get("diferenca_mes") or Decimal("0")
        plan = (r.get("planejamento_fator_r") or {}).get("economia_das_mes") or Decimal("0")
        return (ORDEM.get(r.get("conclusao_preliminar"), 9), -abs(imp), -plan)

    return sorted(achados, key=chave)


def tabela_md(achados: list) -> str:
    linhas = ["| Empresa | Conclusão (AT-01) | Fator r | Anexo aplicado → devido | Impacto no mês | Planejamento |",
              "|---|---|---|---|---|---|"]
    for r in achados:
        emp = r.get("empresa") or {}
        nome = f"{emp.get('codigo', '?')} · {emp.get('razao_social', '')}".strip(" ·")
        if "erro" in r:
            linhas.append(f"| {nome} | ERRO AO LER DADOS: {r['erro']} | | | | |")
            continue
        imp = r.get("impacto")
        plan = r.get("planejamento_fator_r")
        linhas.append(
            f"| {nome} | {r['conclusao_preliminar']}{' · BLOQUEIA' if r.get('bloqueia_transmissao') else ''} | "
            f"{format(r['fator_r'], '.2%') if r.get('fator_r') is not None else '—'} | "
            f"{r.get('anexo_aplicado') or '?'} → {r.get('anexo_devido') or '—'} | "
            f"{(_brl(abs(imp['diferenca_mes'])) + ' ' + imp['sentido']) if imp else '—'} | "
            f"{('economia de ' + _brl(plan['economia_das_mes']) + '/mês') if plan and plan.get('economia_das_mes') else '—'} |")
    return "\n".join(linhas)


def cnaes_a_classificar(achados: list) -> dict:
    """CNAEs da carteira que não estão na tabela, com as empresas que os têm. Classificar uma vez resolve todas."""
    faltam = {}
    for r in achados:
        for c in r.get("cnaes") or []:
            if c.get("anexo") == "?":
                faltam.setdefault(c["formatado"], []).append((r.get("empresa") or {}).get("codigo", "?"))
    return dict(sorted(faltam.items(), key=lambda kv: (-len(kv[1]), kv[0])))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Varredura de Fator R (AT-01) na carteira.")
    ap.add_argument("pasta")
    ap.add_argument("--saida")
    args = ap.parse_args(argv)
    achados = varrer(Path(args.pasta))
    texto = "# Varredura AT-01 · Fator R e anexo\n\n" + tabela_md(achados) + "\n"
    faltam = cnaes_a_classificar(achados)
    if faltam:
        texto += ("\n## CNAEs a classificar em config/tabelas/cnae_anexo.csv\n\n"
                  + "\n".join(f"- {cnae}: empresas {', '.join(emps)}" for cnae, emps in faltam.items()) + "\n")
    print(texto)
    if args.saida:
        saida = Path(args.saida)
        (saida / "pareceres").mkdir(parents=True, exist_ok=True)
        (saida / "achados.md").write_text(texto, encoding="utf-8")
        (saida / "achados.json").write_text(json.dumps(achados, ensure_ascii=False, indent=1, default=str),
                                            encoding="utf-8")
        for r in achados:
            if "erro" not in r:
                cod = (r.get("empresa") or {}).get("codigo", "sem-codigo")
                (saida / "pareceres" / f"{cod}-AT-01.md").write_text(analise_fator_r.parecer_rascunho(r),
                                                                      encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
