# -*- coding: utf-8 -*-
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
import das_simples as das  # noqa: E402

D = Decimal


class TestTabelas(unittest.TestCase):
    def test_reparticao_soma_100_em_todas_as_faixas(self):
        for anexo, (tributos, faixas) in das.TABELAS.items():
            for i, (_, _, rep) in enumerate(faixas, start=1):
                self.assertEqual(len(rep), len(tributos), f"Anexo {anexo} faixa {i}")
                self.assertEqual(sum(D(p) for p in rep), D("100"), f"Anexo {anexo} faixa {i}")
        for anexo, (_, rep) in das.REPARTICAO_EXCEDENTE_5A_FAIXA.items():
            self.assertEqual(sum(D(p) for p in rep.values()), D("100"), f"excedente Anexo {anexo}")

    def test_aliquota_efetiva_continua_nas_divisas_das_faixas_1_a_5(self):
        # as parcelas a deduzir existem para a alíquota efetiva não saltar na troca de faixa
        for anexo, (_, faixas) in das.TABELAS.items():
            for i in range(4):
                limite = das.LIMITES[i]
                nom_a, ded_a, _ = faixas[i]
                nom_b, ded_b, _ = faixas[i + 1]
                ef_a = (limite * D(nom_a) / 100 - D(ded_a)) / limite
                ef_b = (limite * D(nom_b) / 100 - D(ded_b)) / limite
                self.assertEqual(ef_a.quantize(D("0.000001")), ef_b.quantize(D("0.000001")),
                                 f"Anexo {anexo}, divisa {limite}")

    def test_faixas_nas_divisas(self):
        self.assertEqual(das.faixa(D("180000")), 1)
        self.assertEqual(das.faixa(D("180000.01")), 2)
        self.assertEqual(das.faixa(D("4800000")), 6)
        with self.assertRaises(ValueError):
            das.faixa(D("4800000.01"))


class TestCalculo(unittest.TestCase):
    def test_comercio_600_mil(self):
        r = das.calcular("600000", [("I", "normal", "50000")])
        ln = r["linhas"][0]
        self.assertEqual(ln["faixa"], 3)
        self.assertEqual(ln["aliquota_efetiva"].quantize(D("0.0001")), D("7.1900"))
        self.assertEqual(r["das_total"], D("3595.00"))
        self.assertLessEqual(abs(r["das_soma_por_tributo"] - r["das_total"]), D("0.05"))

    def test_segregacao_st_tira_o_icms(self):
        r = das.calcular("600000", [("I", "st", "50000")])
        self.assertNotIn("ICMS", r["linhas"][0]["por_tributo"])
        self.assertEqual(r["das_total"], D("2390.68"))  # 7,19% x (1 - 33,5%)

    def test_segregacao_monofasico_tira_pis_e_cofins(self):
        r = das.calcular("600000", [("I", "monofasico", "50000")])
        self.assertEqual(set(r["linhas"][0]["por_tributo"]), {"IRPJ", "CSLL", "CPP", "ICMS"})
        self.assertEqual(r["das_total"], D("3037.78"))  # 7,19% x 84,5%

    def test_anexo_iii_5a_faixa_com_teto_do_iss(self):
        r = das.calcular("3000000", [("III", "normal", "250000")])
        ln = r["linhas"][0]
        self.assertTrue(ln["teto_iss_aplicado"])
        self.assertEqual(ln["por_tributo"]["ISS"], D("12500.00"))  # 5% da receita
        self.assertEqual(r["das_total"], D("42030.00"))  # 16,812% da receita

    def test_iss_retido_sai_do_das(self):
        r = das.calcular("600000", [("III", "iss_retido", "10000")])
        self.assertNotIn("ISS", r["linhas"][0]["por_tributo"])

    def test_tipo_invalido_para_o_anexo(self):
        with self.assertRaises(ValueError):
            das.calcular("600000", [("III", "st", "1000")])

    def test_fator_r(self):
        self.assertEqual(das.anexo_pelo_fator_r(D("280000"), D("1000000"))[0], "III")
        self.assertEqual(das.anexo_pelo_fator_r(D("279999"), D("1000000"))[0], "V")

    def test_rbt12_proporcional(self):
        self.assertEqual(das.rbt12_proporcional([], D("10000")), D("120000"))
        self.assertEqual(das.rbt12_proporcional(["10000", "20000"], D("5000")), D("180000"))

    def test_faixa_6_avisa_que_icms_e_iss_ficam_de_fora(self):
        r = das.calcular("4000000", [("I", "normal", "100000")])
        self.assertNotIn("ICMS", r["linhas"][0]["por_tributo"])
        self.assertTrue(any("faixa 6" in a for a in r["alertas"]))

    def test_sem_piso_de_2_por_cento_para_o_iss(self):
        # início da 2ª faixa do Anexo III: 6,00% x 32% = 1,92% de ISS, sem arredondar para 2%
        p = das.percentuais("III", D("180000.01"))
        self.assertEqual(p["por_tributo"]["ISS"].quantize(D("0.01")), D("1.92"))

    def test_alerta_de_sublimite(self):
        r = das.calcular("3000000", [("I", "normal", "1000")])
        self.assertTrue(any("80%" in a for a in r["alertas"]))


if __name__ == "__main__":
    unittest.main()
