# -*- coding: utf-8 -*-
"""AT-01 · Fator R e anexo (III × V): levanta os fatos, avalia as hipóteses e calcula o impacto em reais.

Uso:
    python ferramentas/analise_fator_r.py <dados.json> [--saida trabalho/.../pareceres/AT-01]

dados.json (montado pelo agente com as outras ferramentas e com as telas da Domínio):
{
  "empresa": {"codigo": "205", "cnpj": "...", "razao_social": "...", "inicio_atividade": "2019-03-01"},
  "competencia": "2026-09",
  "cnpj_json": "trabalho/2026-09/205/cnpj.json",      # saída do cnpj.py (ou "cnaes": [{"codigo": "6201501"}])
  "nfse_json": "trabalho/2026-09/205/nfse.json",      # saída do nfse.py (ou "receitas": [{"tipo", "valor"}])
  "acumuladores": [{"codigo": "50", "descricao": "Serviços", "anexo": "III", "fator_r": "N"}],
  "rbt12": "360000.00", "folha12": "43200.00", "anexo_aplicado": "III"
}

A ferramenta não decide sozinha quando a nota não traz o CNAE. Nesse caso, a conclusão fica em "Indício" e o agente
lê as discriminações das notas para testar a hipótese H2 (atividade não sujeita).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import das_simples  # noqa: E402
from cnpj import TABELA_CNAE, carregar_tabela, formatar_cnae, so_digitos  # noqa: E402

LIMITE_FATOR_R = Decimal("0.28")
FAIXA_PLANEJAMENTO = Decimal("0.20")
LIMITE_BLOQUEIO = Decimal("50")


def _d(v) -> Decimal:
    return Decimal(str(v)) if v not in (None, "") else Decimal("0")


def _ler_json(caminho, base: Path):
    if not caminho:
        return None
    p = Path(caminho)
    p = p if p.is_absolute() else base / p
    return json.loads(p.read_text(encoding="utf-8"))


def classificar(cnaes: list, tabela: dict) -> list:
    saida = []
    for c in cnaes:
        cod = so_digitos(c.get("codigo")).zfill(7)
        info = tabela.get(cod, {})
        saida.append({"codigo": cod, "formatado": formatar_cnae(cod), "descricao": c.get("descricao", ""),
                      "principal": bool(c.get("principal")), "anexo": info.get("anexo", "?"),
                      "fator_r": info.get("fator_r", "?")})
    return saida


def meses_entre(inicio: str, competencia: str) -> int:
    a = date.fromisoformat(inicio[:10])
    ano, mes = (int(x) for x in competencia.split("-"))
    return (ano - a.year) * 12 + (mes - a.month)


def analisar(dados: dict, tabela: dict | None = None, base: Path = Path(".")) -> dict:
    tabela = carregar_tabela() if tabela is None else tabela
    cnpj_info = _ler_json(dados.get("cnpj_json"), base) or {}
    nfse_info = _ler_json(dados.get("nfse_json"), base) or {}
    cnaes = classificar(dados.get("cnaes") or cnpj_info.get("cnaes") or [], tabela)
    codigos_empresa = {c["codigo"] for c in cnaes}
    sujeitos = [c for c in cnaes if c["fator_r"] == "S"]
    nao_sujeitos_iii = [c for c in cnaes if c["anexo"] == "III" and c["fator_r"] == "N"]
    sem_classificacao = [c for c in cnaes if c["anexo"] == "?"]

    rbt12, folha12 = _d(dados.get("rbt12")), _d(dados.get("folha12"))
    folha_informada = dados.get("folha12") not in (None, "")
    fator_r = (folha12 / rbt12) if rbt12 > 0 and folha_informada else None
    anexo_aplicado = (dados.get("anexo_aplicado") or "").upper()

    # receitas do mês: da entrada ou do resumo de NFS-e (prestadas)
    receitas = dados.get("receitas")
    prestadas = nfse_info.get("prestadas", {})
    if not receitas and prestadas:
        total, retido = _d(prestadas.get("valor_total")), _d(prestadas.get("valor_com_iss_retido"))
        receitas = [r for r in ({"tipo": "normal", "valor": total - retido}, {"tipo": "iss_retido", "valor": retido})
                    if _d(r["valor"]) > 0]
    receitas = receitas or []

    # CNAEs informados nas notas (ABRASF traz; a NFS-e nacional em geral não)
    cnaes_notas = set()
    for g in (prestadas.get("por_servico") or {}).values():
        cnaes_notas |= {so_digitos(c).zfill(7) for c in g.get("cnaes_informados", [])}
    notas_sujeitas = {c for c in cnaes_notas if tabela.get(c, {}).get("fator_r") == "S"}
    notas_nao_sujeitas = {c for c in cnaes_notas if tabela.get(c, {}).get("fator_r") == "N"}
    notas_fora_do_cnpj = cnaes_notas - codigos_empresa
    exemplos = [e for g in (prestadas.get("por_servico") or {}).values() for e in g.get("exemplos", [])][:6]

    acumuladores = dados.get("acumuladores") or []
    acum_iii_fixo = [a for a in acumuladores if a.get("anexo", "").upper() == "III" and a.get("fator_r", "N") != "S"]

    h = {}

    def hip(cod, titulo, resultado, evidencia):
        h[cod] = {"hipotese": titulo, "resultado": resultado, "evidencia": evidencia}

    # H1 · acumulador errado
    t1 = "Acumulador errado (atividade sujeita configurada como Anexo III fixo)"
    if not sujeitos:
        hip("H1", t1, "enfraquece", "A empresa não tem CNAE sujeito ao fator r na tabela.")
    elif fator_r is None:
        hip("H1", t1, "inconclusivo", "Fator r não calculado: falta folha ou RBT12.")
    elif fator_r >= LIMITE_FATOR_R:
        hip("H1", t1, "enfraquece", f"Fator r {fator_r:.2%}: para atividade sujeita, o Anexo III é o correto.")
    elif anexo_aplicado == "V":
        hip("H1", t1, "enfraquece", "A apuração já usa o Anexo V.")
    elif notas_sujeitas:
        hip("H1", t1, "reforça",
            f"Notas com CNAE sujeito ({', '.join(formatar_cnae(c) for c in sorted(notas_sujeitas))}), fator r "
            f"{fator_r:.2%} e apuração no Anexo {anexo_aplicado or '?'}."
            + (f" Acumulador(es) no Anexo III fixo: {', '.join(a.get('codigo', '?') for a in acum_iii_fixo)}."
               if acum_iii_fixo else ""))
    elif notas_nao_sujeitas:
        hip("H1", t1, "enfraquece", "As notas com CNAE informado são de atividade não sujeita.")
    elif not nao_sujeitos_iii:
        hip("H1", t1, "reforça",
            f"Todos os CNAEs da empresa são sujeitos ao fator r e o fator r é {fator_r:.2%}. Salvo atividade fora do "
            f"cadastro (H3), o faturamento é de atividade sujeita, e a apuração usou o Anexo {anexo_aplicado or '?'}.")
    else:
        hip("H1", t1, "inconclusivo",
            "A empresa tem atividades sujeitas e não sujeitas e as notas não trazem CNAE: ler as discriminações.")

    # H2 · outra atividade, não sujeita
    if not nao_sujeitos_iii:
        hip("H2", "Outra atividade, não sujeita ao fator r", "enfraquece",
            "A empresa não tem CNAE do Anexo III fora do fator r.")
    elif notas_nao_sujeitas and not notas_sujeitas:
        hip("H2", "Outra atividade, não sujeita ao fator r", "reforça",
            f"Notas emitidas com CNAE não sujeito: {', '.join(formatar_cnae(c) for c in sorted(notas_nao_sujeitas))}.")
    elif notas_sujeitas:
        hip("H2", "Outra atividade, não sujeita ao fator r", "enfraquece",
            "Há notas com CNAE sujeito ao fator r.")
    else:
        hip("H2", "Outra atividade, não sujeita ao fator r", "inconclusivo",
            "A empresa tem CNAE não sujeito ("
            + ", ".join(c["formatado"] for c in nao_sujeitos_iii)
            + "), mas as notas não informam o CNAE: comparar as discriminações com a atividade.")

    # H3 · CNAE desatualizado
    hip("H3", "CNAE desatualizado no CNPJ", "reforça" if notas_fora_do_cnpj else "enfraquece",
        (f"Notas com CNAE fora do cadastro: {', '.join(formatar_cnae(c) for c in sorted(notas_fora_do_cnpj))}."
         if notas_fora_do_cnpj else "Os CNAEs informados nas notas estão no cadastro (ou não foram informados)."))

    # H4 · fator r ≥ 28%
    if fator_r is None:
        hip("H4", "Fator r ≥ 28% (Anexo III correto)", "inconclusivo", "RBT12 zero ou não informado.")
    else:
        hip("H4", "Fator r ≥ 28% (Anexo III correto)", "reforça" if fator_r >= LIMITE_FATOR_R else "enfraquece",
            f"Folha 12 meses R$ {folha12} ÷ RBT12 R$ {rbt12} = {fator_r:.2%}.")

    # H5 · folha errada ou ausente
    if not folha_informada:
        hip("H5", "Folha errada ou ausente na Domínio", "reforça", "A folha dos 12 meses não foi informada.")
    elif folha12 == 0:
        hip("H5", "Folha errada ou ausente na Domínio", "reforça",
            "Folha dos 12 meses igual a zero: confirmar com o DP (pró-labore, FGTS e INSS entram na folha).")
    else:
        hip("H5", "Folha errada ou ausente na Domínio", "a conferir",
            "Comparar a folha usada pela Domínio com a Domínio Folha ou o eSocial.")

    # H6 · início de atividade
    inicio = (dados.get("empresa") or {}).get("inicio_atividade") or cnpj_info.get("inicio_atividade")
    if inicio and dados.get("competencia"):
        m = meses_entre(inicio, dados["competencia"])
        hip("H6", "Início de atividade (menos de 13 meses)", "reforça" if m < 13 else "enfraquece",
            f"Início em {inicio[:10]}: {m} meses até a competência.")
    else:
        hip("H6", "Início de atividade (menos de 13 meses)", "inconclusivo", "Data de início não informada.")

    # anexo devido e impacto
    anexo_devido = None
    if sujeitos and fator_r is not None and (notas_sujeitas or not notas_nao_sujeitas):
        anexo_devido = "III" if fator_r >= LIMITE_FATOR_R else "V"
    impacto = None
    if anexo_devido and anexo_aplicado in ("III", "V") and receitas and rbt12 > 0 and anexo_devido != anexo_aplicado:
        calc = {a: das_simples.calcular(rbt12, [(a, r["tipo"], _d(r["valor"])) for r in receitas])["das_total"]
                for a in (anexo_aplicado, anexo_devido)}
        dif = calc[anexo_devido] - calc[anexo_aplicado]
        impacto = {"das_aplicado": calc[anexo_aplicado], "das_devido": calc[anexo_devido], "diferenca_mes": dif,
                   "sentido": "pago a menor" if dif > 0 else "pago a maior"}

    # conclusão preliminar
    if fator_r is None or folha12 == 0:
        conclusao = "Indício, falta informação"
    elif not sujeitos and not sem_classificacao:
        conclusao = "Situação justificada"
    elif h["H2"]["resultado"] == "reforça" and h["H1"]["resultado"] == "enfraquece":
        conclusao = "Situação justificada"
    elif impacto and impacto["sentido"] == "pago a menor" and h["H1"]["resultado"] == "reforça":
        conclusao = "Erro provável"
    elif impacto and impacto["sentido"] == "pago a maior":
        conclusao = "Oportunidade"
    elif h["H1"]["resultado"] == "inconclusivo" or h["H2"]["resultado"] == "inconclusivo" or sem_classificacao:
        conclusao = "Indício, falta informação"
    else:
        conclusao = "Situação justificada"

    planejamento = None
    if sujeitos and fator_r is not None and FAIXA_PLANEJAMENTO <= fator_r < LIMITE_FATOR_R and rbt12 > 0:
        adicional = LIMITE_FATOR_R * rbt12 - folha12
        economia = None
        if receitas:
            v = das_simples.calcular(rbt12, [("V", r["tipo"], _d(r["valor"])) for r in receitas])["das_total"]
            iii = das_simples.calcular(rbt12, [("III", r["tipo"], _d(r["valor"])) for r in receitas])["das_total"]
            economia = v - iii
        planejamento = {"fator_r": fator_r, "folha_adicional_12_meses": adicional.quantize(Decimal("0.01")),
                        "folha_adicional_media_mes": (adicional / 12).quantize(Decimal("0.01")),
                        "economia_das_mes": economia,
                        "observacao": "Descontar o custo do aumento de folha ou pró-labore (INSS e IRPF da pessoa "
                                      "física) antes de recomendar. Ver AT-07."}

    alertas = []
    if sem_classificacao:
        alertas.append("CNAE sem classificação na tabela: " + ", ".join(c["formatado"] for c in sem_classificacao))
    if not TABELA_CNAE.exists() and not tabela:
        alertas.append(f"Tabela {TABELA_CNAE} não encontrada.")
    bloqueia = conclusao == "Erro provável" and impacto is not None and abs(impacto["diferenca_mes"]) > LIMITE_BLOQUEIO
    return {"analise": "AT-01", "empresa": dados.get("empresa"), "competencia": dados.get("competencia"),
            "cnaes": cnaes, "fator_r": fator_r, "anexo_aplicado": anexo_aplicado, "anexo_devido": anexo_devido,
            "receitas": receitas, "acumuladores": acumuladores, "cnaes_nas_notas": sorted(cnaes_notas),
            "exemplos_de_discriminacao": exemplos, "hipoteses": h, "conclusao_preliminar": conclusao,
            "impacto": impacto, "bloqueia_transmissao": bloqueia, "planejamento_fator_r": planejamento,
            "alertas": alertas}


def _brl(v) -> str:
    return das_simples._brl(Decimal(v))


def parecer_rascunho(r: dict) -> str:
    emp = r.get("empresa") or {}
    imp = r.get("impacto")
    linhas = [f"# AT-01 · Fator R e anexo · {emp.get('razao_social', '')} ({emp.get('codigo', '')}) · {r.get('competencia')}",
              f"Conclusão preliminar: **{r['conclusao_preliminar']}** (o agente confirma ou corrige lendo as notas)",
              "Impacto: " + (f"{_brl(abs(imp['diferenca_mes']))} no mês, {imp['sentido']}" if imp else "não calculado"),
              "", "## Fatos",
              f"- CNAEs: " + "; ".join(f"{c['formatado']} (anexo {c['anexo']}, fator r {c['fator_r']})" for c in r["cnaes"]),
              f"- Fator r: {r['fator_r']:.2%}" if r["fator_r"] is not None else "- Fator r: não calculado",
              f"- Anexo aplicado na apuração: {r['anexo_aplicado'] or 'não informado'} · anexo devido pelos dados: "
              f"{r['anexo_devido'] or 'indefinido'}",
              f"- CNAEs informados nas notas: {', '.join(formatar_cnae(c) for c in r['cnaes_nas_notas']) or 'nenhum'}"]
    if r["exemplos_de_discriminacao"]:
        linhas.append("- Discriminações (amostra): " + " | ".join(r["exemplos_de_discriminacao"]))
    linhas += ["", "## Regra aplicável", "- LC 123/2006, art. 18 (fator r) · ver docs/referencias/fator-r.md", "",
               "## Hipóteses testadas", "| Hipótese | Resultado | Evidência |", "|---|---|---|"]
    for cod, x in r["hipoteses"].items():
        linhas.append(f"| {cod} · {x['hipotese']} | {x['resultado']} | {x['evidencia']} |")
    linhas += ["", "## Ação sugerida", "- (o agente completa: ajuste, retificação, conversa com o cliente; quem decide)"]
    if r["planejamento_fator_r"]:
        p = r["planejamento_fator_r"]
        linhas += ["", "## Oportunidade de planejamento (AT-07)",
                   f"- Faltam {_brl(p['folha_adicional_12_meses'])} de folha em 12 meses (≈ {_brl(p['folha_adicional_media_mes'])}/mês) "
                   f"para o fator r chegar a 28%."
                   + (f" Economia de DAS estimada: {_brl(p['economia_das_mes'])}/mês." if p["economia_das_mes"] else ""),
                   f"- {p['observacao']}"]
    for a in r["alertas"]:
        linhas.append(f"\n> ATENÇÃO · {a}")
    return "\n".join(linhas) + "\n"


def _json(o):
    return str(o) if isinstance(o, Decimal) else o


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AT-01 · Fator R e anexo (III × V).")
    ap.add_argument("dados")
    ap.add_argument("--saida", help="prefixo dos arquivos .json e .md do parecer")
    args = ap.parse_args(argv)
    caminho = Path(args.dados)
    r = analisar(json.loads(caminho.read_text(encoding="utf-8")), base=caminho.parent)
    texto = parecer_rascunho(r)
    print(texto)
    if args.saida:
        Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(f"{args.saida}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1, default=_json), encoding="utf-8")
        Path(f"{args.saida}.md").write_text(texto, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
