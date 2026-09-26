# -*- coding: utf-8 -*-
"""Gera XML sintéticos de NF-e para os testes (valores fictícios)."""
from pathlib import Path

NS = "http://www.portalfiscal.inf.br/nfe"


def _icms(it: dict) -> str:
    if "csosn" in it:
        tag = "ICMSSN" + {"101": "101", "102": "102", "201": "201", "500": "500", "900": "900"}[it["csosn"]]
        miolo = f"<orig>{it.get('orig', '0')}</orig><CSOSN>{it['csosn']}</CSOSN>"
    else:
        cst = it.get("cst", "00")
        tag = "ICMS" + {"00": "00", "10": "10", "20": "20", "40": "40", "60": "60", "90": "90"}.get(cst, "90")
        miolo = f"<orig>{it.get('orig', '0')}</orig><CST>{cst}</CST>"
    if "picms" in it:
        miolo += f"<vBC>{it.get('vbc', it['vprod'])}</vBC><pICMS>{it['picms']}</pICMS><vICMS>{it['vicms']}</vICMS>"
    if "vicmsst" in it:
        miolo += f"<vBCST>{it.get('vbcst', '0.00')}</vBCST><vICMSST>{it['vicmsst']}</vICMSST>"
    return f"<ICMS><{tag}>{miolo}</{tag}></ICMS>"


def nfe_xml(chave, emit_cnpj, emit_uf, dest_cnpj, dest_uf, itens, emit_crt="3", tp_nf="1",
            dh="2026-09-10T10:00:00-03:00", c_stat="100", numero="1"):
    dets = []
    for n, it in enumerate(itens, start=1):
        extras = "".join(f"<{t}>{it[k]}</{t}>" for k, t in (("vfrete", "vFrete"), ("vseg", "vSeg"),
                                                             ("voutro", "vOutro"), ("vdesc", "vDesc")) if k in it)
        ipi = f"<IPI><cEnq>999</cEnq><IPITrib><CST>50</CST><vIPI>{it['vipi']}</vIPI></IPITrib></IPI>" if "vipi" in it else ""
        dets.append(
            f'<det nItem="{n}"><prod><cProd>P{n}</cProd><xProd>Produto {n}</xProd><NCM>{it.get("ncm", "39241000")}</NCM>'
            f'<CFOP>{it.get("cfop", "6102")}</CFOP><vProd>{it["vprod"]}</vProd>{extras}</prod>'
            f'<imposto>{_icms(it)}{ipi}</imposto></det>')
    v_nf = sum(float(it["vprod"]) for it in itens)
    return (
        f'<?xml version="1.0" encoding="UTF-8"?><nfeProc xmlns="{NS}" versao="4.00"><NFe><infNFe Id="NFe{chave}" versao="4.00">'
        f'<ide><mod>55</mod><serie>1</serie><nNF>{numero}</nNF><dhEmi>{dh}</dhEmi><tpNF>{tp_nf}</tpNF>'
        f'<idDest>2</idDest><finNFe>1</finNFe></ide>'
        f'<emit><CNPJ>{emit_cnpj}</CNPJ><xNome>Fornecedor {emit_uf}</xNome><enderEmit><UF>{emit_uf}</UF></enderEmit><CRT>{emit_crt}</CRT></emit>'
        f'<dest><CNPJ>{dest_cnpj}</CNPJ><xNome>Cliente</xNome><enderDest><UF>{dest_uf}</UF></enderDest></dest>'
        + "".join(dets) +
        f'<total><ICMSTot><vProd>{v_nf:.2f}</vProd><vNF>{v_nf:.2f}</vNF><vICMS>0.00</vICMS><vST>0.00</vST><vIPI>0.00</vIPI></ICMSTot></total>'
        f'</infNFe></NFe><protNFe><infProt><cStat>{c_stat}</cStat></infProt></protNFe></nfeProc>')


def evento_cancelamento(chave):
    return (f'<?xml version="1.0" encoding="UTF-8"?><procEventoNFe xmlns="{NS}"><evento><infEvento>'
            f'<chNFe>{chave}</chNFe><tpEvento>110111</tpEvento></infEvento></evento></procEventoNFe>')


def gravar(pasta: Path, nome: str, conteudo: str) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / nome
    arq.write_text(conteudo, encoding="utf-8")
    return arq


NS_NFSE = "http://www.sped.fazenda.gov.br/nfse"
NS_ABRASF = "http://www.abrasf.org.br/nfse.xsd"


def nfse_nacional(numero, prestador, tomador, c_trib_nac, descricao, valor, tp_ret="1", op_simp="3",
                  competencia="2026-09-01", ret_irrf=None, municipio="9999999"):
    fed = f"<tribFed><vRetIRRF>{ret_irrf}</vRetIRRF></tribFed>" if ret_irrf else ""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?><NFSe xmlns="{NS_NFSE}" versao="1.00">'
        f'<infNFSe Id="NFS{numero:050d}"><nNFSe>{numero}</nNFSe><cLocIncid>{municipio}</cLocIncid>'
        f'<emit><CNPJ>{prestador}</CNPJ></emit><valores><vISSQN>0.00</vISSQN></valores>'
        f'<DPS versao="1.00"><infDPS Id="DPS1"><dhEmi>{competencia}T10:00:00-03:00</dhEmi><dCompet>{competencia}</dCompet>'
        f'<prest><CNPJ>{prestador}</CNPJ><regTrib><opSimpNac>{op_simp}</opSimpNac></regTrib></prest>'
        f'<toma><CNPJ>{tomador}</CNPJ></toma>'
        f'<serv><cServ><cTribNac>{c_trib_nac}</cTribNac><xDescServ>{descricao}</xDescServ><cNBS>115021000</cNBS></cServ></serv>'
        f'<valores><vServPrest><vServ>{valor}</vServ></vServPrest>'
        f'<trib><tribMun><tribISSQN>1</tribISSQN><tpRetISSQN>{tp_ret}</tpRetISSQN><pAliq>2.01</pAliq></tribMun>{fed}</trib>'
        f'</valores></infDPS></DPS></infNFSe></NFSe>')


def nfse_abrasf(numero, prestador, tomador, item, cnae, descricao, valor, iss_retido="2", ret_ir=None):
    ir = f"<ValorIr>{ret_ir}</ValorIr>" if ret_ir else ""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?><CompNfse xmlns="{NS_ABRASF}"><Nfse versao="2.02"><InfNfse>'
        f'<Numero>{numero}</Numero><CodigoVerificacao>AB{numero}</CodigoVerificacao><DataEmissao>2026-09-15T09:00:00</DataEmissao>'
        f'<ValoresNfse><ValorIss>0</ValorIss></ValoresNfse>'
        f'<PrestadorServico><IdentificacaoPrestador><CpfCnpj><Cnpj>{prestador}</Cnpj></CpfCnpj></IdentificacaoPrestador></PrestadorServico>'
        f'<DeclaracaoPrestacaoServico><InfDeclaracaoPrestacaoServico><Competencia>2026-09-01</Competencia>'
        f'<Servico><Valores><ValorServicos>{valor}</ValorServicos>{ir}<Aliquota>2.01</Aliquota></Valores>'
        f'<IssRetido>{iss_retido}</IssRetido><ItemListaServico>{item}</ItemListaServico><CodigoCnae>{cnae}</CodigoCnae>'
        f'<Discriminacao>{descricao}</Discriminacao><CodigoMunicipio>9999999</CodigoMunicipio></Servico>'
        f'<Prestador><CpfCnpj><Cnpj>{prestador}</Cnpj></CpfCnpj></Prestador>'
        f'<Tomador><IdentificacaoTomador><CpfCnpj><Cnpj>{tomador}</Cnpj></CpfCnpj></IdentificacaoTomador></Tomador>'
        f'<OptanteSimplesNacional>1</OptanteSimplesNacional>'
        f'</InfDeclaracaoPrestacaoServico></DeclaracaoPrestacaoServico></InfNfse></Nfse></CompNfse>')
