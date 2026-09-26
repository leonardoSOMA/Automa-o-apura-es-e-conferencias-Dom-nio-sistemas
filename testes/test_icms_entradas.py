# -*- coding: utf-8 -*-
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
from icms_entradas import calcular, carregar_config  # noqa: E402

from testes.fabrica import gravar, nfe_xml  # noqa: E402

CLIENTE = "11111111000111"
BASE_CFG = {
    "uf": "ZZ", "validado_por": "teste", "validado_em": "2026-09-26", "finalidade_padrao": "revenda",
    "aliquota_interna_padrao": 0.18, "aliquotas_internas_por_ncm": {}, "fcp": 0.0,
    "antecipacao_parcial": {"aplica": True, "base": "unica", "inclui_ipi": False, "reducao_simples": 0.0,
                            "credito_fornecedor_simples": "aliquota_interestadual"},
    "antecipacao_st": {"aplica": True, "usar_mva_ajustada": True, "credito_fornecedor_simples": "aliquota_interestadual",
                       "mva_por_ncm": {"2203": 0.40}},
    "difal_uso_consumo_ativo": {"aplica": True, "base": "dupla", "inclui_ipi": True,
                                "credito_fornecedor_simples": "aliquota_interestadual"},
}


def chave(n):
    return f"35260900000000000100550010000000{n:02d}1000000{n:03d}"[:44].ljust(44, "0")


class TestICMSEntradas(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.xml = self.tmp / "xml"
        self.cfgdir = self.tmp / "cfg"

    def cfg(self, **alteracoes):
        cfg = json.loads(json.dumps(BASE_CFG))
        for caminho, valor in alteracoes.items():
            alvo = cfg
            partes = caminho.split("__")
            for p in partes[:-1]:
                alvo = alvo[p]
            alvo[partes[-1]] = valor
        self.cfgdir.mkdir(exist_ok=True)
        (self.cfgdir / "ZZ.json").write_text(json.dumps(cfg), encoding="utf-8")
        return carregar_config("ZZ", self.cfgdir)

    def nota(self, n, itens, uf="SP", crt="3"):
        gravar(self.xml, f"n{n}.xml", nfe_xml(chave(n), "00000000000100", uf, CLIENTE, "ZZ", itens, emit_crt=crt))

    def unico(self, cfg, finalidades=None):
        r = calcular(self.xml, "ZZ", CLIENTE, cfg, finalidades)
        self.assertEqual(len(r["itens"]), 1)
        return r["itens"][0]

    def test_antecipacao_parcial_base_unica(self):
        self.nota(1, [{"vprod": "1000.00", "cst": "00", "picms": "12.00", "vicms": "120.00"}])
        it = self.unico(self.cfg())
        self.assertEqual(it["tipo"], "antecipacao_parcial")
        self.assertEqual(it["valor"], Decimal("60.00"))  # 1000 x 18% - 120

    def test_antecipacao_parcial_importado_4_por_cento_sem_destaque(self):
        self.nota(2, [{"vprod": "1000.00", "csosn": "102", "orig": "1"}], crt="1")
        it = self.unico(self.cfg())
        self.assertEqual(it["aliq_interestadual"], Decimal("0.04"))
        self.assertEqual(it["valor"], Decimal("140.00"))  # 180 - 40

    def test_antecipacao_parcial_com_reducao_simples(self):
        self.nota(3, [{"vprod": "1000.00", "cst": "00", "picms": "12.00", "vicms": "120.00"}])
        it = self.unico(self.cfg(antecipacao_parcial__reducao_simples=0.2))
        self.assertEqual(it["valor"], Decimal("48.00"))  # 60 x 80%

    def test_rota_sudeste_para_nordeste_infere_7_por_cento(self):
        self.nota(4, [{"vprod": "1000.00", "csosn": "102"}], uf="MG", crt="1")
        it = self.unico(self.cfg())
        self.assertEqual(it["aliq_interestadual"], Decimal("0.07"))
        self.assertEqual(it["valor"], Decimal("110.00"))  # 180 - 70

    def test_difal_base_dupla(self):
        self.nota(5, [{"vprod": "1000.00", "cst": "00", "picms": "12.00", "vicms": "120.00"}])
        it = self.unico(self.cfg(), [{"chave": chave(5), "item": "", "cprod": "", "finalidade": "uso_consumo"}])
        self.assertEqual(it["tipo"], "difal")
        self.assertEqual(it["base"], Decimal("1073.17"))  # (1000 - 120) / 0,82
        self.assertEqual(it["valor"], Decimal("73.17"))

    def test_difal_base_unica(self):
        self.nota(6, [{"vprod": "1000.00", "cst": "00", "picms": "12.00", "vicms": "120.00"}])
        it = self.unico(self.cfg(difal_uso_consumo_ativo__base="unica"),
                        [{"chave": chave(6), "item": "1", "cprod": "", "finalidade": "ativo"}])
        self.assertEqual(it["valor"], Decimal("60.00"))

    def test_antecipacao_st_com_mva_ajustada(self):
        self.nota(7, [{"vprod": "1000.00", "ncm": "22030000", "cst": "00", "picms": "12.00", "vicms": "120.00"}])
        it = self.unico(self.cfg())
        self.assertEqual(it["tipo"], "antecipacao_st")
        self.assertEqual(it["base"], Decimal("1502.44"))  # 1000 x (1,4 x 0,88 / 0,82)
        self.assertEqual(it["valor"], Decimal("150.44"))

    def test_st_retida_pelo_fornecedor_nao_gera_valor(self):
        self.nota(8, [{"vprod": "1000.00", "ncm": "22030000", "cst": "10", "picms": "12.00", "vicms": "120.00",
                       "vicmsst": "150.44"}])
        it = self.unico(self.cfg())
        self.assertEqual(it["tipo"], "st_retida_pelo_fornecedor")
        self.assertEqual(it["valor"], Decimal("0"))

    def test_compra_interna_fica_fora(self):
        self.nota(9, [{"vprod": "1000.00", "cst": "00", "picms": "18.00", "vicms": "180.00"}], uf="ZZ")
        r = calcular(self.xml, "ZZ", CLIENTE, self.cfg())
        self.assertEqual(r["itens"], [])

    def test_avisa_finalidade_presumida_e_config_nao_validada(self):
        self.nota(10, [{"vprod": "100.00", "cst": "00", "picms": "12.00", "vicms": "12.00"}])
        r = calcular(self.xml, "ZZ", CLIENTE, self.cfg(validado_em=""))
        self.assertTrue(any("NÃO validada" in a for a in r["avisos"]))
        self.assertTrue(any("presumida" in a for a in r["avisos"]))


if __name__ == "__main__":
    unittest.main()
