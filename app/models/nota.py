from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

if TYPE_CHECKING:
    from .usuario import Usuario


class Nota(db.Model):
    __tablename__ = "notas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    titulo: Mapped[str] = mapped_column(String(150))
    conteudo: Mapped[str] = mapped_column(Text)
    fixada: Mapped[bool] = mapped_column(default=False, server_default="0")
    criada_em: Mapped[datetime] = mapped_column(default=datetime.now)
    atualizada_em: Mapped[datetime] = mapped_column(default=datetime.now)

    usuario: Mapped[Usuario] = relationship(back_populates="notas")
