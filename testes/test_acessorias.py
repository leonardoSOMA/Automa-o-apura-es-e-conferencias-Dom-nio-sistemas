# -*- coding: utf-8 -*-
import io
import os
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ferramentas"))
import acessorias  # noqa: E402

RECEBIDOS = []


class ApiFalsa(BaseHTTPRequestHandler):
    def _registrar(self, corpo=b""):
        RECEBIDOS.append({"metodo": self.command, "caminho": self.path,
                          "auth": self.headers.get("Authorization"), "tipo": self.headers.get("Content-Type"),
                          "corpo": corpo})

    def do_POST(self):
        corpo = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self._registrar(corpo)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"recebido"}')

    def do_GET(self):
        self._registrar()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'[{"Obrigacao":"DAS","Status":"Entregue"}]')

    def log_message(self, *args):
        pass


class TestAcessorias(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(("127.0.0.1", 0), ApiFalsa)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        os.environ["ACESSORIAS_API"] = f"http://127.0.0.1:{cls.srv.server_port}"
        os.environ["ACESSORIAS_TOKEN"] = "token-de-teste"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        RECEBIDOS.clear()
        self.pdf = Path(tempfile.mkdtemp()) / "DAS_101_2026-09.pdf"
        self.pdf.write_bytes(b"%PDF-1.4 guia de teste")

    def test_sem_confirmacao_so_simula(self):
        saida = io.StringIO()
        with redirect_stdout(saida):
            self.assertEqual(acessorias.enviar([str(self.pdf)], confirmado=False), 0)
        self.assertEqual(RECEBIDOS, [])
        self.assertIn("SIMULAÇÃO", saida.getvalue())

    def test_envio_confirmado_vai_ao_econtinuo_com_o_arquivo(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(acessorias.enviar([str(self.pdf)], confirmado=True), 0)
        r = RECEBIDOS[0]
        self.assertEqual((r["metodo"], r["caminho"]), ("POST", "/econtinuo"))
        self.assertEqual(r["auth"], "Bearer token-de-teste")
        self.assertTrue(r["tipo"].startswith("multipart/form-data"))
        self.assertIn(b'name="arquivo"; filename="DAS_101_2026-09.pdf"', r["corpo"])
        self.assertIn(b"guia de teste", r["corpo"])

    def test_consulta_entregas(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(acessorias.entregas("00.000.000/0001-00", "2026-10-01", "2026-10-31"), 0)
        self.assertEqual(RECEBIDOS[0]["caminho"], "/deliveries/00000000000100?DtInitial=2026-10-01&DtFinal=2026-10-31")

    def test_arquivo_inexistente(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(acessorias.enviar(["nao-existe.pdf"], confirmado=True), 1)
        self.assertEqual(RECEBIDOS, [])


if __name__ == "__main__":
    unittest.main()
