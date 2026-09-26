# -*- coding: utf-8 -*-
"""Leitura de NFS-e (padrão Nacional e ABRASF 2.x) para o agente fiscal.

Uso:
    python ferramentas/nfse.py resumo <pasta> --cnpj <CNPJ> [--competencia AAAA-MM] [--saida nfse.json]

O resumo separa as notas prestadas e tomadas pela empresa e agrupa a receita por código de serviço. Ele mostra o ISS
retido, os municípios de incidência e as retenções federais, e é a base das análises AT-01 a AT-05.

A busca dos campos é pelo nome da tag, sem depender do caminho, porque o leiaute ABRASF varia entre prefeituras.
Campos não encontrados ficam vazios e aparecem no aviso "campos ausentes".

Referências (conferidas em 26/09/2026, detalhes em docs/referencias/nfse-e-retencoes.md):
- NFS-e Nacional, XSD 1.01 (NT 007/2026): não tem CNAE. O vRetCSLL traz a soma de PIS, COFINS e CSLL retidos. O
  cancelamento chega em evento separado (e101101; substituição e105102).
- ABRASF 2.x: CodigoCnae vem como inteiro, sem o zero à esquerda. A alíquota pode vir em fração (0,05) ou em
  percentual (5,00). O cancelamento vem em NfseCancelamento.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

NS_NACIONAL = "http://www.sped.fazenda.gov.br/nfse"
NS_ABRASF = "http://www.abrasf.org.br/nfse.xsd"
EVENTOS_CANCELAMENTO = {"e101101", "e105102", "e105104", "e305101"}  # cancelamento, substituição, deferido, de ofício


def so_digitos(texto) -> str:
    return "".join(c for c in str(texto or "") if c.isdigit())


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _achar(el, *nomes):
    """Primeiro descendente (ou o próprio elemento) cujo nome local esteja em `nomes`, na ordem de preferência."""
    if el is None:
        return None
    for nome in nomes:
        for sub in el.iter():
            if _local(sub.tag) == nome:
                return sub
    return None


def _ou(*elementos):
    """Primeiro elemento que não seja None. (Não use `or`: elemento sem filhos conta como falso.)"""
    for e in elementos:
        if e is not None:
            return e
    return None


def _txt(el, *nomes) -> str:
    alvo = _achar(el, *nomes)
    return alvo.text.strip() if alvo is not None and alvo.text else ""


def _dec(el, *nomes) -> Decimal:
    valor = _txt(el, *nomes).replace(",", ".")
    try:
        return Decimal(valor) if valor else Decimal("0")
    except InvalidOperation:
        return Decimal("0")


def _doc(el) -> str:
    return so_digitos(_txt(el, "CNPJ", "Cnpj") or _txt(el, "CPF", "Cpf"))


@dataclass
class NFSe:
    arquivo: str
    padrao: str                 # nacional | abrasf
    numero: str
    chave: str
    emissao: str
    competencia: str
    prestador: str
    prestador_simples: str      # texto do indicador de Simples na nota (quando houver)
    tomador: str
    codigo_servico: str         # cTribNac (nacional) ou ItemListaServico (ABRASF)
    subitem_lc116: str          # subitem da lista da LC 116, no formato "01.01"
    codigo_municipal: str
    cnae: str
    nbs: str
    descricao: str
    municipio_incidencia: str
    valor_servico: Decimal
    aliquota_iss: Decimal
    valor_iss: Decimal
    iss_retido: bool
    ret_irrf: Decimal
    ret_csll: Decimal
    ret_pis: Decimal
    ret_cofins: Decimal
    ret_inss: Decimal
    exigibilidade: str = ""     # nacional: tribISSQN (1 tributável, 2 imune, 3 exportação, 4 não incidência)
    cancelada: bool = False
    ausentes: list = field(default_factory=list)

    @property
    def retencoes_federais(self) -> Decimal:
        return self.ret_irrf + self.ret_csll + self.ret_pis + self.ret_cofins + self.ret_inss


def subitem_lc116(codigo: str) -> str:
    """cTribNac "010101" -> "01.01"; ItemListaServico "1.01", "0101" ou "01.01" -> "01.01"."""
    c = (codigo or "").strip()
    if "." in c:
        item, sub = c.split(".", 1)
        return f"{int(item):02d}.{so_digitos(sub)[:2].zfill(2)}" if item.isdigit() else c
    d = so_digitos(c)
    if len(d) >= 4:
        return f"{d[:2]}.{d[2:4]}"
    if len(d) == 3:
        return f"0{d[0]}.{d[1:]}"
    return c


def _aliquota_pct(v: Decimal) -> Decimal:
    """ABRASF pode trazer 0,05 (fração) ou 5,00 (percentual). Devolve sempre percentual."""
    return v * 100 if 0 < v < 1 else v


def _ler_nacional(raiz, arq) -> NFSe:
    inf = _ou(_achar(raiz, "infNFSe"), raiz)
    dps = _achar(raiz, "infDPS")
    prest = _ou(_achar(dps, "prest"), _achar(inf, "emit"))
    toma = _achar(dps, "toma")
    tp_ret = _txt(raiz, "tpRetISSQN")
    return NFSe(
        arquivo=str(arq), padrao="nacional",
        numero=_txt(inf, "nNFSe"), chave=so_digitos(inf.get("Id", "")),
        emissao=(_txt(dps, "dhEmi") or _txt(inf, "dhProc"))[:10], competencia=_txt(dps, "dCompet")[:7],
        prestador=_doc(prest), prestador_simples=_txt(prest, "opSimpNac"), tomador=_doc(toma),
        codigo_servico=_txt(raiz, "cTribNac"), subitem_lc116=subitem_lc116(_txt(raiz, "cTribNac")),
        codigo_municipal=_txt(raiz, "cTribMun"), cnae="",
        nbs=_txt(raiz, "cNBS"), descricao=_txt(raiz, "xDescServ"),
        municipio_incidencia=_txt(inf, "cLocIncid") or _txt(raiz, "cLocPrestacao"),
        valor_servico=_dec(raiz, "vServ"), aliquota_iss=_dec(raiz, "pAliqAplic", "pAliq"),
        valor_iss=_dec(inf, "vISSQN"), iss_retido=tp_ret in ("2", "3"),
        # NT 007/2026: vRetCSLL = PIS + COFINS + CSLL retidos; vPis/vCofins são débito próprio, não retenção
        ret_irrf=_dec(raiz, "vRetIRRF"), ret_csll=_dec(raiz, "vRetCSLL"), ret_pis=Decimal("0"),
        ret_cofins=Decimal("0"), ret_inss=_dec(raiz, "vRetCP"), exigibilidade=_txt(raiz, "tribISSQN"),
    )


def _ler_abrasf(raiz, arq) -> NFSe:
    inf = _ou(_achar(raiz, "InfNfse"), raiz)
    serv = _achar(raiz, "Servico")
    prest = _achar(raiz, "PrestadorServico", "Prestador", "IdentificacaoPrestador")
    toma = _achar(raiz, "TomadorServico", "Tomador", "IdentificacaoTomador")
    return NFSe(
        arquivo=str(arq), padrao="abrasf",
        numero=_txt(inf, "Numero"), chave=_txt(inf, "CodigoVerificacao"),
        emissao=_txt(inf, "DataEmissao")[:10], competencia=_txt(raiz, "Competencia")[:7],
        prestador=_doc(prest), prestador_simples=_txt(raiz, "OptanteSimplesNacional"), tomador=_doc(toma),
        codigo_servico=_txt(serv, "ItemListaServico"), subitem_lc116=subitem_lc116(_txt(serv, "ItemListaServico")),
        codigo_municipal=_txt(serv, "CodigoTributacaoMunicipio"),
        cnae=so_digitos(_txt(serv, "CodigoCnae")).zfill(7) if so_digitos(_txt(serv, "CodigoCnae")) else "",
        nbs=_txt(serv, "CodigoNbs"), descricao=_txt(serv, "Discriminacao"),
        municipio_incidencia=_txt(serv, "MunicipioIncidencia") or _txt(serv, "CodigoMunicipio"),
        valor_servico=_dec(serv, "ValorServicos"), aliquota_iss=_aliquota_pct(_dec(serv, "Aliquota")),
        valor_iss=_dec(serv, "ValorIss") or _dec(inf, "ValorIss"), iss_retido=_txt(serv, "IssRetido") == "1",
        ret_irrf=_dec(serv, "ValorIr"), ret_csll=_dec(serv, "ValorCsll"), ret_pis=_dec(serv, "ValorPis"),
        ret_cofins=_dec(serv, "ValorCofins"), ret_inss=_dec(serv, "ValorInss"),
        exigibilidade=_txt(serv, "ExigibilidadeISS"), cancelada=_achar(raiz, "NfseCancelamento") is not None,
    )


OBRIGATORIOS = ("numero", "emissao", "prestador", "codigo_servico", "descricao", "valor_servico")


def chaves_canceladas(arq: Path) -> set:
    """Chaves de NFS-e Nacional canceladas ou substituídas por evento (infPedReg com e101101, e105102...)."""
    raiz = ET.parse(arq).getroot()
    chaves = set()
    for el in raiz.iter():
        if _local(el.tag) == "infPedReg":
            if {_local(e.tag) for e in el.iter()} & EVENTOS_CANCELAMENTO:
                ch = so_digitos(_txt(el, "chNFSe"))
                if ch:
                    chaves.add(ch)
    return chaves


def ler_nfse(arq: Path) -> NFSe | None:
    raiz = ET.parse(arq).getroot()
    tags = {_local(e.tag) for e in raiz.iter()}
    if "infNFSe" in tags or "infDPS" in tags:
        nota = _ler_nacional(raiz, arq)
    elif "InfNfse" in tags or "CompNfse" in tags:
        nota = _ler_abrasf(raiz, arq)
    else:
        return None
    nota.ausentes = [c for c in OBRIGATORIOS if not getattr(nota, c)]
    return nota


def resumo(pasta: Path, cnpj: str, competencia: str | None = None) -> dict:
    cnpj = so_digitos(cnpj)
    prestadas, tomadas, ignorados, fora, vistas = [], [], [], [], set()
    notas, canceladas = [], set()
    for arq in sorted(Path(pasta).rglob("*.xml")):
        try:
            n = ler_nfse(arq)
            if n is None:
                eventos = chaves_canceladas(arq)
                if eventos:
                    canceladas |= eventos
                else:
                    ignorados.append(f"{arq} (não é NFS-e nem evento de cancelamento)")
                continue
        except ET.ParseError as erro:
            ignorados.append(f"{arq} (XML inválido: {erro})")
            continue
        notas.append(n)
    canceladas_lista = []
    for n in notas:
        if n.cancelada or (n.chave and n.chave in canceladas):
            n.cancelada = True
            if n.prestador == cnpj or n.tomador == cnpj:
                canceladas_lista.append(n.numero)
            continue
        chave = (n.prestador, n.numero, n.chave)
        if chave in vistas:
            continue
        vistas.add(chave)
        if competencia and (n.competencia or n.emissao[:7]) != competencia:
            fora.append(n.numero)
        if n.prestador == cnpj:
            prestadas.append(n)
        elif n.tomador == cnpj:
            tomadas.append(n)
        else:
            ignorados.append(f"{n.arquivo} (não envolve o CNPJ {cnpj})")

    def por_servico(lista):
        grupos = defaultdict(lambda: {"notas": 0, "valor": Decimal("0"), "iss_retido": Decimal("0"),
                                      "cnaes_informados": set(), "exemplos": []})
        for n in lista:
            g = grupos[n.subitem_lc116 or n.codigo_servico or "(sem código)"]
            g["notas"] += 1
            g["valor"] += n.valor_servico
            if n.iss_retido:
                g["iss_retido"] += n.valor_servico
            if n.cnae:
                g["cnaes_informados"].add(n.cnae)
            if len(g["exemplos"]) < 3 and n.descricao:
                g["exemplos"].append(n.descricao[:160])
        return {k: {**v, "cnaes_informados": sorted(v["cnaes_informados"])} for k, v in sorted(grupos.items())}

    def bloco(lista):
        return {
            "quantidade": len(lista),
            "valor_total": sum((n.valor_servico for n in lista), Decimal("0")),
            "valor_com_iss_retido": sum((n.valor_servico for n in lista if n.iss_retido), Decimal("0")),
            "retencoes_federais": sum((n.retencoes_federais for n in lista), Decimal("0")),
            "municipios_incidencia": sorted({n.municipio_incidencia for n in lista if n.municipio_incidencia}),
            "por_servico": por_servico(lista),
            "notas": [{k: v for k, v in asdict(n).items() if k != "arquivo"} for n in lista],
        }

    avisos = []
    incompletas = [n.numero or n.arquivo for n in prestadas + tomadas if n.ausentes]
    if incompletas:
        avisos.append(f"Campos ausentes em {len(incompletas)} nota(s): conferir o leiaute da prefeitura.")
    if any(n.retencoes_federais > 0 for n in prestadas):
        avisos.append("Há retenções federais em notas prestadas: ver análise AT-05.")
    return {"cnpj": cnpj, "competencia": competencia, "prestadas": bloco(prestadas), "tomadas": bloco(tomadas),
            "canceladas": sorted(canceladas_lista), "fora_da_competencia": fora, "arquivos_ignorados": ignorados,
            "avisos": avisos}


def _json(o):
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, set):
        return sorted(o)
    return o


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Leitura e resumo de NFS-e (Nacional e ABRASF).")
    sub = ap.add_subparsers(dest="comando", required=True)
    r = sub.add_parser("resumo")
    r.add_argument("pasta")
    r.add_argument("--cnpj", required=True)
    r.add_argument("--competencia")
    r.add_argument("--saida")
    args = ap.parse_args(argv)
    res = resumo(Path(args.pasta), args.cnpj, args.competencia)
    for nome in ("prestadas", "tomadas"):
        b = res[nome]
        print(f"{nome.capitalize()}: {b['quantidade']} notas · R$ {b['valor_total']} · com ISS retido R$ "
              f"{b['valor_com_iss_retido']} · retenções federais R$ {b['retencoes_federais']}")
        for cod, g in b["por_servico"].items():
            print(f"   serviço {cod}: {g['notas']} notas · R$ {g['valor']}"
                  + (f" · CNAE na nota {', '.join(g['cnaes_informados'])}" if g["cnaes_informados"] else ""))
    for aviso in res["avisos"]:
        print("ATENÇÃO · " + aviso)
    if args.saida:
        Path(args.saida).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=_json), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
