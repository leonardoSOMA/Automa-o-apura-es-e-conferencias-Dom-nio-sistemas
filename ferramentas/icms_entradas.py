# -*- coding: utf-8 -*-
"""ICMS nas entradas interestaduais: antecipação parcial, antecipação com ST e DIFAL.

Pensado para empresas do Simples Nacional que compram de outros estados. As regras variam por UF, por isso tudo o que
é legislação fica em `config/uf/<UF>.json` e precisa ser validado por um contador antes do uso real.

Uso:
    python ferramentas/icms_entradas.py <pasta dos XML de entrada> --uf <UF> --cnpj <CNPJ>
        [--finalidades finalidades.csv] [--saida prefixo] [--permitir-nao-validada]

finalidades.csv (opcional), separador ";", colunas: chave;item;cprod;finalidade
    finalidade = revenda | uso_consumo | ativo. Use item ou cprod para apontar o item; deixe vazio para a nota toda.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nfe import Nota, ler_pasta, so_digitos  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SUL_SUDESTE_EXCETO_ES = {"MG", "PR", "RJ", "RS", "SC", "SP"}
ORIGEM_IMPORTADA = {"1", "2", "3", "8"}
FINALIDADES = {"revenda", "uso_consumo", "ativo"}
CENTAVO = Decimal("0.01")


def dinheiro(v: Decimal) -> Decimal:
    return v.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def carregar_config(uf: str, pasta: Path | None = None) -> dict:
    arq = (pasta or RAIZ / "config" / "uf") / f"{uf.upper()}.json"
    if not arq.exists():
        raise FileNotFoundError(f"Sem configuração para a UF {uf}: crie {arq} a partir de config/uf/MODELO.json")
    cfg = json.loads(arq.read_text(encoding="utf-8"))
    cfg["_arquivo"] = str(arq)
    return cfg


def _pct(valor) -> Decimal:
    return Decimal(str(valor))


def _por_ncm(tabela: dict, ncm: str):
    """Procura o NCM pelo prefixo mais longo (ex.: "2203" vale para 22030000)."""
    melhor = None
    for prefixo, valor in (tabela or {}).items():
        if ncm.startswith(prefixo) and (melhor is None or len(prefixo) > len(melhor[0])):
            melhor = (prefixo, valor)
    return melhor[1] if melhor else None


def aliquota_interestadual(item, uf_origem: str, uf_destino: str) -> tuple[Decimal, str]:
    if item.p_icms > 0:
        return item.p_icms / 100, "destacada na nota"
    if item.orig in ORIGEM_IMPORTADA:
        return Decimal("0.04"), "inferida: produto importado (4%)"
    if uf_origem in SUL_SUDESTE_EXCETO_ES and uf_destino not in SUL_SUDESTE_EXCETO_ES:
        return Decimal("0.07"), "inferida pela rota (7%)"
    return Decimal("0.12"), "inferida pela rota (12%)"


def carregar_finalidades(arq: Path | None) -> list:
    if not arq:
        return []
    with open(arq, encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    for ln in linhas:
        if ln.get("finalidade", "").strip() not in FINALIDADES:
            raise ValueError(f"Finalidade inválida em {arq}: {ln}")
    return linhas


def finalidade_do_item(nota: Nota, item, regras: list, padrao: str) -> tuple[str, bool]:
    """Devolve (finalidade, presumida?). Regra mais específica vence: item > cprod > nota inteira."""
    candidatas = []
    for r in regras:
        if so_digitos(r.get("chave", "")) != nota.chave:
            continue
        if r.get("item") and int(r["item"]) == item.numero:
            candidatas.append((3, r["finalidade"]))
        elif r.get("cprod") and r["cprod"].strip() == item.cprod:
            candidatas.append((2, r["finalidade"]))
        elif not r.get("item") and not r.get("cprod"):
            candidatas.append((1, r["finalidade"]))
    if candidatas:
        return max(candidatas)[1].strip(), False
    return padrao, True


def calcular_item(nota: Nota, item, cfg: dict, finalidade: str) -> dict:
    uf = cfg["uf"].upper()
    aliq_inter, origem_aliq = aliquota_interestadual(item, nota.emit_uf, uf)
    aliq_int = _pct(_por_ncm(cfg.get("aliquotas_internas_por_ncm"), item.ncm) or cfg["aliquota_interna_padrao"])
    fcp = _pct(cfg.get("fcp", 0))
    res = {
        "chave": nota.chave, "numero": nota.numero, "emitente": nota.emit_nome, "uf_origem": nota.emit_uf,
        "item": item.numero, "cprod": item.cprod, "descricao": item.xprod, "ncm": item.ncm,
        "cfop_fornecedor": item.cfop, "finalidade": finalidade, "tipo": "", "base": Decimal("0"),
        "aliq_interestadual": aliq_inter, "aliq_interna": aliq_int, "credito": Decimal("0"),
        "valor": Decimal("0"), "fcp": Decimal("0"), "obs": [],
    }
    if origem_aliq != "destacada na nota":
        res["obs"].append(f"alíquota interestadual {origem_aliq}")
    if item.cst in ("40", "41", "50"):
        res["obs"].append(f"CST {item.cst} na origem (isenta, não tributada ou suspensa): conferir se há ICMS a antecipar")

    if item.st_retida_na_nota:
        res["tipo"] = "st_retida_pelo_fornecedor"
        res["obs"].append(f"ICMS-ST de R$ {item.v_icms_st} retido na nota")
        return res
    if item.st_encerrada_antes:
        res["tipo"] = "st_encerrada_anteriormente"
        return res

    fornecedor_simples = nota.emit_crt in ("1", "4") or item.p_icms == 0

    def credito(base_operacao: Decimal, regra: str) -> Decimal:
        if item.v_icms > 0:
            return item.v_icms
        if fornecedor_simples and regra == "zero":
            return Decimal("0")
        return dinheiro(base_operacao * aliq_inter)

    if finalidade in ("uso_consumo", "ativo"):
        d = cfg.get("difal_uso_consumo_ativo", {})
        if not d.get("aplica", False):
            res["tipo"] = "difal_nao_aplicavel"
            return res
        v = item.valor_operacao(incluir_ipi=d.get("inclui_ipi", True))
        cred = credito(v, d.get("credito_fornecedor_simples", "aliquota_interestadual"))
        if d.get("base", "dupla") == "dupla":
            base = (v - cred) / (1 - aliq_int - fcp)
            valor = base * aliq_int - cred
        else:
            base = v
            valor = v * aliq_int - cred
        res.update(tipo="difal", base=dinheiro(base), credito=cred, valor=dinheiro(max(valor, Decimal("0"))),
                   fcp=dinheiro(base * fcp))
        return res

    mva = _por_ncm(cfg.get("antecipacao_st", {}).get("mva_por_ncm"), item.ncm)
    st = cfg.get("antecipacao_st", {})
    if mva is not None and st.get("aplica", False):
        mva = _pct(mva)
        if st.get("usar_mva_ajustada", True) and aliq_inter < aliq_int:
            mva = (1 + mva) * (1 - aliq_inter) / (1 - aliq_int) - 1
        v = item.valor_operacao(incluir_ipi=True)
        base = v * (1 + mva)
        cred = credito(item.valor_operacao(), st.get("credito_fornecedor_simples", "aliquota_interestadual"))
        valor = base * aliq_int - cred
        res.update(tipo="antecipacao_st", base=dinheiro(base), credito=cred, valor=dinheiro(max(valor, Decimal("0"))),
                   fcp=dinheiro(base * fcp))
        res["obs"].append(f"MVA aplicada {dinheiro(mva * 100)}%")
        return res

    ap = cfg.get("antecipacao_parcial", {})
    if not ap.get("aplica", False):
        res["tipo"] = "sem_antecipacao"
        return res
    v = item.valor_operacao(incluir_ipi=ap.get("inclui_ipi", False))
    cred = credito(item.valor_operacao(), ap.get("credito_fornecedor_simples", "aliquota_interestadual"))
    if ap.get("base", "unica") == "dupla":
        base = (v - cred) / (1 - aliq_int)
        valor = base * aliq_int - cred
    else:
        base = v
        valor = v * aliq_int - cred
    reducao = _pct(ap.get("reducao_simples", 0))
    if reducao:
        valor = valor * (1 - reducao)
        res["obs"].append(f"redução de {dinheiro(reducao * 100)}% para o Simples")
    res.update(tipo="antecipacao_parcial", base=dinheiro(base), credito=cred, valor=dinheiro(max(valor, Decimal("0"))))
    return res


def calcular(pasta: Path, uf: str, cnpj: str, cfg: dict, finalidades: list | None = None) -> dict:
    uf, cnpj = uf.upper(), so_digitos(cnpj)
    notas, canceladas, ignorados = ler_pasta(pasta)
    padrao = cfg.get("finalidade_padrao", "revenda")
    linhas, avisos, vistas = [], [], set()
    for n in notas:
        if n.chave in vistas or n.chave in canceladas or n.dest_doc != cnpj:
            continue
        vistas.add(n.chave)
        if n.emit_uf == uf:
            continue  # operação interna: fora do escopo desta calculadora
        for item in n.itens:
            fin, presumida = finalidade_do_item(n, item, finalidades or [], padrao)
            linha = calcular_item(n, item, cfg, fin)
            if presumida:
                linha["obs"].append(f"finalidade presumida ({fin}): confirmar pelo CFOP de entrada escriturado")
            linhas.append(linha)
    if not cfg.get("validado_em"):
        avisos.append(f"Configuração {cfg.get('_arquivo')} NÃO validada: valores só para teste.")
    if any("presumida" in o for ln in linhas for o in ln["obs"]):
        avisos.append("Há itens com finalidade presumida.")
    totais = {}
    for ln in linhas:
        t = totais.setdefault(ln["tipo"], {"itens": 0, "valor": Decimal("0"), "fcp": Decimal("0")})
        t["itens"] += 1
        t["valor"] += ln["valor"]
        t["fcp"] += ln["fcp"]
    return {"uf": uf, "cnpj": cnpj, "config": cfg.get("_arquivo"), "config_validada": bool(cfg.get("validado_em")),
            "totais": totais, "itens": linhas, "avisos": avisos, "arquivos_ignorados": ignorados}


def _json_default(o):
    return str(o) if isinstance(o, Decimal) else o


def gravar(res: dict, prefixo: Path) -> None:
    prefixo.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{prefixo}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=_json_default),
                                       encoding="utf-8")
    campos = ["chave", "numero", "emitente", "uf_origem", "item", "cprod", "descricao", "ncm", "cfop_fornecedor",
              "finalidade", "tipo", "base", "aliq_interestadual", "aliq_interna", "credito", "valor", "fcp", "obs"]
    with open(f"{prefixo}.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(campos)
        for ln in res["itens"]:
            w.writerow([" | ".join(ln[c]) if c == "obs" else str(ln[c]).replace(".", ",")
                        if isinstance(ln[c], Decimal) else ln[c] for c in campos])


NOMES = {"antecipacao_parcial": "Antecipação parcial", "antecipacao_st": "Antecipação com ST", "difal": "DIFAL",
         "st_retida_pelo_fornecedor": "ST já retida pelo fornecedor", "st_encerrada_anteriormente": "ST encerrada antes",
         "sem_antecipacao": "Sem antecipação na UF", "difal_nao_aplicavel": "DIFAL não aplicável"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Antecipação de ICMS e DIFAL nas entradas interestaduais.")
    ap.add_argument("pasta")
    ap.add_argument("--uf", required=True)
    ap.add_argument("--cnpj", required=True)
    ap.add_argument("--finalidades")
    ap.add_argument("--saida", help="prefixo dos arquivos .json e .csv de saída")
    ap.add_argument("--config-dir", help="pasta das configurações por UF (padrão: config/uf)")
    ap.add_argument("--permitir-nao-validada", action="store_true")
    args = ap.parse_args(argv)
    cfg = carregar_config(args.uf, Path(args.config_dir) if args.config_dir else None)
    if not cfg.get("validado_em") and not args.permitir_nao_validada:
        print(f"PARE: a configuração {cfg['_arquivo']} não foi validada por um contador. "
              "Valide a legislação da UF ou rode com --permitir-nao-validada só para teste.")
        return 2
    res = calcular(Path(args.pasta), args.uf, args.cnpj, cfg,
                   carregar_finalidades(Path(args.finalidades)) if args.finalidades else None)
    for tipo, t in res["totais"].items():
        extra = f" + FCP R$ {dinheiro(t['fcp'])}" if t["fcp"] else ""
        print(f"{NOMES.get(tipo, tipo)}: {t['itens']} itens, R$ {dinheiro(t['valor'])}{extra}")
    for aviso in res["avisos"]:
        print("ATENÇÃO · " + aviso)
    if args.saida:
        gravar(res, Path(args.saida))
    return 0


if __name__ == "__main__":
    sys.exit(main())
