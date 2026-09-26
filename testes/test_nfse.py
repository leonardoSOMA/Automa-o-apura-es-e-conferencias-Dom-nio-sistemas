# -*- coding: utf-8 -*-
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
from nfse import ler_nfse, resumo  # noqa: E402

from testes.fabrica import evento_nfse_cancelamento, gravar, nfse_abrasf, nfse_nacional  # noqa: E402
from nfse import subitem_lc116  # noqa: E402

EMPRESA = "12345678000199"
CLIENTE = "98765432000155"


class TestNFSe(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_le_nfse_nacional(self):
        arq = gravar(self.tmp, "n1.xml", nfse_nacional(1, EMPRESA, CLIENTE, "010101", "Desenvolvimento de sistema",
                                                       "5000.00", tp_ret="2"))
        n = ler_nfse(arq)
        self.assertEqual(n.padrao, "nacional")
        self.assertEqual((n.numero, n.prestador, n.tomador), ("1", EMPRESA, CLIENTE))
        self.assertEqual(n.codigo_servico, "010101")
        self.assertEqual(n.valor_servico, Decimal("5000.00"))
        self.assertTrue(n.iss_retido)
        self.assertEqual(n.competencia, "2026-09")
        self.assertEqual(n.ausentes, [])

    def test_le_nfse_abrasf_com_cnae(self):
        arq = gravar(self.tmp, "a1.xml", nfse_abrasf(7, EMPRESA, CLIENTE, "17.01", "7020400", "Consultoria em gestão",
                                                     "3000.00", iss_retido="1"))
        n = ler_nfse(arq)
        self.assertEqual(n.padrao, "abrasf")
        self.assertEqual((n.codigo_servico, n.cnae), ("17.01", "7020400"))
        self.assertTrue(n.iss_retido)
        self.assertEqual(n.valor_servico, Decimal("3000.00"))

    def test_resumo_agrupa_por_servico_e_aponta_retencao_federal(self):
        gravar(self.tmp, "n1.xml", nfse_nacional(1, EMPRESA, CLIENTE, "010101", "Desenvolvimento", "5000.00"))
        gravar(self.tmp, "n2.xml", nfse_nacional(2, EMPRESA, CLIENTE, "010101", "Manutenção de sistema", "2000.00",
                                                 tp_ret="2", ret_irrf="30.00"))
        gravar(self.tmp, "a1.xml", nfse_abrasf(9, CLIENTE, EMPRESA, "17.01", "7020400", "Consultoria", "800.00"))
        r = resumo(self.tmp, EMPRESA, "2026-09")
        self.assertEqual(r["prestadas"]["quantidade"], 2)
        self.assertEqual(r["prestadas"]["valor_total"], Decimal("7000.00"))
        self.assertEqual(r["prestadas"]["valor_com_iss_retido"], Decimal("2000.00"))
        self.assertEqual(r["prestadas"]["por_servico"]["01.01"]["notas"], 2)
        self.assertEqual(r["tomadas"]["quantidade"], 1)
        self.assertTrue(any("AT-05" in a for a in r["avisos"]))


class TestCorrecoesNFSe(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_subitem_lc116(self):
        self.assertEqual(subitem_lc116("010101"), "01.01")
        self.assertEqual(subitem_lc116("1.01"), "01.01")
        self.assertEqual(subitem_lc116("17.01"), "17.01")
        self.assertEqual(subitem_lc116("0702"), "07.02")

    def test_abrasf_cnae_com_zero_a_esquerda_e_aliquota_em_fracao(self):
        xml = nfse_abrasf(3, EMPRESA, CLIENTE, "1.01", "111301", "Serviço", "100.00").replace(
            "<Aliquota>2.01</Aliquota>", "<Aliquota>0.05</Aliquota>")
        n = ler_nfse(gravar(self.tmp, "a.xml", xml))
        self.assertEqual(n.cnae, "0111301")
        self.assertEqual(n.aliquota_iss, Decimal("5.00"))
        self.assertEqual(n.subitem_lc116, "01.01")

    def test_nacional_cancelada_por_evento_sai_do_total(self):
        gravar(self.tmp, "n1.xml", nfse_nacional(1, EMPRESA, CLIENTE, "010101", "Serviço", "1000.00"))
        gravar(self.tmp, "n2.xml", nfse_nacional(2, EMPRESA, CLIENTE, "010101", "Serviço", "500.00"))
        gravar(self.tmp, "ev.xml", evento_nfse_cancelamento(f"{2:050d}"))
        r = resumo(self.tmp, EMPRESA)
        self.assertEqual(r["prestadas"]["quantidade"], 1)
        self.assertEqual(r["prestadas"]["valor_total"], Decimal("1000.00"))
        self.assertEqual(r["canceladas"], ["2"])

    def test_abrasf_cancelada_na_propria_nota(self):
        xml = nfse_abrasf(4, EMPRESA, CLIENTE, "17.01", "7020400", "Consultoria", "900.00").replace(
            "</Nfse>", "</Nfse><NfseCancelamento><Confirmacao><DataHora>2026-09-20T10:00:00</DataHora></Confirmacao></NfseCancelamento>")
        gravar(self.tmp, "a.xml", xml)
        r = resumo(self.tmp, EMPRESA)
        self.assertEqual(r["prestadas"]["quantidade"], 0)
        self.assertEqual(r["canceladas"], ["4"])


if __name__ == "__main__":
    unittest.main()
