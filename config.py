import os
import secrets
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BANCO = RAIZ / "database" / "mynotes.db"
ARQUIVO_CHAVE = RAIZ / "instance" / "secret_key"


def carregar_chave_secreta() -> str:
    if chave := os.environ.get("SECRET_KEY"):
        return chave
    if not ARQUIVO_CHAVE.exists():
        ARQUIVO_CHAVE.parent.mkdir(parents=True, exist_ok=True)
        ARQUIVO_CHAVE.write_text(secrets.token_hex(32), encoding="ascii")
    return ARQUIVO_CHAVE.read_text(encoding="ascii").strip()


class Config:
    SECRET_KEY = carregar_chave_secreta()
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BANCO.as_posix()}"
    SESSION_COOKIE_NAME = "mynotes_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 1024 * 1024
