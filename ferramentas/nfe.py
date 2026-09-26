# -*- coding: utf-8 -*-
"""Leitura de XML de NF-e/NFC-e (modelos 55 e 65) para o agente fiscal.

Uso na linha de comando:
    python ferramentas/nfe.py resumo <pasta> --cnpj <CNPJ> [--competencia AAAA-MM] [--saida documentos.json]

O resumo separa as notas em saídas (emitidas pela empresa) e entradas (recebidas de terceiros), soma valores e
aponta canceladas, duplicadas e notas fora da competência.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from pathlib import Path

NS = "{http://www.portalfiscal.inf.br/nfe}"
EVENTO_CANCELAMENTO = "110111"


def so_digitos(texto: str) -> str:
    return "".join(c for c in (texto or "") if c.isdigit())


def _txt(el, caminho: str) -> str:
    if el is None:
        return ""
    alvo = el.find(caminho.replace("n:", NS))
    return alvo.text.strip() if alvo is not None and alvo.text else ""


def _dec(el, caminho: str) -> Decimal:
    valor = _txt(el, caminho)
    return Decimal(valor) if valor else Decimal("0")


@dataclass
class Item:
    numero: int
    cprod: str
    xprod: str
    ncm: str
    cest: str
    cfop: str
    orig: str
    cst: str            # CST (regime normal) ou CSOSN (Simples Nacional)
    v_prod: Decimal
    v_frete: Decimal
    v_seg: Decimal
    v_outro: Decimal
    v_desc: Decimal
    v_bc: Decimal
    p_icms: Decimal
    v_icms: Decimal
    v_bc_st: Decimal
    v_icms_st: Decimal
    p_cred_sn: Decimal
    v_cred_sn: Decimal
    v_ipi: Decimal
    tem_ibscbs: bool

    @property
    def st_retida_na_nota(self) -> bool:
        """O fornecedor reteve ICMS-ST nesta nota."""
        return self.v_icms_st > 0

    @property
    def st_encerrada_antes(self) -> bool:
        """ICMS cobrado anteriormente por substituição tributária (CST 60 ou CSOSN 500)."""
        return self.cst in ("60", "500")

    def valor_operacao(self, incluir_ipi: bool = False) -> Decimal:
        valor = self.v_prod + self.v_frete + self.v_seg + self.v_outro - self.v_desc
        return valor + self.v_ipi if incluir_ipi else valor


@dataclass
class Nota:
    arquivo: str
    chave: str
    modelo: str
    serie: str
    numero: str
    emissao: str
    tp_nf: str          # 0 = entrada, 1 = saída (do ponto de vista do emitente)
    fin_nfe: str
    id_dest: str
    emit_cnpj: str
    emit_nome: str
    emit_uf: str
    emit_crt: str       # 1 Simples, 2 Simples com excesso, 3 regime normal, 4 MEI
    dest_doc: str
    dest_nome: str
    dest_uf: str
    v_nf: Decimal
    v_prod: Decimal
    v_icms: Decimal
    v_st: Decimal
    v_ipi: Decimal
    status: str
    itens: list = field(default_factory=list)

    @property
    def competencia(self) -> str:
        return self.emissao[:7]


def _ler_item(det) -> Item:
    prod = det.find(f"{NS}prod")
    imposto = det.find(f"{NS}imposto")
    icms_grupo = imposto.find(f"{NS}ICMS") if imposto is not None else None
    icms = list(icms_grupo)[0] if icms_grupo is not None and len(icms_grupo) else None
    cst = _txt(icms, "n:CST") or _txt(icms, "n:CSOSN")
    ipi = imposto.find(f"{NS}IPI/{NS}IPITrib") if imposto is not None else None
    return Item(
        numero=int(det.get("nItem", "0")),
        cprod=_txt(prod, "n:cProd"),
        xprod=_txt(prod, "n:xProd"),
        ncm=_txt(prod, "n:NCM"),
        cest=_txt(prod, "n:CEST"),
        cfop=_txt(prod, "n:CFOP"),
        orig=_txt(icms, "n:orig"),
        cst=cst,
        v_prod=_dec(prod, "n:vProd"),
        v_frete=_dec(prod, "n:vFrete"),
        v_seg=_dec(prod, "n:vSeg"),
        v_outro=_dec(prod, "n:vOutro"),
        v_desc=_dec(prod, "n:vDesc"),
        v_bc=_dec(icms, "n:vBC"),
        p_icms=_dec(icms, "n:pICMS"),
        v_icms=_dec(icms, "n:vICMS"),
        v_bc_st=_dec(icms, "n:vBCST"),
        v_icms_st=_dec(icms, "n:vICMSST"),
        p_cred_sn=_dec(icms, "n:pCredSN"),
        v_cred_sn=_dec(icms, "n:vCredICMSSN"),
        v_ipi=_dec(ipi, "n:vIPI"),
        tem_ibscbs=imposto is not None and imposto.find(f"{NS}IBSCBS") is not None,
    )


def ler_nota(caminho: Path) -> Nota | None:
    """Lê um XML de NF-e/NFC-e. Devolve None se o arquivo não for uma nota (ex.: evento, CT-e)."""
    raiz = ET.parse(caminho).getroot()
    inf = raiz.find(f".//{NS}infNFe")
    if inf is None:
        return None
    ide, emit, dest, tot = (inf.find(f"{NS}{t}") for t in ("ide", "emit", "dest", "total"))
    icms_tot = tot.find(f"{NS}ICMSTot") if tot is not None else None
    prot = raiz.find(f".//{NS}protNFe/{NS}infProt")
    c_stat = _txt(prot, "n:cStat")
    status = "autorizada" if c_stat in ("100", "150") else (f"cStat {c_stat}" if c_stat else "sem protocolo")
    return Nota(
        arquivo=str(caminho),
        chave=so_digitos(inf.get("Id", "")),
        modelo=_txt(ide, "n:mod"),
        serie=_txt(ide, "n:serie"),
        numero=_txt(ide, "n:nNF"),
        emissao=(_txt(ide, "n:dhEmi") or _txt(ide, "n:dEmi"))[:10],
        tp_nf=_txt(ide, "n:tpNF"),
        fin_nfe=_txt(ide, "n:finNFe"),
        id_dest=_txt(ide, "n:idDest"),
        emit_cnpj=so_digitos(_txt(emit, "n:CNPJ") or _txt(emit, "n:CPF")),
        emit_nome=_txt(emit, "n:xNome"),
        emit_uf=_txt(emit, "n:enderEmit/n:UF"),
        emit_crt=_txt(emit, "n:CRT"),
        dest_doc=so_digitos(_txt(dest, "n:CNPJ") or _txt(dest, "n:CPF")),
        dest_nome=_txt(dest, "n:xNome"),
        dest_uf=_txt(dest, "n:enderDest/n:UF"),
        v_nf=_dec(icms_tot, "n:vNF"),
        v_prod=_dec(icms_tot, "n:vProd"),
        v_icms=_dec(icms_tot, "n:vICMS"),
        v_st=_dec(icms_tot, "n:vST"),
        v_ipi=_dec(icms_tot, "n:vIPI"),
        status=status,
        itens=[_ler_item(det) for det in inf.findall(f"{NS}det")],
    )


def chaves_canceladas(caminho: Path) -> set:
    """Chaves canceladas por evento (procEventoNFe com tpEvento 110111) encontradas no arquivo."""
    raiz = ET.parse(caminho).getroot()
    canceladas = set()
    for ev in raiz.iter(f"{NS}infEvento"):
        if _txt(ev, "n:tpEvento") == EVENTO_CANCELAMENTO:
            canceladas.add(so_digitos(_txt(ev, "n:chNFe")))
    return canceladas


def ler_pasta(pasta: Path) -> tuple[list, set, list]:
    """Lê todos os XML da pasta (recursivo). Devolve (notas, chaves canceladas, arquivos ignorados)."""
    notas, canceladas, ignorados = [], set(), []
    for arq in sorted(Path(pasta).rglob("*")):
        if not arq.is_file() or arq.suffix.lower() != ".xml":
            continue
        try:
            nota = ler_nota(arq)
            if nota is not None:
                notas.append(nota)
            else:
                encontrados = chaves_canceladas(arq)
                if encontrados:
                    canceladas |= encontrados
                else:
                    ignorados.append(f"{arq} (não é NF-e nem cancelamento)")
        except ET.ParseError as erro:
            ignorados.append(f"{arq} (XML inválido: {erro})")
    return notas, canceladas, ignorados


def resumo(pasta: Path, cnpj: str, competencia: str | None = None) -> dict:
    cnpj = so_digitos(cnpj)
    notas, canceladas, ignorados = ler_pasta(pasta)
    grupos = {"saidas": [], "entradas": [], "entradas_proprias": [], "outras": []}
    vistas, duplicadas, fora = set(), [], []
    for n in notas:
        if n.chave in vistas:
            duplicadas.append(n.chave)
            continue
        vistas.add(n.chave)
        if n.emit_cnpj == cnpj:
            grupos["saidas" if n.tp_nf == "1" else "entradas_proprias"].append(n)
        elif n.dest_doc == cnpj:
            grupos["entradas"].append(n)
        else:
            grupos["outras"].append(n)
        if competencia and n.competencia != competencia:
            fora.append(n.chave)

    def bloco(lista):
        validas = [n for n in lista if n.chave not in canceladas]
        return {
            "quantidade": len(validas),
            "valor_total": str(sum((n.v_nf for n in validas), Decimal("0"))),
            "canceladas": sorted(n.chave for n in lista if n.chave in canceladas),
            "sem_autorizacao": sorted(n.chave for n in validas if n.status != "autorizada"),
            "notas": [{"chave": n.chave, "numero": n.numero, "serie": n.serie, "emissao": n.emissao,
                       "emitente": n.emit_nome, "uf_origem": n.emit_uf, "valor": str(n.v_nf)} for n in validas],
        }

    return {
        "cnpj": cnpj,
        "competencia": competencia,
        "saidas": bloco(grupos["saidas"]),
        "entradas": bloco(grupos["entradas"]),
        "entradas_proprias": bloco(grupos["entradas_proprias"]),
        "de_outras_empresas": [n.chave for n in grupos["outras"]],
        "duplicadas": duplicadas,
        "fora_da_competencia": fora,
        "arquivos_ignorados": ignorados,
    }


def _imprimir(r: dict) -> None:
    print(f"CNPJ {r['cnpj']} · competência {r['competencia'] or '(não informada)'}")
    for nome, chave in (("Saídas", "saidas"), ("Entradas de terceiros", "entradas"),
                        ("Entradas emitidas pela empresa", "entradas_proprias")):
        b = r[chave]
        print(f"  {nome}: {b['quantidade']} notas, R$ {b['valor_total']}"
              + (f" · {len(b['canceladas'])} canceladas" if b["canceladas"] else ""))
    for rotulo, chave in (("De outras empresas", "de_outras_empresas"), ("Duplicadas", "duplicadas"),
                          ("Fora da competência", "fora_da_competencia"), ("Ignorados", "arquivos_ignorados")):
        if r[chave]:
            print(f"  ATENÇÃO · {rotulo}: {len(r[chave])}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Leitura e resumo de XML de NF-e/NFC-e.")
    sub = ap.add_subparsers(dest="comando", required=True)
    r = sub.add_parser("resumo", help="resume os XML de uma pasta")
    r.add_argument("pasta")
    r.add_argument("--cnpj", required=True)
    r.add_argument("--competencia", help="AAAA-MM")
    r.add_argument("--saida", help="arquivo JSON para gravar o resumo")
    args = ap.parse_args(argv)
    res = resumo(Path(args.pasta), args.cnpj, args.competencia)
    _imprimir(res)
    if args.saida:
        Path(args.saida).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
