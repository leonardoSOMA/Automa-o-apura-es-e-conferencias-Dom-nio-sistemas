# -*- coding: utf-8 -*-
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
from nfe import ler_nota, resumo  # noqa: E402

from testes.fabrica import evento_cancelamento, gravar, nfe_xml  # noqa: E402

CLIENTE = "11111111000111"
CH1 = "35260900000000000100550010000000011000000011"
CH2 = "35260900000000000100550010000000021000000022"
CH3 = "29260911111111000111550010000000031000000033"


class TestNFe(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_le_campos_da_nota_e_do_item(self):
        arq = gravar(self.tmp, "a.xml", nfe_xml(CH1, "00000000000100", "SP", CLIENTE, "BA", [
            {"vprod": "1000.00", "ncm": "22030000", "cfop": "6102", "cst": "00", "picms": "12.00", "vicms": "120.00",
             "vipi": "50.00", "vfrete": "30.00"}]))
        n = ler_nota(arq)
        self.assertEqual(n.chave, CH1)
        self.assertEqual((n.emit_uf, n.dest_uf, n.dest_doc), ("SP", "BA", CLIENTE))
        self.assertEqual(n.status, "autorizada")
        it = n.itens[0]
        self.assertEqual((it.ncm, it.cfop, it.cst), ("22030000", "6102", "00"))
        self.assertEqual(it.p_icms, Decimal("12.00"))
        self.assertEqual(it.valor_operacao(), Decimal("1030.00"))
        self.assertEqual(it.valor_operacao(incluir_ipi=True), Decimal("1080.00"))

    def test_resumo_separa_entradas_saidas_e_canceladas(self):
        gravar(self.tmp, "ent1.xml", nfe_xml(CH1, "00000000000100", "SP", CLIENTE, "BA", [{"vprod": "100.00"}]))
        gravar(self.tmp, "ent2.xml", nfe_xml(CH2, "00000000000100", "SP", CLIENTE, "BA", [{"vprod": "50.00"}]))
        gravar(self.tmp, "sai1.xml", nfe_xml(CH3, CLIENTE, "BA", "22222222000122", "BA", [{"vprod": "300.00"}]))
        gravar(self.tmp, "sai1-copia.xml", nfe_xml(CH3, CLIENTE, "BA", "22222222000122", "BA", [{"vprod": "300.00"}]))
        gravar(self.tmp, "canc.xml", evento_cancelamento(CH2))
        r = resumo(self.tmp, CLIENTE, "2026-09")
        self.assertEqual(r["entradas"]["quantidade"], 1)
        self.assertEqual(r["entradas"]["valor_total"], "100.00")
        self.assertEqual(r["entradas"]["canceladas"], [CH2])
        self.assertEqual(r["saidas"]["quantidade"], 1)
        self.assertEqual(r["duplicadas"], [CH3])
        self.assertEqual(r["fora_da_competencia"], [])


if __name__ == "__main__":
    unittest.main()
