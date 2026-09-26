# -*- coding: utf-8 -*-
"""AT-02 (ISS retido), AT-03 (município de incidência) e AT-05 (retenções federais em notas de optante).

Uso:
    python ferramentas/analise_iss.py <dados.json> [--saida trabalho/.../pareceres/ISS]

dados.json:
{
  "empresa": {"codigo": "205", "razao_social": "..."},
  "competencia": "2026-09",
  "nfse_json": "nfse.json",                    # saída do nfse.py (notas prestadas da competência)
  "municipio_estabelecimento": "9999999",      # código IBGE do município da empresa
  "apuracao": {
    "rbt12": "360000", "anexo": "III",
    "receitas_declaradas": [{"tipo": "normal", "valor": "..."}, {"tipo": "iss_retido", "valor": "..."}],
    "receita_iss_outro_municipio": "0"         # receita declarada com ISS devido a outro município
  }
}
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import das_simples  # noqa: E402

TOLERANCIA = Decimal("1.00")


def _d(v) -> Decimal:
    return Decimal(str(v)) if v not in (None, "") else Decimal("0")


def _achado(codigo, titulo, conclusao, impacto, sentido, fatos, hipoteses, acao):
    return {"analise": codigo, "titulo": titulo, "conclusao": conclusao, "impacto_mes": impacto, "sentido": sentido,
            "fatos": fatos, "hipoteses": hipoteses, "acao": acao}


def at02_iss_retido(prestadas: dict, apuracao: dict) -> dict:
    retido_notas = _d(prestadas.get("valor_com_iss_retido"))
    declarado = sum((_d(r["valor"]) for r in apuracao.get("receitas_declaradas", []) if r.get("tipo") == "iss_retido"),
                    Decimal("0"))
    dif = retido_notas - declarado
    fatos = [f"Receita com ISS retido nas notas: R$ {retido_notas}", f"Receita segregada como ISS retido na apuração: R$ {declarado}"]
    if abs(dif) <= TOLERANCIA:
        return _achado("AT-02", "ISS retido segregado", "Situação justificada", Decimal("0"), None, fatos, [],
                       "Nenhuma: a segregação bate com as notas.")
    rbt12, anexo = _d(apuracao.get("rbt12")), apuracao.get("anexo", "III")
    base = abs(dif)
    com_iss = das_simples.calcular(rbt12, [(anexo, "normal", base)])["das_total"]
    sem_iss = das_simples.calcular(rbt12, [(anexo, "iss_retido", base)])["das_total"]
    impacto = com_iss - sem_iss
    if dif > 0:
        return _achado(
            "AT-02", "ISS retido não segregado", "Oportunidade", impacto, "pago a maior", fatos,
            ["H1 · a apuração não marcou a receita como ISS retido (acumulador ou PGDAS-D sem a segregação)",
             "H2 · a nota diz ISS retido, mas o tomador não reteve: confirmar com o cliente antes de corrigir",
             "H3 · notas de outra competência entraram no resumo"],
            "Se H1 se confirmar: ajustar o acumulador e retificar o PGDAS-D, porque o ISS dessas notas foi pago duas "
            "vezes (retido pelo tomador e no DAS). Decide: sócio.")
    return _achado(
        "AT-02", "Receita segregada como ISS retido sem retenção nas notas", "Erro provável", impacto, "pago a menor",
        fatos,
        ["H1 · segregação indevida na apuração",
         "H2 · as notas não marcaram a retenção, mas o tomador reteve: pedir comprovante ao cliente",
         "H3 · notas faltando no resumo"],
        "Conferir com o cliente. Sem retenção comprovada, o ISS dessas receitas precisa voltar ao DAS. Decide: sócio.")


def at03_municipio(prestadas: dict, municipio: str, apuracao: dict) -> dict:
    fora = Decimal("0")
    municipios = set()
    for n in prestadas.get("notas", []):
        m = n.get("municipio_incidencia")
        if m and municipio and m != municipio:
            fora += _d(n.get("valor_servico"))
            municipios.add(m)
    declarado = _d(apuracao.get("receita_iss_outro_municipio"))
    fatos = [f"Receita com ISS devido a outro município pelas notas: R$ {fora}"
             + (f" (municípios {', '.join(sorted(municipios))})" if municipios else ""),
             f"Receita declarada com ISS em outro município: R$ {declarado}"]
    if abs(fora - declarado) <= TOLERANCIA:
        return _achado("AT-03", "Município de incidência do ISS", "Situação justificada", Decimal("0"), None, fatos, [],
                       "Nenhuma.")
    return _achado(
        "AT-03", "Município de incidência do ISS divergente", "Indício, falta informação", None, "destino do ISS",
        fatos,
        ["H1 · serviço das exceções da LC 116, art. 3º, com ISS devido no local da prestação, sem indicação no PGDAS-D",
         "H2 · município de incidência preenchido errado na nota",
         "H3 · o ISS foi retido pelo tomador no outro município (ver AT-02)"],
        "Conferir o tipo de serviço e o local da prestação. Se H1 se confirmar, informar o município correto no PGDAS-D "
        "para o ISS não ser cobrado duas vezes. Decide: coordenador.")


def at05_retencoes(prestadas: dict, anexo: str) -> dict:
    tot = {k: Decimal("0") for k in ("ret_irrf", "ret_csll", "ret_pis", "ret_cofins", "ret_inss")}
    notas_com_retencao = []
    for n in prestadas.get("notas", []):
        valores = {k: _d(n.get(k)) for k in tot}
        if any(valores.values()):
            notas_com_retencao.append(n.get("numero"))
        for k, v in valores.items():
            tot[k] += v
    federais = tot["ret_irrf"] + tot["ret_csll"] + tot["ret_pis"] + tot["ret_cofins"]
    inss_fora_anexo_iv = tot["ret_inss"] if anexo.upper() != "IV" else Decimal("0")
    indevido = federais + inss_fora_anexo_iv
    fatos = [f"Retenções nas notas prestadas: IRRF R$ {tot['ret_irrf']} · CSLL R$ {tot['ret_csll']} · PIS R$ "
             f"{tot['ret_pis']} · COFINS R$ {tot['ret_cofins']} · INSS R$ {tot['ret_inss']}",
             f"Anexo da empresa: {anexo}"]
    if indevido <= 0:
        return _achado("AT-05", "Retenções em notas de optante", "Situação justificada", Decimal("0"), None, fatos, [],
                       "Nenhuma.")
    return _achado(
        "AT-05", "Retenções federais em notas de optante do Simples", "Oportunidade", indevido, "retido indevidamente",
        fatos + [f"Notas com retenção: {', '.join(str(x) for x in notas_com_retencao[:20])}"],
        ["H1 · o tomador reteve sem necessidade, porque a nota não informou a condição de optante do Simples",
         "H2 · INSS retido em serviço que não é cessão de mão de obra do Anexo IV",
         "H3 · o campo de retenção da nota está preenchido, mas não houve desconto no pagamento: confirmar com o cliente"],
        "Confirmar com o cliente se o valor foi descontado. Se foi, avaliar a restituição e orientar a informar a "
        "condição de optante nas próximas notas. Decide: sócio.")


def _ler_json(caminho, base: Path):
    p = Path(caminho)
    return json.loads((p if p.is_absolute() else base / p).read_text(encoding="utf-8"))


def analisar(dados: dict, base: Path = Path(".")) -> list:
    nfse = _ler_json(dados["nfse_json"], base) if dados.get("nfse_json") else {}
    prestadas = nfse.get("prestadas", {})
    apuracao = dados.get("apuracao", {})
    return [at02_iss_retido(prestadas, apuracao),
            at03_municipio(prestadas, dados.get("municipio_estabelecimento", ""), apuracao),
            at05_retencoes(prestadas, apuracao.get("anexo", "III"))]


def parecer(achado: dict, dados: dict) -> str:
    emp = dados.get("empresa") or {}
    imp = achado["impacto_mes"]
    linhas = [f"# {achado['analise']} · {achado['titulo']} · {emp.get('razao_social', '')} ({emp.get('codigo', '')}) · "
              f"{dados.get('competencia')}",
              f"Conclusão preliminar: **{achado['conclusao']}** (o agente confirma com as notas e o cliente)",
              "Impacto: " + (f"{das_simples._brl(imp)} no mês, {achado['sentido']}" if imp else "sem valor calculado"),
              "", "## Fatos"] + [f"- {f}" for f in achado["fatos"]]
    if achado["hipoteses"]:
        linhas += ["", "## Hipóteses a testar"] + [f"- {h}" for h in achado["hipoteses"]]
    linhas += ["", "## Ação sugerida", f"- {achado['acao']}"]
    return "\n".join(linhas) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AT-02, AT-03 e AT-05: ISS retido, município e retenções.")
    ap.add_argument("dados")
    ap.add_argument("--saida", help="prefixo dos arquivos de saída")
    args = ap.parse_args(argv)
    caminho = Path(args.dados)
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    achados = analisar(dados, caminho.parent)
    for a in achados:
        texto = parecer(a, dados)
        print(texto)
        if args.saida:
            Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
            Path(f"{args.saida}-{a['analise']}.md").write_text(texto, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
