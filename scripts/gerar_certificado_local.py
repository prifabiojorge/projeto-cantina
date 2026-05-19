#!/usr/bin/env python3
"""Gera certificado local persistente para contingência fora da Vercel."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
CERT_DIR = ROOT / "instance" / "certs"
CERT = CERT_DIR / "cert.pem"
KEY = CERT_DIR / "key.pem"


def main() -> int:
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    if CERT.exists() and KEY.exists():
        print(f"Certificado já existe em {CERT_DIR}")
        return 0

    cmd = [
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:4096",
        "-keyout",
        str(KEY),
        "-out",
        str(CERT),
        "-days",
        "365",
        "-nodes",
        "-subj",
        "/CN=localhost",
    ]
    try:
        subprocess.check_call(cmd)
    except FileNotFoundError:
        print("OpenSSL não encontrado. Instale OpenSSL ou continue usando ssl_context='adhoc'.")
        return 1
    print(f"Certificado gerado em {CERT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
