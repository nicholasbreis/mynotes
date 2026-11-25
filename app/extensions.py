import sqlite3
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()


@event.listens_for(Engine, "connect")
def configurar_sqlite(conexao: Any, _registro: Any) -> None:
    if not isinstance(conexao, sqlite3.Connection):
        return
    # O SQLite só aplica o ON DELETE CASCADE com este PRAGMA ligado em cada conexão.
    conexao.execute("PRAGMA foreign_keys = ON")
    # O lower() nativo ignora letras acentuadas, o que quebraria a busca em português.
    conexao.create_function("lower", 1, lambda texto: texto.lower() if texto is not None else None)
