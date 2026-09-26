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
from cnpj import TABELA_CNAE, carregar_tabela  # noqa: E402

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

    def dados(self, cnaes, notas, folha12, anexo, rbt12="360000", acumuladores=None, **extra):
        d = {"empresa": {"codigo": "205", "razao_social": "Teste", "inicio_atividade": "2019-01-01"},
             "competencia": "2026-09", "cnaes": [{"codigo": c} for c in cnaes],
             "nfse_json": resumo_nfse(self.tmp, notas), "rbt12": rbt12, "folha12": folha12,
             "anexo_aplicado": anexo,
             "acumuladores": acumuladores or [{"codigo": "50", "anexo": "III", "fator_r": "N"}]}
        d.update(extra)
        return d

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

    def test_folha_zero_confirmada_usa_fator_001_e_vai_para_o_anexo_v(self):
        d = self.dados(["6201501"], [nfse_abrasf(8, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "30000.00")],
                       "0", "III", folha_confirmada=True)
        r = analisar(d, TABELA)
        self.assertEqual(r["fator_r"], Decimal("0.01"))
        self.assertIn("art. 26", r["regra_fator_r"])
        self.assertEqual(r["anexo_devido"], "V")
        self.assertEqual(r["conclusao_preliminar"], "Erro provável")
        self.assertEqual(r["impacto"]["diferenca_mes"], Decimal("2445.00"))
        self.assertTrue(any("causa provável" in c for c in r["configuracao"]))

    def test_folha_zero_sem_confirmacao_fica_em_indicio(self):
        d = self.dados(["6201501"], [nfse_abrasf(9, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "30000.00")],
                       "0", "III")
        r = analisar(d, TABELA)
        self.assertEqual(r["conclusao_preliminar"], "Indício, falta informação")
        self.assertEqual(r["hipoteses"]["H5"]["resultado"], "reforça")
        self.assertIn("0,01", r["hipoteses"]["H5"]["evidencia"])
        self.assertFalse(r["bloqueia_transmissao"])

    def test_receita_zero_com_folha_usa_fator_028(self):
        d = self.dados(["6201501"], [nfse_abrasf(10, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "30000.00")],
                       "5000", "III", rbt12="0", acumuladores=[{"codigo": "50", "anexo": "V", "fator_r": "S"}])
        r = analisar(d, TABELA)
        self.assertEqual(r["fator_r"], Decimal("0.28"))
        self.assertEqual(r["anexo_devido"], "III")
        self.assertEqual(r["conclusao_preliminar"], "Situação justificada")

    def test_risco_latente_acumulador_iii_fixo_com_fator_r_acima_de_28(self):
        d = self.dados(["6201501"], [nfse_abrasf(11, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "30000.00")],
                       "111600", "III")  # 31%: o III está certo hoje, mas o acumulador não troca de anexo
        r = analisar(d, TABELA)
        self.assertEqual(r["conclusao_preliminar"], "Risco latente")
        self.assertIsNone(r["impacto"])
        self.assertFalse(r["bloqueia_transmissao"])
        self.assertEqual(r["folha_para_28"], Decimal("100800.00"))
        self.assertIn("R$ 100.800,00", r["configuracao"][0])
        self.assertIn("## Configuração da Domínio", parecer_rascunho(r))

    def test_troca_automatica_marcada_com_fator_r_acima_de_28_e_justificada(self):
        d = self.dados(["6201501"], [nfse_abrasf(12, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "30000.00")],
                       "111600", "III", acumuladores=[{"codigo": "50", "anexo": "V", "fator_r": "S"}])
        r = analisar(d, TABELA)
        self.assertEqual(r["conclusao_preliminar"], "Situação justificada")
        self.assertEqual(r["configuracao"], [])

    def test_atividade_nao_sujeita_apurada_no_anexo_v_e_oportunidade(self):
        d = self.dados(["8599604"], [nfse_abrasf(13, EMPRESA, TOMADOR, "08.02", "8599604", "Treinamento gerencial", "30000.00")],
                       "43200", "V", acumuladores=[{"codigo": "51", "anexo": "V", "fator_r": "S"}])
        r = analisar(d, TABELA)
        self.assertEqual(r["anexo_devido"], "III")
        self.assertEqual(r["conclusao_preliminar"], "Oportunidade")
        self.assertEqual(r["impacto"]["diferenca_mes"], Decimal("-2445.00"))
        self.assertTrue(any("não tem atividade sujeita" in c for c in r["configuracao"]))

    def test_atividade_nao_sujeita_com_troca_automatica_e_risco_latente(self):
        d = self.dados(["8599604"], [nfse_abrasf(14, EMPRESA, TOMADOR, "08.02", "8599604", "Treinamento gerencial", "30000.00")],
                       "111600", "III", acumuladores=[{"codigo": "51", "anexo": "V", "fator_r": "S"}])
        r = analisar(d, TABELA)
        self.assertEqual(r["conclusao_preliminar"], "Risco latente")
        self.assertIsNone(r["impacto"])

    def test_receita_mista_no_mes_fica_em_indicio(self):
        d = self.dados(["6201501", "8599604"],
                       [nfse_abrasf(15, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "20000.00"),
                        nfse_abrasf(16, EMPRESA, TOMADOR, "08.02", "8599604", "Treinamento", "10000.00")],
                       "43200", "III")
        r = analisar(d, TABELA)
        self.assertIsNone(r["faturamento_sujeito"])
        self.assertEqual(r["hipoteses"]["H1"]["resultado"], "inconclusivo")
        self.assertIn("separar a receita", r["hipoteses"]["H1"]["evidencia"])
        self.assertEqual(r["conclusao_preliminar"], "Indício, falta informação")

    def test_cnae_que_depende_do_servico_fica_em_indicio(self):
        tabela = dict(TABELA, **{"7410202": {"anexo": "IV ou V", "fator_r": "D",
                                             "observacao": "Decoração de interiores é Anexo IV."}})
        d = self.dados(["7410202"], [nfse_nacional(17, EMPRESA, TOMADOR, "170601", "Projeto de interiores", "30000.00")],
                       "43200", "III")
        r = analisar(d, tabela)
        self.assertEqual(r["hipoteses"]["H1"]["resultado"], "inconclusivo")
        self.assertEqual(r["conclusao_preliminar"], "Indício, falta informação")
        self.assertTrue(any("depende do serviço" in a for a in r["alertas"]))

    def test_competencia_de_2027_gera_alerta(self):
        d = self.dados(["6201501"], [nfse_abrasf(18, EMPRESA, TOMADOR, "01.01", "6201501", "Desenvolvimento", "30000.00")],
                       "43200", "III", competencia="2027-02")
        r = analisar(d, TABELA)
        self.assertTrue(any("2027" in a for a in r["alertas"]))


class TestTabelaCnae(unittest.TestCase):
    """Confere a forma da tabela do escritório (config/tabelas/cnae_anexo.csv), não a classificação legal."""

    def test_tabela_do_escritorio(self):
        linhas = TABELA_CNAE.read_text(encoding="utf-8-sig").strip().splitlines()[1:]
        tabela = carregar_tabela(TABELA_CNAE)
        self.assertEqual(len(tabela), len(linhas), "código de CNAE repetido na tabela")
        for cod, ln in tabela.items():
            self.assertRegex(cod, r"^\d{7}$")
            self.assertIn(ln["fator_r"], {"S", "N", "D"}, cod)
            self.assertIn(ln["confianca"], {"alta", "média"}, cod)
            self.assertTrue(ln["fonte"], cod)
            if ln["fator_r"] == "S":
                self.assertEqual(ln["anexo"], "V", cod)
            if ln["fator_r"] == "N":
                self.assertIn(ln["anexo"], {"III", "IV"}, cod)
        self.assertEqual((tabela["6920601"]["anexo"], tabela["6920601"]["fator_r"]), ("III", "N"))
        self.assertEqual(tabela["6920602"]["fator_r"], "S")
        self.assertEqual(tabela["6911701"]["anexo"], "IV")
        self.assertEqual(tabela["6622300"]["fator_r"], "D")



if __name__ == "__main__":
    unittest.main()
