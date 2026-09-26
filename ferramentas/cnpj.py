# -*- coding: utf-8 -*-
"""Consulta os dados cadastrais de um CNPJ (CNAEs, Simples, situação) e classifica os CNAEs pelo anexo do Simples.

Uso:
    python ferramentas/cnpj.py <CNPJ> [--saida cnpj.json]

Fonte: BrasilAPI (https://brasilapi.com.br/api/cnpj/v1/<cnpj>), que republica os dados abertos da Receita Federal e
pode ter alguns dias de atraso. Para decisão final, confira o cartão CNPJ no site da Receita.
Endereço alternativo: variável de ambiente CNPJ_API. A classificação usa config/tabelas/cnae_anexo.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from urllib import error, request

RAIZ = Path(__file__).resolve().parent.parent
TABELA_CNAE = RAIZ / "config" / "tabelas" / "cnae_anexo.csv"
PADRAO_API = "https://brasilapi.com.br/api/cnpj/v1"


def so_digitos(texto) -> str:
    return "".join(c for c in str(texto or "") if c.isdigit())


def formatar_cnae(codigo) -> str:
    c = so_digitos(codigo).zfill(7)
    return f"{c[:4]}-{c[4]}/{c[5:]}"


def consultar(cnpj: str) -> dict:
    base = os.environ.get("CNPJ_API", PADRAO_API).rstrip("/")
    req = request.Request(f"{base}/{so_digitos(cnpj)}", headers={"Accept": "application/json",
                                                                  "User-Agent": "agente-fiscal"})
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        raise RuntimeError(f"Consulta do CNPJ falhou (HTTP {e.code}). Use o cartão CNPJ da Receita.") from e
    except error.URLError as e:
        raise RuntimeError(f"Sem acesso à API de CNPJ ({e.reason}). Use o cartão CNPJ da Receita.") from e


def carregar_tabela(arq: Path = TABELA_CNAE) -> dict:
    if not arq.exists():
        return {}
    with open(arq, encoding="utf-8-sig", newline="") as f:
        return {so_digitos(ln["cnae"]).zfill(7): ln for ln in csv.DictReader(f, delimiter=";")}


def cnaes(dados: dict, tabela: dict | None = None) -> list:
    tabela = carregar_tabela() if tabela is None else tabela
    lista = [(dados.get("cnae_fiscal"), dados.get("cnae_fiscal_descricao"), True)]
    lista += [(s.get("codigo"), s.get("descricao"), False) for s in dados.get("cnaes_secundarios") or []]
    saida = []
    for codigo, descricao, principal in lista:
        cod = so_digitos(codigo)
        if not cod or int(cod) == 0:
            continue
        cod = cod.zfill(7)
        info = tabela.get(cod, {})
        saida.append({"codigo": cod, "formatado": formatar_cnae(cod), "descricao": descricao or "",
                      "principal": principal, "anexo": info.get("anexo", "não classificado"),
                      "fator_r": info.get("fator_r", "?"), "observacao": info.get("observacao", "")})
    return saida


def resumo(dados: dict, tabela: dict | None = None) -> dict:
    return {
        "cnpj": so_digitos(dados.get("cnpj")),
        "razao_social": dados.get("razao_social"),
        "situacao": dados.get("descricao_situacao_cadastral"),
        "inicio_atividade": dados.get("data_inicio_atividade"),
        "uf": dados.get("uf"),
        "municipio": dados.get("municipio"),
        "optante_simples": dados.get("opcao_pelo_simples"),
        "data_opcao_simples": dados.get("data_opcao_pelo_simples"),
        "mei": dados.get("opcao_pelo_mei"),
        "cnaes": cnaes(dados, tabela),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Dados cadastrais e CNAEs de um CNPJ.")
    ap.add_argument("cnpj")
    ap.add_argument("--saida", help="grava o resumo em JSON")
    args = ap.parse_args(argv)
    try:
        r = resumo(consultar(args.cnpj))
    except RuntimeError as erro:
        print(f"ATENÇÃO · {erro}")
        return 1
    print(f"{r['razao_social']} · {r['situacao']} · {r['municipio']}/{r['uf']} · início {r['inicio_atividade']}")
    print(f"Simples: {'sim' if r['optante_simples'] else 'não'} (desde {r['data_opcao_simples']}) · MEI: "
          f"{'sim' if r['mei'] else 'não'}")
    for c in r["cnaes"]:
        marca = "principal" if c["principal"] else "secundário"
        print(f"  {c['formatado']} ({marca}) · anexo {c['anexo']} · fator r: {c['fator_r']} · {c['descricao']}")
    if args.saida:
        Path(args.saida).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
