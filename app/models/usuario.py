from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

if TYPE_CHECKING:
    from .nota import Nota

PERFIL_USUARIO = "usuario"
PERFIL_ADMIN = "admin"


class Usuario(db.Model):
    __tablename__ = "usuarios"
    __table_args__ = (CheckConstraint("perfil IN ('usuario', 'admin')", name="ck_usuarios_perfil"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    senha: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(10), default=PERFIL_USUARIO, server_default=PERFIL_USUARIO)
    ativo: Mapped[bool] = mapped_column(default=True, server_default="1")
    criado_em: Mapped[datetime] = mapped_column(default=datetime.now)

    notas: Mapped[list[Nota]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def eh_admin(self) -> bool:
        return self.perfil == PERFIL_ADMIN

    def definir_senha(self, senha: str) -> None:
        self.senha = generate_password_hash(senha)

    def senha_confere(self, senha: str) -> bool:
        return check_password_hash(self.senha, senha)
