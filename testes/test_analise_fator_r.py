# -*- coding: utf-8 -*-
"""Cenários da AT-01. A tabela de CNAE aqui é um fixture de teste, não a classificação legal."""
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
import nfse  # noqa: E402
from analise_fator_r import analisar, parecer_rascunho  # noqa: E402

from testes.fabrica import gravar, nfse_abrasf, nfse_nacional  # noqa: E402

TABELA = {"6201501": {"anexo": "V", "fator_r": "S"}, "8599604": {"anexo": "III", "fator_r": "N"}}
EMPRESA = "12345678000199"
TOMADOR = "98765432000155"


def resumo_nfse(tmp: Path, notas) -> str:
    pasta = tmp / "xml"
    for i, xml in enumerate(notas):
        gravar(pasta, f"n{i}.xml", xml)
    arq = tmp / "nfse.json"
    arq.write_text(json.dumps(nfse.resumo(pasta, EMPRESA), default=nfse._json), encoding="utf-8")
    return str(arq)


class TestFatorR(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def dados(self, cnaes, notas, folha12, anexo, rbt12="360000"):
        return {"empresa": {"codigo": "205", "razao_social": "Teste", "inicio_atividade": "2019-01-01"},
                "competencia": "2026-09", "cnaes": [{"codigo": c} for c in cnaes],
                "nfse_json": resumo_nfse(self.tmp, notas), "rbt12": rbt12, "folha12": folha12,
                "anexo_aplicado": anexo, "acumuladores": [{"codigo": "50", "anexo": "III", "fator_r": "N"}]}

    def test_erro_provavel_atividade_sujeita_no_anexo_iii(self):
        d = self.dados(["6201501"], [nfse_abrasf(1, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento de sistema", "30000.00")],
                       "43200", "III")
        r = analisar(d, TABELA)
        self.assertEqual(r["hipoteses"]["H1"]["resultado"], "reforça")
        self.assertEqual(r["conclusao_preliminar"], "Erro provável")
        self.assertEqual(r["impacto"]["diferenca_mes"], Decimal("2445.00"))  # V 5.025,00 - III 2.580,00
        self.assertTrue(r["bloqueia_transmissao"])
        self.assertIn("Erro provável", parecer_rascunho(r))

    def test_situacao_justificada_quando_fatura_atividade_nao_sujeita(self):
        d = self.dados(["6201501", "8599604"],
                       [nfse_abrasf(2, EMPRESA, TOMADOR, "08.02", "8599604", "Treinamento gerencial", "30000.00")],
                       "43200", "III")
        r = analisar(d, TABELA)
        self.assertEqual(r["hipoteses"]["H2"]["resultado"], "reforça")
        self.assertEqual(r["conclusao_preliminar"], "Situação justificada")
        self.assertIsNone(r["impacto"])

    def test_nota_sem_cnae_e_empresa_so_com_atividade_sujeita(self):
        d = self.dados(["6201501"], [nfse_nacional(3, EMPRESA, TOMADOR, "010101", "Desenvolvimento", "30000.00")],
                       "43200", "III")
        r = analisar(d, TABELA)
        self.assertEqual(r["hipoteses"]["H1"]["resultado"], "reforça")
        self.assertEqual(r["conclusao_preliminar"], "Erro provável")

    def test_nota_sem_cnae_e_empresa_mista_fica_em_indicio(self):
        d = self.dados(["6201501", "8599604"], [nfse_nacional(4, EMPRESA, TOMADOR, "010101", "Serviço", "30000.00")],
                       "43200", "III")
        r = analisar(d, TABELA)
        self.assertEqual(r["hipoteses"]["H1"]["resultado"], "inconclusivo")
        self.assertEqual(r["conclusao_preliminar"], "Indício, falta informação")

    def test_oportunidade_fator_r_acima_de_28_no_anexo_v(self):
        d = self.dados(["6201501"], [nfse_abrasf(5, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "30000.00")],
                       "111600", "V")  # 31%
        r = analisar(d, TABELA)
        self.assertEqual(r["conclusao_preliminar"], "Oportunidade")
        self.assertEqual(r["impacto"]["sentido"], "pago a maior")

    def test_sem_folha_fica_em_indicio(self):
        d = self.dados(["6201501"], [nfse_abrasf(6, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "30000.00")],
                       None, "III")
        r = analisar(d, TABELA)
        self.assertIsNone(r["fator_r"])
        self.assertEqual(r["conclusao_preliminar"], "Indício, falta informação")

    def test_planejamento_quando_fator_r_entre_20_e_28(self):
        d = self.dados(["6201501"], [nfse_abrasf(7, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "30000.00")],
                       "90000", "V")  # 25%
        r = analisar(d, TABELA)
        p = r["planejamento_fator_r"]
        self.assertEqual(p["folha_adicional_12_meses"], Decimal("10800.00"))
        self.assertEqual(p["economia_das_mes"], Decimal("2445.00"))
        self.assertEqual(r["conclusao_preliminar"], "Situação justificada")


if __name__ == "__main__":
    unittest.main()
