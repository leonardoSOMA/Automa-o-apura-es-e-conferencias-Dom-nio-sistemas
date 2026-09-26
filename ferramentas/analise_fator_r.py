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
  "rbt12": "360000.00", "folha12": "43200.00", "anexo_aplicado": "III",
  "folha_confirmada": false,        # true quando o DP confirmou a folha dos 12 meses, inclusive folha zero
  "rbt12_fator_r": "360000.00"      # opcional: receita dos 12 meses por competência, se a empresa apura por caixa
}

Nos acumuladores, "fator_r" = "S" quando a troca automática entre os Anexos III e V está marcada na Domínio; "N"
quando o anexo é fixo. Na tabela de CNAE, fator_r = "S" (sujeito), "N" (não sujeito) ou "D" (depende do serviço).

A ferramenta não decide sozinha quando a nota não traz o CNAE e a empresa tem atividades sujeitas e não sujeitas.
Nesse caso, a conclusão fica em "Indício" e o agente lê as discriminações das notas para testar a hipótese H2.
Regras e fontes: docs/referencias/fator-r.md.
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
FATOR_SEM_FOLHA = Decimal("0.01")    # há receita e não há folha (Res. CGSN 140/2018, art. 26)
FATOR_SEM_RECEITA = Decimal("0.28")  # há folha e não há receita (Res. CGSN 140/2018, art. 26)
FAIXA_PLANEJAMENTO = Decimal("0.20")
LIMITE_BLOQUEIO = Decimal("50")
INICIO_REGRAS_2027 = "2027-01"

ACOES = {
    "Erro provável": "Ajustar o acumulador (imposto 44 > Definições: troca automática entre os Anexos III e V) e "
                     "avaliar a retificação dos PGDAS-D dos meses afetados. Decide: sócio.",
    "Oportunidade": "Corrigir a configuração e avaliar a retificação dos PGDAS-D com pedido de restituição ou "
                    "compensação. Decide: sócio.",
    "Risco latente": "Corrigir a configuração do acumulador antes que o fator r mude. O DAS de hoje não muda. "
                     "Decide: coordenador.",
    "Indício, falta informação": "Levantar o que falta (ver hipóteses inconclusivas) e rodar de novo. Quem tem: DP "
                                 "(folha) e cliente (serviço prestado).",
    "Situação justificada": "Nenhuma.",
}


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
                      "fator_r": info.get("fator_r", "?"), "observacao": info.get("observacao", "")})
    return saida


def meses_entre(inicio: str, competencia: str) -> int:
    a = date.fromisoformat(inicio[:10])
    ano, mes = (int(x) for x in competencia.split("-"))
    return (ano - a.year) * 12 + (mes - a.month)


def calcular_fator_r(receita12: Decimal, folha12: Decimal, folha_informada: bool) -> tuple:
    """Fator r e a regra usada (LC 123, art. 18 §§5º-J, 5º-K e 24; Res. CGSN 140, art. 26 nos valores zero)."""
    if not folha_informada:
        return None, "folha dos 12 meses não informada"
    if receita12 > 0 and folha12 > 0:
        return folha12 / receita12, "folha dos 12 meses ÷ receita dos 12 meses"
    if receita12 > 0:
        return FATOR_SEM_FOLHA, "sem folha e com receita: fator r de 0,01 (Res. CGSN 140, art. 26)"
    if folha12 > 0:
        return FATOR_SEM_RECEITA, "com folha e sem receita: fator r de 0,28 (Res. CGSN 140, art. 26)"
    return None, "sem folha e sem receita nos 12 meses: conferir a regra de início de atividade"


def _codigos(acumuladores: list) -> str:
    return ", ".join(str(a.get("codigo", "?")) for a in acumuladores)


def analisar(dados: dict, tabela: dict | None = None, base: Path = Path(".")) -> dict:
    tabela = carregar_tabela() if tabela is None else tabela
    cnpj_info = _ler_json(dados.get("cnpj_json"), base) or {}
    nfse_info = _ler_json(dados.get("nfse_json"), base) or {}
    cnaes = classificar(dados.get("cnaes") or cnpj_info.get("cnaes") or [], tabela)
    codigos_empresa = {c["codigo"] for c in cnaes}
    sujeitos = [c for c in cnaes if c["fator_r"] == "S"]
    dependem = [c for c in cnaes if c["fator_r"] == "D"]
    nao_sujeitos = [c for c in cnaes if c["fator_r"] == "N"]
    nao_sujeitos_iii = [c for c in nao_sujeitos if c["anexo"] == "III"]
    sem_classificacao = [c for c in cnaes if c["anexo"] == "?"]

    rbt12, folha12 = _d(dados.get("rbt12")), _d(dados.get("folha12"))
    folha_informada = dados.get("folha12") not in (None, "")
    folha_confirmada = bool(dados.get("folha_confirmada"))
    receita12 = _d(dados["rbt12_fator_r"]) if dados.get("rbt12_fator_r") not in (None, "") else rbt12
    fator_r, regra_fator_r = calcular_fator_r(receita12, folha12, folha_informada)
    folha_para_28 = (LIMITE_FATOR_R * receita12).quantize(Decimal("0.01")) if receita12 > 0 else None
    anexo_aplicado = (dados.get("anexo_aplicado") or "").upper()

    # receitas do mês: da entrada ou do resumo de NFS-e (prestadas)
    receitas = dados.get("receitas")
    prestadas = nfse_info.get("prestadas", {})
    if not receitas and prestadas:
        total, retido = _d(prestadas.get("valor_total")), _d(prestadas.get("valor_com_iss_retido"))
        receitas = [r for r in ({"tipo": "normal", "valor": total - retido}, {"tipo": "iss_retido", "valor": retido})
                    if _d(r["valor"]) > 0]
    receitas = receitas or []

    # CNAEs informados nas notas (ABRASF traz; a NFS-e nacional não tem o campo)
    cnaes_notas = set()
    for g in (prestadas.get("por_servico") or {}).values():
        cnaes_notas |= {so_digitos(c).zfill(7) for c in g.get("cnaes_informados", [])}
    notas_sujeitas = {c for c in cnaes_notas if tabela.get(c, {}).get("fator_r") == "S"}
    notas_nao_sujeitas = {c for c in cnaes_notas if tabela.get(c, {}).get("fator_r") == "N"}
    notas_indefinidas = cnaes_notas - notas_sujeitas - notas_nao_sujeitas  # "D" ou fora da tabela
    notas_fora_do_cnpj = cnaes_notas - codigos_empresa
    exemplos = [e for g in (prestadas.get("por_servico") or {}).values() for e in g.get("exemplos", [])][:6]

    # a receita do mês é de atividade sujeita ao fator r? True, False ou None (só lendo as notas)
    so_sujeitas = bool(sujeitos) and not (nao_sujeitos or dependem or sem_classificacao)
    so_nao_sujeitas = bool(nao_sujeitos) and not (sujeitos or dependem or sem_classificacao)
    if notas_sujeitas and (notas_nao_sujeitas or notas_indefinidas):
        faturamento_sujeito, motivo = None, "As notas do mês trazem CNAE sujeito e não sujeito: separar a receita por atividade."
    elif notas_sujeitas:
        faturamento_sujeito, motivo = True, ""
    elif notas_nao_sujeitas and not notas_indefinidas:
        faturamento_sujeito, motivo = False, ""
    elif cnaes_notas:
        faturamento_sujeito, motivo = None, ("As notas trazem CNAE que depende do serviço ou que não está na tabela: "
                                             "ler as discriminações.")
    elif so_sujeitas:
        faturamento_sujeito, motivo = True, ""
    elif so_nao_sujeitas:
        faturamento_sujeito, motivo = False, ""
    else:
        faturamento_sujeito, motivo = None, ("A empresa tem atividades sujeitas e não sujeitas (ou que dependem do "
                                             "serviço) e as notas não trazem CNAE: ler as discriminações.")

    acumuladores = dados.get("acumuladores") or []
    com_troca = [a for a in acumuladores if str(a.get("fator_r", "")).upper() == "S"]
    fixos = [a for a in acumuladores if str(a.get("fator_r", "")).upper() != "S"]
    iii_fixo = [a for a in fixos if str(a.get("anexo", "")).upper() == "III"]
    v_fixo = [a for a in fixos if str(a.get("anexo", "")).upper() == "V"]

    h = {}

    def hip(cod, titulo, resultado, evidencia):
        h[cod] = {"hipotese": titulo, "resultado": resultado, "evidencia": evidencia}

    # H1 · acumulador errado
    t1 = "Acumulador errado (atividade sujeita configurada como Anexo III fixo)"
    if not (sujeitos or dependem or notas_sujeitas):
        hip("H1", t1, "enfraquece", "A empresa não tem CNAE sujeito ao fator r na tabela.")
    elif fator_r is None:
        hip("H1", t1, "inconclusivo", f"Fator r não calculado: {regra_fator_r}.")
    elif fator_r >= LIMITE_FATOR_R:
        hip("H1", t1, "enfraquece", f"Fator r {fator_r:.2%}: para atividade sujeita, o Anexo III é o correto.")
    elif anexo_aplicado == "V":
        hip("H1", t1, "enfraquece", "A apuração já usa o Anexo V.")
    elif faturamento_sujeito and notas_sujeitas:
        hip("H1", t1, "reforça",
            f"Notas com CNAE sujeito ({', '.join(formatar_cnae(c) for c in sorted(notas_sujeitas))}), fator r "
            f"{fator_r:.2%} e apuração no Anexo {anexo_aplicado or '?'}."
            + (f" Acumulador(es) no Anexo III fixo: {_codigos(iii_fixo)}." if iii_fixo else ""))
    elif faturamento_sujeito:
        hip("H1", t1, "reforça",
            f"Todos os CNAEs da empresa são sujeitos ao fator r e o fator r é {fator_r:.2%}. Salvo atividade fora do "
            f"cadastro (H3), o faturamento é de atividade sujeita, e a apuração usou o Anexo {anexo_aplicado or '?'}.")
    elif faturamento_sujeito is False:
        hip("H1", t1, "enfraquece", "As notas com CNAE informado são de atividade não sujeita.")
    else:
        hip("H1", t1, "inconclusivo", motivo)

    # H2 · outra atividade, não sujeita
    t2 = "Outra atividade, não sujeita ao fator r"
    if not (nao_sujeitos_iii or dependem or notas_nao_sujeitas):
        hip("H2", t2, "enfraquece", "A empresa não tem CNAE do Anexo III fora do fator r.")
    elif faturamento_sujeito is False:
        hip("H2", t2, "reforça",
            (f"Notas emitidas com CNAE não sujeito: {', '.join(formatar_cnae(c) for c in sorted(notas_nao_sujeitas))}."
             if notas_nao_sujeitas else "Todos os CNAEs da empresa são de atividade não sujeita."))
    elif faturamento_sujeito:
        hip("H2", t2, "enfraquece", "Há notas com CNAE sujeito ao fator r." if notas_sujeitas
            else "A empresa só tem CNAE sujeito ao fator r.")
    else:
        hip("H2", t2, "inconclusivo",
            "A empresa tem CNAE não sujeito ou que depende do serviço ("
            + ", ".join(c["formatado"] for c in nao_sujeitos_iii + dependem)
            + f"). {motivo}")

    # H3 · CNAE desatualizado
    hip("H3", "CNAE desatualizado no CNPJ", "reforça" if notas_fora_do_cnpj else "enfraquece",
        (f"Notas com CNAE fora do cadastro: {', '.join(formatar_cnae(c) for c in sorted(notas_fora_do_cnpj))}."
         if notas_fora_do_cnpj else "Os CNAEs informados nas notas estão no cadastro (ou não foram informados)."))

    # H4 · fator r ≥ 28%
    if fator_r is None:
        hip("H4", "Fator r ≥ 28% (Anexo III correto)", "inconclusivo", f"Fator r não calculado: {regra_fator_r}.")
    else:
        hip("H4", "Fator r ≥ 28% (Anexo III correto)", "reforça" if fator_r >= LIMITE_FATOR_R else "enfraquece",
            f"Folha 12 meses R$ {folha12} e receita 12 meses R$ {receita12}: fator r {fator_r:.2%} ({regra_fator_r}).")

    # H5 · folha errada ou ausente
    t5 = "Folha errada ou ausente na Domínio"
    if not folha_informada:
        hip("H5", t5, "reforça", "A folha dos 12 meses não foi informada.")
    elif folha12 == 0 and folha_confirmada:
        hip("H5", t5, "enfraquece", "Folha zero confirmada pelo DP: o fator r é 0,01 (Res. CGSN 140, art. 26).")
    elif folha12 == 0:
        hip("H5", t5, "reforça",
            "Folha dos 12 meses igual a zero: confirmar com o DP (salários, pró-labore, FGTS e INSS entram na folha). "
            "Se não houver folha nem pró-labore, o fator r é 0,01 (Res. CGSN 140, art. 26) e a atividade sujeita vai "
            "para o Anexo V.")
    elif folha_confirmada:
        hip("H5", t5, "enfraquece", "Folha dos 12 meses conferida com o DP.")
    else:
        hip("H5", t5, "a conferir", "Comparar a folha usada pela Domínio com a Domínio Folha ou o eSocial.")

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
    if faturamento_sujeito and fator_r is not None:
        anexo_devido = "III" if fator_r >= LIMITE_FATOR_R else "V"
    elif faturamento_sujeito is False:
        anexos = ({tabela.get(c, {}).get("anexo") for c in notas_nao_sujeitas} if notas_nao_sujeitas
                  else {c["anexo"] for c in nao_sujeitos})
        anexo_devido = anexos.pop() if len(anexos) == 1 else None
    impacto = None
    if (anexo_devido in ("III", "V") and anexo_aplicado in ("III", "V") and anexo_devido != anexo_aplicado
            and receitas and rbt12 > 0):
        calc = {a: das_simples.calcular(rbt12, [(a, r["tipo"], _d(r["valor"])) for r in receitas])["das_total"]
                for a in (anexo_aplicado, anexo_devido)}
        dif = calc[anexo_devido] - calc[anexo_aplicado]
        impacto = {"das_aplicado": calc[anexo_aplicado], "das_devido": calc[anexo_devido], "diferenca_mes": dif,
                   "sentido": "pago a menor" if dif > 0 else "pago a maior"}

    # configuração da Domínio: causa provável do erro ou risco latente (erro que ainda não mudou o DAS)
    configuracao = []
    risco_latente = False
    if faturamento_sujeito and fator_r is not None and acumuladores and (so_sujeitas or not com_troca):
        if iii_fixo and fator_r >= LIMITE_FATOR_R:
            risco_latente = True
            configuracao.append(
                f"Acumulador(es) {_codigos(iii_fixo)} no Anexo III fixo, sem a troca automática. Hoje o fator r é "
                f"{fator_r:.2%} e o III está certo. "
                + (f"Se a folha dos 12 meses ficar abaixo de {_brl(folha_para_28)} (hoje {_brl(folha12)}), o fator r "
                   f"cai abaixo de 28%" if folha_para_28 is not None else "Se o fator r cair abaixo de 28%")
                + ", a Domínio continua no III e o DAS sai menor que o devido.")
        elif iii_fixo and anexo_aplicado == "III":
            configuracao.append(f"Acumulador(es) {_codigos(iii_fixo)} no Anexo III fixo, sem a troca automática: "
                                f"causa provável do DAS a menor.")
        elif v_fixo and fator_r < LIMITE_FATOR_R:
            risco_latente = True
            configuracao.append(
                f"Acumulador(es) {_codigos(v_fixo)} no Anexo V fixo, sem a troca automática. Hoje o fator r é "
                f"{fator_r:.2%} e o V está certo. "
                + (f"Quando a folha dos 12 meses chegar a {_brl(folha_para_28)}, o fator r chega a 28%"
                   if folha_para_28 is not None else "Quando o fator r chegar a 28%")
                + ", a Domínio continua no V e o DAS sai maior que o devido.")
        elif v_fixo and anexo_aplicado == "V":
            configuracao.append(f"Acumulador(es) {_codigos(v_fixo)} no Anexo V fixo, sem a troca automática: causa "
                                f"provável do DAS a maior.")
    elif faturamento_sujeito and impacto and com_troca:
        configuracao.append("Os acumuladores têm a troca automática, mas o anexo aplicado diverge do fator r: conferir "
                            "a folha informada na Domínio (Movimentos > Outros > Simples Nacional > Valor da Folha).")
    if faturamento_sujeito is False and not (sujeitos or dependem) and com_troca:
        risco_latente = True
        configuracao.append(
            f"Acumulador(es) {_codigos(com_troca)} com a troca automática do fator r, mas a empresa não tem atividade "
            f"sujeita. Com o fator r abaixo de 28%, a Domínio leva a receita para o Anexo V e o DAS sai maior que o "
            f"devido.")

    # conclusão preliminar
    if faturamento_sujeito is False:
        if impacto and impacto["sentido"] == "pago a maior":
            conclusao = "Oportunidade"
        elif anexo_aplicado == "V" or (anexo_devido and anexo_aplicado and anexo_devido != anexo_aplicado):
            conclusao = "Indício, falta informação"
        elif risco_latente:
            conclusao = "Risco latente"
        else:
            conclusao = "Situação justificada"
    elif fator_r is None or (folha12 == 0 and not folha_confirmada) or faturamento_sujeito is None:
        conclusao = "Indício, falta informação"
    elif impacto and impacto["sentido"] == "pago a menor":
        conclusao = "Erro provável"
    elif impacto and impacto["sentido"] == "pago a maior":
        conclusao = "Oportunidade"
    elif anexo_aplicado not in ("III", "V"):
        conclusao = "Indício, falta informação"
    elif risco_latente:
        conclusao = "Risco latente"
    else:
        conclusao = "Situação justificada"

    planejamento = None
    if (faturamento_sujeito is not False and (sujeitos or notas_sujeitas) and fator_r is not None
            and FAIXA_PLANEJAMENTO <= fator_r < LIMITE_FATOR_R and receita12 > 0):
        adicional = LIMITE_FATOR_R * receita12 - folha12
        economia = None
        if receitas and rbt12 > 0:
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
    for c in dependem:
        alertas.append(f"CNAE {c['formatado']}: a sujeição ao fator r depende do serviço faturado. "
                       f"{c['observacao']}".strip())
    if faturamento_sujeito and anexo_aplicado == "IV":
        alertas.append("Atividade sujeita ao fator r apurada no Anexo IV: conferir o acumulador.")
    if faturamento_sujeito is False and anexo_devido == "IV" and anexo_aplicado and anexo_aplicado != "IV":
        alertas.append(f"Atividade do Anexo IV apurada no Anexo {anexo_aplicado}: conferir o acumulador e a CPP (AT-06).")
    if (dados.get("competencia") or "") >= INICIO_REGRAS_2027:
        alertas.append("Competência de 2027 em diante: a janela dos 12 meses e as tabelas mudam (LC 214/2025 e Res. "
                       "CGSN 190/2026). O impacto aqui usa as tabelas de 2026: conferir antes de concluir.")
    if not TABELA_CNAE.exists() and not tabela:
        alertas.append(f"Tabela {TABELA_CNAE} não encontrada.")
    bloqueia = conclusao == "Erro provável" and impacto is not None and abs(impacto["diferenca_mes"]) > LIMITE_BLOQUEIO
    return {"analise": "AT-01", "empresa": dados.get("empresa"), "competencia": dados.get("competencia"),
            "cnaes": cnaes, "fator_r": fator_r, "regra_fator_r": regra_fator_r, "folha_para_28": folha_para_28,
            "anexo_aplicado": anexo_aplicado, "anexo_devido": anexo_devido, "faturamento_sujeito": faturamento_sujeito,
            "receitas": receitas, "acumuladores": acumuladores, "cnaes_nas_notas": sorted(cnaes_notas),
            "exemplos_de_discriminacao": exemplos, "hipoteses": h, "configuracao": configuracao,
            "conclusao_preliminar": conclusao, "acao_sugerida": ACOES[conclusao], "impacto": impacto,
            "bloqueia_transmissao": bloqueia, "planejamento_fator_r": planejamento, "alertas": alertas}


def _brl(v) -> str:
    return das_simples._brl(Decimal(v))


REGRAS = [
    "- LC 123/2006, art. 18 §§5º-I e 5º-M: atividades sujeitas ao fator r; §5º-J: Anexo III quando o fator r é igual ou "
    "maior que 28%; §5º-K: folha paga e receita auferida nos 12 meses anteriores ao período de apuração.",
    "- LC 123/2006, art. 18 §§24 a 26: a folha inclui salários, pró-labore, FGTS e contribuição patronal recolhidos; "
    "não inclui aluguéis nem distribuição de lucros.",
    "- Res. CGSN 140/2018, art. 26: sem folha e com receita, fator r de 0,01; com folha e sem receita, 0,28.",
    "- Referência conferida: docs/referencias/fator-r.md",
]


def parecer_rascunho(r: dict) -> str:
    emp = r.get("empresa") or {}
    imp = r.get("impacto")
    linhas = [f"# AT-01 · Fator R e anexo · {emp.get('razao_social', '')} ({emp.get('codigo', '')}) · {r.get('competencia')}",
              f"Conclusão preliminar: **{r['conclusao_preliminar']}** (o agente confirma ou corrige lendo as notas)",
              "Impacto: " + (f"{_brl(abs(imp['diferenca_mes']))} no mês, {imp['sentido']}" if imp else "não calculado"),
              "", "## Fatos",
              f"- CNAEs: " + "; ".join(f"{c['formatado']} (anexo {c['anexo']}, fator r {c['fator_r']})" for c in r["cnaes"]),
              (f"- Fator r: {r['fator_r']:.2%} ({r['regra_fator_r']})" if r["fator_r"] is not None
               else f"- Fator r: não calculado ({r['regra_fator_r']})"),
              f"- Anexo aplicado na apuração: {r['anexo_aplicado'] or 'não informado'} · anexo devido pelos dados: "
              f"{r['anexo_devido'] or 'indefinido'}",
              f"- CNAEs informados nas notas: {', '.join(formatar_cnae(c) for c in r['cnaes_nas_notas']) or 'nenhum'}"]
    if r["folha_para_28"] is not None:
        linhas.append(f"- Folha de 12 meses que leva o fator r a 28%: {_brl(r['folha_para_28'])}")
    if r["exemplos_de_discriminacao"]:
        linhas.append("- Discriminações (amostra): " + " | ".join(r["exemplos_de_discriminacao"]))
    linhas += ["", "## Regra aplicável"] + REGRAS + ["", "## Hipóteses testadas", "| Hipótese | Resultado | Evidência |",
                                                       "|---|---|---|"]
    for cod, x in r["hipoteses"].items():
        linhas.append(f"| {cod} · {x['hipotese']} | {x['resultado']} | {x['evidencia']} |")
    if r["configuracao"]:
        linhas += ["", "## Configuração da Domínio"] + [f"- {c}" for c in r["configuracao"]]
    linhas += ["", "## Ação sugerida", f"- {r['acao_sugerida']} (o agente confirma ou ajusta depois de ler as notas)"]
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
