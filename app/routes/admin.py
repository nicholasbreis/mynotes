from flask import Blueprint, abort, flash, g, redirect, render_template, url_for

from app.extensions import db
from app.models import Usuario
from app.sessao import admin_obrigatorio

bp = Blueprint("admin", __name__, url_prefix="/admin/usuarios")


def _outro_usuario(usuario_id: int) -> Usuario:
    usuario = db.get_or_404(Usuario, usuario_id)
    if usuario.id == g.usuario.id:
        abort(403)
    return usuario


@bp.get("")
@admin_obrigatorio
def listar():
    usuarios = db.session.scalars(db.select(Usuario).order_by(Usuario.nome)).all()
    return render_template("admin/usuarios.html", usuarios=usuarios)


@bp.post("/<int:usuario_id>/bloquear")
@admin_obrigatorio
def bloquear(usuario_id: int):
    usuario = _outro_usuario(usuario_id)
    usuario.ativo = not usuario.ativo
    db.session.commit()
    flash("Usuário desbloqueado." if usuario.ativo else "Usuário bloqueado.", "success")
    return redirect(url_for("admin.listar"))


@bp.post("/<int:usuario_id>/excluir")
@admin_obrigatorio
def excluir(usuario_id: int):
    db.session.delete(_outro_usuario(usuario_id))
    db.session.commit()
    flash("Usuário e suas notas foram excluídos.", "success")
    return redirect(url_for("admin.listar"))
