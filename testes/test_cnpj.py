# -*- coding: utf-8 -*-
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
import cnpj  # noqa: E402

RESPOSTA = {
    "cnpj": "12345678000199", "razao_social": "SOFT EXEMPLO LTDA", "descricao_situacao_cadastral": "ATIVA",
    "data_inicio_atividade": "2019-03-01", "uf": "XX", "municipio": "CIDADE EXEMPLO",
    "cnae_fiscal": 6201501, "cnae_fiscal_descricao": "Desenvolvimento de programas de computador sob encomenda",
    "cnaes_secundarios": [{"codigo": 8599604, "descricao": "Treinamento em desenvolvimento profissional e gerencial"},
                          {"codigo": 0, "descricao": ""}],
    "opcao_pelo_simples": True, "data_opcao_pelo_simples": "2019-03-01", "opcao_pelo_mei": False,
}


class ApiFalsa(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/12345678000199"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(RESPOSTA).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass


class TestCNPJ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(("127.0.0.1", 0), ApiFalsa)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        os.environ["CNPJ_API"] = f"http://127.0.0.1:{cls.srv.server_port}/api/cnpj/v1"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_formatar_cnae(self):
        self.assertEqual(cnpj.formatar_cnae(6201501), "6201-5/01")
        self.assertEqual(cnpj.formatar_cnae("111301"), "0111-3/01")

    def test_consulta_e_classificacao(self):
        tabela = {"6201501": {"anexo": "V", "fator_r": "S", "observacao": "teste"}}
        r = cnpj.resumo(cnpj.consultar("12.345.678/0001-99"), tabela)
        self.assertTrue(r["optante_simples"])
        self.assertEqual([c["formatado"] for c in r["cnaes"]], ["6201-5/01", "8599-6/04"])  # ignora código 0
        self.assertEqual((r["cnaes"][0]["anexo"], r["cnaes"][0]["fator_r"]), ("V", "S"))
        self.assertEqual(r["cnaes"][1]["anexo"], "não classificado")

    def test_cnpj_inexistente_da_erro_claro(self):
        with self.assertRaises(RuntimeError):
            cnpj.consultar("00000000000000")


if __name__ == "__main__":
    unittest.main()
