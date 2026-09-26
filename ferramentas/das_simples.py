# -*- coding: utf-8 -*-
"""Recálculo independente do DAS do Simples Nacional, para conferir o valor gerado pela Domínio ou pelo PGDAS-D.

Uso:
    python ferramentas/das_simples.py --rbt12 600000 --anexo I --receita normal=50000 --receita st=10000
    python ferramentas/das_simples.py --rbt12 900000 --receita I:normal=40000 --receita III:iss_retido=8000
    python ferramentas/das_simples.py --rbt12 900000 --anexo III --folha12 270000 --receita normal=60000

Tipos de receita:
    Anexos I e II: normal, st, monofasico, st_monofasico, exportacao
    Anexos III, IV e V: normal, iss_retido, exportacao
Tabelas: LC 123/2006, Anexos I a V, na redação da LC 155/2016, vigentes de 01/2018 a 12/2026. A partir de 01/2027 a
repartição muda com a CBS/IBS: as tabelas novas precisam ser incluídas antes de usar a ferramenta em 2027.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import ROUND_HALF_UP, Decimal

VIGENCIA = ("2018-01", "2026-12")
LIMITES = [Decimal(v) for v in ("180000", "360000", "720000", "1800000", "3600000", "4800000")]
SUBLIMITE = Decimal("3600000")
CENTAVO = Decimal("0.01")

# anexo -> (tributos, [(alíquota nominal %, parcela a deduzir, [repartição % por tributo])] por faixa 1..6)
TABELAS = {
    "I": (["IRPJ", "CSLL", "COFINS", "PIS", "CPP", "ICMS"], [
        ("4.00", "0", ["5.50", "3.50", "12.74", "2.76", "41.50", "34.00"]),
        ("7.30", "5940", ["5.50", "3.50", "12.74", "2.76", "41.50", "34.00"]),
        ("9.50", "13860", ["5.50", "3.50", "12.74", "2.76", "42.00", "33.50"]),
        ("10.70", "22500", ["5.50", "3.50", "12.74", "2.76", "42.00", "33.50"]),
        ("14.30", "87300", ["5.50", "3.50", "12.74", "2.76", "42.00", "33.50"]),
        ("19.00", "378000", ["13.50", "10.00", "28.27", "6.13", "42.10", "0"]),
    ]),
    "II": (["IRPJ", "CSLL", "COFINS", "PIS", "CPP", "IPI", "ICMS"], [
        ("4.50", "0", ["5.50", "3.50", "11.51", "2.49", "37.50", "7.50", "32.00"]),
        ("7.80", "5940", ["5.50", "3.50", "11.51", "2.49", "37.50", "7.50", "32.00"]),
        ("10.00", "13860", ["5.50", "3.50", "11.51", "2.49", "37.50", "7.50", "32.00"]),
        ("11.20", "22500", ["5.50", "3.50", "11.51", "2.49", "37.50", "7.50", "32.00"]),
        ("14.70", "85500", ["5.50", "3.50", "11.51", "2.49", "37.50", "7.50", "32.00"]),
        ("30.00", "720000", ["8.50", "7.50", "20.96", "4.54", "23.50", "35.00", "0"]),
    ]),
    "III": (["IRPJ", "CSLL", "COFINS", "PIS", "CPP", "ISS"], [
        ("6.00", "0", ["4.00", "3.50", "12.82", "2.78", "43.40", "33.50"]),
        ("11.20", "9360", ["4.00", "3.50", "14.05", "3.05", "43.40", "32.00"]),
        ("13.50", "17640", ["4.00", "3.50", "13.64", "2.96", "43.40", "32.50"]),
        ("16.00", "35640", ["4.00", "3.50", "13.64", "2.96", "43.40", "32.50"]),
        ("21.00", "125640", ["4.00", "3.50", "12.82", "2.78", "43.40", "33.50"]),
        ("33.00", "648000", ["35.00", "15.00", "16.03", "3.47", "30.50", "0"]),
    ]),
    "IV": (["IRPJ", "CSLL", "COFINS", "PIS", "ISS"], [
        ("4.50", "0", ["18.80", "15.20", "17.67", "3.83", "44.50"]),
        ("9.00", "8100", ["19.80", "15.20", "20.55", "4.45", "40.00"]),
        ("10.20", "12420", ["20.80", "15.20", "19.73", "4.27", "40.00"]),
        ("14.00", "39780", ["17.80", "19.20", "18.90", "4.10", "40.00"]),
        ("22.00", "183780", ["18.80", "19.20", "18.08", "3.92", "40.00"]),
        ("33.00", "828000", ["53.50", "21.50", "20.55", "4.45", "0"]),
    ]),
    "V": (["IRPJ", "CSLL", "COFINS", "PIS", "CPP", "ISS"], [
        ("15.50", "0", ["25.00", "15.00", "14.10", "3.05", "28.85", "14.00"]),
        ("18.00", "4500", ["23.00", "15.00", "14.10", "3.05", "27.85", "17.00"]),
        ("19.50", "9900", ["24.00", "15.00", "14.92", "3.23", "23.85", "19.00"]),
        ("20.50", "17100", ["21.00", "15.00", "15.74", "3.41", "23.85", "21.00"]),
        ("23.00", "62100", ["23.00", "12.50", "14.10", "3.05", "23.85", "23.50"]),
        ("30.50", "540000", ["35.00", "15.50", "16.44", "3.56", "29.50", "0"]),
    ]),
}

# 5ª faixa dos Anexos III e IV: acima deste limite de alíquota efetiva o ISS fica em 5% e o excedente
# (efetiva - 5%) é repartido pelos tributos federais nestes percentuais.
TETO_ISS = Decimal("5")
REPARTICAO_EXCEDENTE_5A_FAIXA = {
    "III": (Decimal("14.92537"), {"IRPJ": "6.02", "CSLL": "5.26", "COFINS": "19.28", "PIS": "4.18", "CPP": "65.26"}),
    "IV": (Decimal("12.5"), {"IRPJ": "31.33", "CSLL": "32.00", "COFINS": "30.13", "PIS": "6.54"}),
}

# tributos excluídos da alíquota efetiva em cada tipo de receita segregada
EXCLUSOES = {
    "normal": set(),
    "st": {"ICMS"},
    "monofasico": {"PIS", "COFINS"},
    "st_monofasico": {"ICMS", "PIS", "COFINS"},
    "exportacao": {"COFINS", "PIS", "ICMS", "IPI", "ISS"},
    "iss_retido": {"ISS"},
}
TIPOS_POR_ANEXO = {
    "I": {"normal", "st", "monofasico", "st_monofasico", "exportacao"},
    "II": {"normal", "st", "monofasico", "st_monofasico", "exportacao"},
    "III": {"normal", "iss_retido", "exportacao"},
    "IV": {"normal", "iss_retido", "exportacao"},
    "V": {"normal", "iss_retido", "exportacao"},
}


def dinheiro(v: Decimal) -> Decimal:
    return v.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def faixa(rbt12: Decimal) -> int:
    for i, limite in enumerate(LIMITES, start=1):
        if rbt12 <= limite:
            return i
    raise ValueError(f"RBT12 de R$ {rbt12} acima do limite do Simples Nacional (R$ 4,8 mi)")


def rbt12_proporcional(receitas_anteriores: list, receita_mes: Decimal) -> Decimal:
    """RBT12 de empresa com menos de 12 meses de atividade: média dos meses anteriores × 12.
    No primeiro mês, usa a receita do próprio mês × 12."""
    if not receitas_anteriores:
        return Decimal(receita_mes) * 12
    anteriores = [Decimal(v) for v in receitas_anteriores]
    return sum(anteriores, Decimal("0")) / len(anteriores) * 12


def anexo_pelo_fator_r(folha12: Decimal, rbt12: Decimal) -> tuple[str, Decimal]:
    """Atividades sujeitas ao fator r: Anexo III se folha dos 12 meses / RBT12 >= 28%, senão Anexo V."""
    fator = Decimal(folha12) / Decimal(rbt12) if rbt12 else Decimal("0")
    return ("III" if fator >= Decimal("0.28") else "V"), fator


def percentuais(anexo: str, rbt12: Decimal) -> dict:
    """Alíquota efetiva e percentual efetivo de cada tributo (em % da receita), antes da segregação."""
    tributos, faixas = TABELAS[anexo]
    f = faixa(rbt12)
    nominal, deducao, reparticao = faixas[f - 1]
    nominal, deducao = Decimal(nominal), Decimal(deducao)
    efetiva = (rbt12 * nominal / 100 - deducao) / rbt12 * 100 if rbt12 > 0 else nominal
    por_tributo = {t: efetiva * Decimal(p) / 100 for t, p in zip(tributos, reparticao)}
    regra = REPARTICAO_EXCEDENTE_5A_FAIXA.get(anexo)
    teto_aplicado = False
    if regra and f == 5 and efetiva > regra[0]:
        excedente = efetiva - TETO_ISS
        por_tributo = {t: excedente * Decimal(p) / 100 for t, p in regra[1].items()}
        por_tributo["ISS"] = TETO_ISS
        teto_aplicado = True
    return {"anexo": anexo, "faixa": f, "aliquota_nominal": nominal, "parcela_deduzir": deducao,
            "aliquota_efetiva": efetiva, "por_tributo": por_tributo, "teto_iss_aplicado": teto_aplicado}


def calcular(rbt12, receitas: list) -> dict:
    """receitas: lista de (anexo, tipo, valor). Devolve o detalhamento e o total do DAS."""
    rbt12 = Decimal(rbt12)
    linhas, total_direto, total_tributos, alertas = [], Decimal("0"), {}, []
    for anexo, tipo, valor in receitas:
        anexo, valor = anexo.upper(), Decimal(valor)
        if anexo not in TABELAS:
            raise ValueError(f"Anexo inválido: {anexo}")
        if tipo not in TIPOS_POR_ANEXO[anexo]:
            raise ValueError(f"Tipo de receita '{tipo}' não se aplica ao Anexo {anexo}")
        p = percentuais(anexo, rbt12)
        devidos = {t: pct for t, pct in p["por_tributo"].items() if t not in EXCLUSOES[tipo] and pct > 0}
        efetiva_segregada = sum(devidos.values(), Decimal("0"))
        valores = {t: dinheiro(valor * pct / 100) for t, pct in devidos.items()}
        for t, v in valores.items():
            total_tributos[t] = total_tributos.get(t, Decimal("0")) + v
        direto = dinheiro(valor * efetiva_segregada / 100)
        total_direto += direto
        linhas.append({"anexo": anexo, "tipo": tipo, "receita": valor, "faixa": p["faixa"],
                       "aliquota_nominal": p["aliquota_nominal"], "parcela_deduzir": p["parcela_deduzir"],
                       "aliquota_efetiva": p["aliquota_efetiva"], "aliquota_efetiva_segregada": efetiva_segregada,
                       "valor": direto, "por_tributo": valores, "teto_iss_aplicado": p["teto_iss_aplicado"]})
    if rbt12 > SUBLIMITE:
        alertas.append("RBT12 acima do sublimite de R$ 3,6 mi: ICMS e ISS são recolhidos fora do DAS.")
    elif rbt12 > SUBLIMITE * Decimal("0.8"):
        alertas.append("RBT12 acima de 80% do sublimite de R$ 3,6 mi.")
    soma_tributos = sum(total_tributos.values(), Decimal("0"))
    return {"rbt12": rbt12, "vigencia_tabelas": VIGENCIA, "linhas": linhas, "das_total": total_direto,
            "das_soma_por_tributo": soma_tributos, "total_por_tributo": total_tributos, "alertas": alertas}


def _pct(v: Decimal) -> str:
    return f"{v.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)}%".replace(".", ",")


def _brl(v: Decimal) -> str:
    inteiro, dec = f"{dinheiro(v):.2f}".split(".")
    return "R$ " + f"{int(inteiro):,}".replace(",", ".") + "," + dec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Recálculo do DAS do Simples Nacional.")
    ap.add_argument("--rbt12", required=True, help="receita bruta dos 12 meses anteriores (use ponto decimal)")
    ap.add_argument("--anexo", help="anexo padrão das receitas sem prefixo (I, II, III, IV, V)")
    ap.add_argument("--folha12", help="folha dos 12 meses para o fator r (substitui III/V pelo anexo correto)")
    ap.add_argument("--receita", action="append", required=True,
                    help="[ANEXO:]TIPO=VALOR, ex.: normal=50000 ou III:iss_retido=8000")
    ap.add_argument("--json", action="store_true", help="imprime o resultado em JSON")
    args = ap.parse_args(argv)
    rbt12 = Decimal(args.rbt12)
    fator_info = None
    if args.folha12:
        anexo_r, fator = anexo_pelo_fator_r(Decimal(args.folha12), rbt12)
        fator_info = (anexo_r, fator)
    receitas = []
    for r in args.receita:
        chave, valor = r.split("=")
        anexo, tipo = chave.split(":") if ":" in chave else (args.anexo, chave)
        if not anexo:
            ap.error(f"informe o anexo em --anexo ou no prefixo da receita: {r}")
        if fator_info and anexo.upper() in ("III", "V"):
            anexo = fator_info[0]
        receitas.append((anexo, tipo.strip(), Decimal(valor)))
    res = calcular(rbt12, receitas)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        return 0
    print(f"RBT12 {_brl(rbt12)} · tabelas vigentes de {VIGENCIA[0]} a {VIGENCIA[1]}")
    if fator_info:
        print(f"Fator r {_pct(fator_info[1] * 100)} → Anexo {fator_info[0]}")
    for ln in res["linhas"]:
        print(f"Anexo {ln['anexo']} · faixa {ln['faixa']} · {ln['tipo']}: receita {_brl(ln['receita'])} × "
              f"{_pct(ln['aliquota_efetiva_segregada'])} = {_brl(ln['valor'])}"
              + ("  (teto de 5% do ISS aplicado)" if ln["teto_iss_aplicado"] else ""))
        print("   " + " · ".join(f"{t} {_brl(v)}" for t, v in ln["por_tributo"].items()))
    print(f"DAS: {_brl(res['das_total'])} (soma por tributo {_brl(res['das_soma_por_tributo'])})")
    for a in res["alertas"]:
        print("ATENÇÃO · " + a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
