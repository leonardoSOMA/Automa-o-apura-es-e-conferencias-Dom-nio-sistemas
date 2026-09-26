# -*- coding: utf-8 -*-
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
import nfse  # noqa: E402
import varredura  # noqa: E402

from testes.fabrica import gravar, nfse_abrasf  # noqa: E402

TABELA = {"6201501": {"anexo": "V", "fator_r": "S"}, "8599604": {"anexo": "III", "fator_r": "N"}}
TOMADOR = "98765432000155"


def empresa(raiz: Path, codigo: str, cnpj: str, cnaes, cnae_nota: str, folha12: str, anexo: str, acumuladores=None):
    pasta = raiz / codigo
    gravar(pasta / "xml", "n1.xml", nfse_abrasf(1, cnpj, TOMADOR, "01.01", cnae_nota, "Serviço", "30000.00"))
    (pasta / "nfse.json").write_text(json.dumps(nfse.resumo(pasta / "xml", cnpj), default=nfse._json), encoding="utf-8")
    dados = {"empresa": {"codigo": codigo, "razao_social": f"Empresa {codigo}"}, "competencia": "2026-09",
             "cnaes": [{"codigo": c} for c in cnaes], "nfse_json": "nfse.json", "rbt12": "360000",
             "folha12": folha12, "anexo_aplicado": anexo, "acumuladores": acumuladores or []}
    (pasta / "fator_r.json").write_text(json.dumps(dados), encoding="utf-8")


class TestVarredura(unittest.TestCase):
    def test_ordena_por_gravidade_e_impacto_e_grava_saida(self):
        raiz = Path(tempfile.mkdtemp())
        empresa(raiz, "301", "11111111000111", ["6201501", "8599604"], "8599604", "43200", "III")  # justificada
        empresa(raiz, "302", "22222222000122", ["6201501"], "6201501", "43200", "III")             # erro provável
        empresa(raiz, "303", "33333333000133", ["6201501"], "6201501", "111600", "V")              # oportunidade
        empresa(raiz, "304", "44444444000144", ["6201501"], "6201501", "111600", "III",
                [{"codigo": "50", "anexo": "III", "fator_r": "N"}])                                      # risco latente
        achados = varredura.varrer(raiz, TABELA)
        self.assertEqual([a["empresa"]["codigo"] for a in achados], ["302", "303", "304", "301"])
        self.assertEqual([a["conclusao_preliminar"] for a in achados],
                         ["Erro provável", "Oportunidade", "Risco latente", "Situação justificada"])
        md = varredura.tabela_md(achados)
        self.assertIn("BLOQUEIA", md)
        self.assertIn("R$ 2.445,00 pago a menor", md)

    def test_lista_cnaes_fora_da_tabela(self):
        raiz = Path(tempfile.mkdtemp())
        empresa(raiz, "305", "55555555000155", ["6201501", "4751201"], "6201501", "43200", "III")
        empresa(raiz, "306", "66666666000166", ["4751201"], "4751201", "43200", "III")
        achados = varredura.varrer(raiz, TABELA)
        self.assertEqual(varredura.cnaes_a_classificar(achados), {"4751-2/01": ["305", "306"]})


if __name__ == "__main__":
    unittest.main()
