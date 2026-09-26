# -*- coding: utf-8 -*-
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
import nfse  # noqa: E402
from analise_iss import analisar, parecer  # noqa: E402

from testes.fabrica import gravar, nfse_nacional  # noqa: E402

EMPRESA, TOMADOR, CIDADE = "12345678000199", "98765432000155", "1111111"


class TestAnaliseISS(unittest.TestCase):
    def cenario(self, notas, receitas, outro_municipio="0"):
        tmp = Path(tempfile.mkdtemp())
        for i, xml in enumerate(notas):
            gravar(tmp / "xml", f"n{i}.xml", xml)
        (tmp / "nfse.json").write_text(json.dumps(nfse.resumo(tmp / "xml", EMPRESA), default=nfse._json), encoding="utf-8")
        dados = {"empresa": {"codigo": "205", "razao_social": "Teste"}, "competencia": "2026-09",
                 "nfse_json": "nfse.json", "municipio_estabelecimento": CIDADE,
                 "apuracao": {"rbt12": "360000", "anexo": "III", "receitas_declaradas": receitas,
                              "receita_iss_outro_municipio": outro_municipio}}
        return {a["analise"]: a for a in analisar(dados, tmp)}, dados

    def test_iss_retido_nao_segregado_e_pago_duas_vezes(self):
        r, dados = self.cenario(
            [nfse_nacional(1, EMPRESA, TOMADOR, "010101", "Serviço", "10000.00", tp_ret="2", municipio=CIDADE),
             nfse_nacional(2, EMPRESA, TOMADOR, "010101", "Serviço", "20000.00", municipio=CIDADE)],
            [{"tipo": "normal", "valor": "30000"}])
        a = r["AT-02"]
        self.assertEqual(a["conclusao"], "Oportunidade")
        self.assertEqual(a["impacto_mes"], Decimal("275.20"))  # 10.000 x 8,6% x 32% (parcela do ISS na 2ª faixa)
        self.assertIn("pago a maior", parecer(a, dados))

    def test_iss_retido_segregado_corretamente(self):
        r, _ = self.cenario(
            [nfse_nacional(1, EMPRESA, TOMADOR, "010101", "Serviço", "10000.00", tp_ret="2", municipio=CIDADE)],
            [{"tipo": "iss_retido", "valor": "10000"}])
        self.assertEqual(r["AT-02"]["conclusao"], "Situação justificada")

    def test_iss_de_outro_municipio_nao_declarado(self):
        r, _ = self.cenario(
            [nfse_nacional(1, EMPRESA, TOMADOR, "070201", "Obra", "8000.00", municipio="2222222")],
            [{"tipo": "normal", "valor": "8000"}])
        self.assertEqual(r["AT-03"]["conclusao"], "Indício, falta informação")

    def test_outro_municipio_com_retencao_nao_entra_na_at03(self):
        r, _ = self.cenario(
            [nfse_nacional(1, EMPRESA, TOMADOR, "070201", "Obra", "8000.00", tp_ret="2", municipio="2222222")],
            [{"tipo": "iss_retido", "valor": "8000"}])
        self.assertEqual(r["AT-03"]["conclusao"], "Situação justificada")
        self.assertEqual(r["AT-02"]["conclusao"], "Situação justificada")

    def test_retencao_federal_em_nota_de_optante(self):
        r, _ = self.cenario(
            [nfse_nacional(1, EMPRESA, TOMADOR, "170101", "Consultoria", "10000.00", municipio=CIDADE, ret_irrf="150.00")],
            [{"tipo": "normal", "valor": "10000"}])
        self.assertEqual(r["AT-05"]["conclusao"], "Oportunidade")
        self.assertEqual(r["AT-05"]["impacto_mes"], Decimal("150.00"))


if __name__ == "__main__":
    unittest.main()
