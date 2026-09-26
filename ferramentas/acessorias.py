# -*- coding: utf-8 -*-
"""Cliente mínimo da API do Acessórias: envia guias ao robô e-Contínuo e consulta entregas.

Enviar uma guia ao e-Contínuo É enviar ao cliente. Sem --confirmo-envio o comando só mostra o que faria.

Uso:
    python ferramentas/acessorias.py enviar <pdf> [<pdf> ...] [--confirmo-envio]
    python ferramentas/acessorias.py entregas <CNPJ> --de AAAA-MM-DD --ate AAAA-MM-DD

Configuração (variáveis de ambiente do computador, nunca no repositório):
    ACESSORIAS_TOKEN   token gerado no Acessórias em Configurações > API Token
    ACESSORIAS_API     endereço da API (padrão https://api.acessorias.com)

Endpoints conforme a documentação pública da API (POST /econtinuo com o campo "arquivo"; GET /deliveries/{CNPJ}
com DtInitial e DtFinal). Validar com o token real na sessão do Acessórias antes do uso em produção.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from urllib import error, parse, request

PADRAO_API = "https://api.acessorias.com"


def _base() -> str:
    return os.environ.get("ACESSORIAS_API", PADRAO_API).rstrip("/")


def _token() -> str:
    token = os.environ.get("ACESSORIAS_TOKEN", "").strip()
    if not token:
        raise SystemExit("Defina a variável de ambiente ACESSORIAS_TOKEN (Acessórias > Configurações > API Token).")
    return token


def montar_multipart(campo: str, arquivo: Path) -> tuple[bytes, str]:
    fronteira = uuid.uuid4().hex
    tipo = mimetypes.guess_type(arquivo.name)[0] or "application/octet-stream"
    cabecalho = (f"--{fronteira}\r\nContent-Disposition: form-data; name=\"{campo}\"; filename=\"{arquivo.name}\"\r\n"
                 f"Content-Type: {tipo}\r\n\r\n").encode("utf-8")
    corpo = cabecalho + arquivo.read_bytes() + f"\r\n--{fronteira}--\r\n".encode("utf-8")
    return corpo, f"multipart/form-data; boundary={fronteira}"


def _chamar(req: request.Request) -> tuple[int, str]:
    try:
        with request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def enviar(arquivos: list, confirmado: bool) -> int:
    faltando = [a for a in arquivos if not Path(a).is_file()]
    if faltando:
        print("Arquivo não encontrado: " + ", ".join(faltando))
        return 1
    if not confirmado:
        print("SIMULAÇÃO (nada foi enviado). Com --confirmo-envio estes arquivos iriam ao e-Contínuo e ao cliente:")
        for a in arquivos:
            print(f"  {a}")
        return 0
    token, falhas = _token(), 0
    for a in arquivos:
        corpo, tipo = montar_multipart("arquivo", Path(a))
        req = request.Request(f"{_base()}/econtinuo", data=corpo, method="POST",
                              headers={"Authorization": f"Bearer {token}", "Content-Type": tipo})
        status, texto = _chamar(req)
        ok = 200 <= status < 300
        falhas += not ok
        print(f"{'OK' if ok else 'FALHOU'} · {a} · HTTP {status} · {texto[:300]}")
    return 1 if falhas else 0


def entregas(cnpj: str, de: str, ate: str) -> int:
    cnpj = "".join(c for c in cnpj if c.isdigit())
    consulta = parse.urlencode({"DtInitial": de, "DtFinal": ate})
    req = request.Request(f"{_base()}/deliveries/{cnpj}?{consulta}",
                          headers={"Authorization": f"Bearer {_token()}", "Accept": "application/json"})
    status, texto = _chamar(req)
    if not 200 <= status < 300:
        print(f"FALHOU · HTTP {status} · {texto[:300]}")
        return 1
    try:
        print(json.dumps(json.loads(texto), ensure_ascii=False, indent=1))
    except json.JSONDecodeError:
        print(texto)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="API do Acessórias: envio ao e-Contínuo e consulta de entregas.")
    sub = ap.add_subparsers(dest="comando", required=True)
    e = sub.add_parser("enviar", help="envia PDFs ao robô e-Contínuo (é o envio ao cliente)")
    e.add_argument("arquivos", nargs="+")
    e.add_argument("--confirmo-envio", action="store_true", help="sem esta opção, só simula")
    c = sub.add_parser("entregas", help="lista as entregas de uma empresa no período")
    c.add_argument("cnpj")
    c.add_argument("--de", required=True)
    c.add_argument("--ate", required=True)
    args = ap.parse_args(argv)
    if args.comando == "enviar":
        return enviar(args.arquivos, args.confirmo_envio)
    return entregas(args.cnpj, args.de, args.ate)


if __name__ == "__main__":
    sys.exit(main())
